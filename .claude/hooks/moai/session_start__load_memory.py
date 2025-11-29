#!/usr/bin/env python3
"""SessionStart Hook: Load Memory and Context Hints

Claude Code Event: SessionStart
Purpose: Load context hints and recent episodic memory at session start for continuity
Execution: Triggered automatically when Claude Code session begins

This hook integrates with SwarmDB to:
- Load user preferences and communication style
- Retrieve recent episodic memory (last 24 hours)
- Load relevant semantic memory patterns
- Inject context hints into session state
- Suggest next actions based on last session

Memory Integration:
- ContextHints: User preferences, workflow patterns, expertise level
- EpisodicMemory: Recent events, commands, agent executions
- SemanticMemory: Long-term knowledge patterns (future)
- SessionState: Last session's unfinished tasks

Architecture:
- Uses SwarmDB for persistent memory storage
- Loads memory in parallel for performance
- Graceful degradation if memory unavailable
- Injects context into session via system message

TDD Approach:
- RED: Test memory loading and context injection
- GREEN: Implement SwarmDB queries and context building
- REFACTOR: Optimize parallel loading and error handling
"""

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup import path for shared modules
HOOKS_DIR = Path(__file__).parent
LIB_DIR = HOOKS_DIR / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

# Import shared modules
try:
    from lib.path_utils import find_project_root
    from lib.timeout import CrossPlatformTimeout, TimeoutError as PlatformTimeoutError
except ImportError:
    # Fallback implementations
    def find_project_root() -> Path:
        return Path.cwd()

    class CrossPlatformTimeout:
        def __init__(self, seconds):
            pass
        def start(self):
            pass
        def cancel(self):
            pass

    class PlatformTimeoutError(Exception):
        pass


# ============================================================================
# SwarmDB Integration
# ============================================================================

def get_swarm_db():
    """Initialize SwarmDB connection

    Returns:
        SwarmDB instance or None if unavailable
    """
    try:
        # Import SwarmDB from moai-flow
        project_root = find_project_root()
        moai_flow_path = project_root / "moai-flow"

        if str(moai_flow_path) not in sys.path:
            sys.path.insert(0, str(moai_flow_path))

        from memory.swarm_db import SwarmDB

        # Initialize with default path
        db_path = project_root / ".moai" / "memory" / "swarm.db"
        return SwarmDB(db_path=db_path)

    except (ImportError, Exception):
        # SwarmDB not available - graceful degradation
        return None


def load_context_hints(db, session_id: str) -> Dict[str, Any]:
    """Load context hints for current session

    Args:
        db: SwarmDB instance
        session_id: Current session identifier

    Returns:
        Dict of context hints (user preferences, patterns)
    """
    if not db:
        return {}

    try:
        # Load user preferences
        preferences = db.get_memory(
            session_id="global",  # Global preferences
            memory_type="context_hint",
            key="user_preferences"
        )

        return preferences or {
            "communication": "concise",
            "workflow": "tdd",
            "expertise": "intermediate"
        }

    except Exception:
        return {}


def load_recent_episodes(db, hours: int = 24) -> List[Dict[str, Any]]:
    """Load recent episodic memory

    Args:
        db: SwarmDB instance
        hours: Number of hours to look back

    Returns:
        List of recent episode events
    """
    if not db:
        return []

    try:
        # Calculate cutoff time
        cutoff = datetime.now() - timedelta(hours=hours)
        cutoff_iso = cutoff.isoformat()

        # Query recent events from SwarmDB
        conn = db._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM agent_events
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT 20
            """,
            (cutoff_iso,)
        )

        events = []
        for row in cursor.fetchall():
            event = dict(row)
            # Parse JSON metadata
            if event.get("metadata"):
                try:
                    event["metadata"] = json.loads(event["metadata"])
                except json.JSONDecodeError:
                    event["metadata"] = {}
            events.append(event)

        return events

    except Exception:
        return []


def load_semantic_knowledge(db) -> List[Dict[str, Any]]:
    """Load relevant semantic memory patterns

    Args:
        db: SwarmDB instance

    Returns:
        List of semantic knowledge entries
    """
    if not db:
        return []

    try:
        # Query semantic memory from session_memory table
        conn = db._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT key, value, timestamp
            FROM session_memory
            WHERE memory_type = 'semantic'
            ORDER BY timestamp DESC
            LIMIT 10
            """
        )

        knowledge = []
        for row in cursor.fetchall():
            try:
                value = json.loads(row["value"])
                knowledge.append({
                    "topic": row["key"],
                    "data": value,
                    "timestamp": row["timestamp"]
                })
            except (json.JSONDecodeError, KeyError):
                continue

        return knowledge

    except Exception:
        return []


def load_last_session_state() -> Dict[str, Any]:
    """Load last session state from file

    Returns:
        Last session state dictionary
    """
    try:
        state_file = find_project_root() / ".moai" / "memory" / "last-session-state.json"

        if not state_file.exists():
            return {}

        state_data = json.loads(state_file.read_text())
        return state_data

    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return {}


def suggest_next_actions(
    last_state: Dict[str, Any],
    recent_episodes: List[Dict[str, Any]]
) -> List[str]:
    """Suggest next actions based on last session and recent activity

    Args:
        last_state: Last session state
        recent_episodes: Recent episodic memory

    Returns:
        List of suggested action strings
    """
    suggestions = []

    # Check for uncommitted changes
    if last_state.get("uncommitted_changes"):
        suggestions.append("Review and commit uncommitted changes")

    # Check for SPECs in progress
    specs_in_progress = last_state.get("specs_in_progress", [])
    if specs_in_progress:
        for spec_id in specs_in_progress:
            suggestions.append(f"Continue {spec_id} implementation")

    # Check for recent incomplete agent tasks
    incomplete_agents = [
        e for e in recent_episodes
        if e.get("event_type") == "spawn" and
        not any(
            c.get("event_type") == "complete" and
            c.get("agent_id") == e.get("agent_id")
            for c in recent_episodes
        )
    ]

    if incomplete_agents:
        suggestions.append("Review incomplete agent tasks from last session")

    # Check for error events
    error_events = [e for e in recent_episodes if e.get("event_type") == "error"]
    if error_events:
        suggestions.append("Investigate errors from previous session")

    # Default suggestion if nothing specific
    if not suggestions:
        suggestions.append("Run /moai:1-plan to start new feature")

    return suggestions


# ============================================================================
# Context Building
# ============================================================================

def build_session_context(
    session_id: str,
    db
) -> Dict[str, Any]:
    """Build complete session context from all memory sources

    Args:
        session_id: Current session identifier
        db: SwarmDB instance

    Returns:
        Complete session context dictionary
    """
    # Use ThreadPoolExecutor for parallel loading
    context: Dict[str, Any] = {
        "session_id": session_id,
        "user_preferences": {},
        "recent_episodes": [],
        "relevant_knowledge": [],
        "suggested_next_actions": [],
        "last_session_state": {}
    }

    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit parallel tasks
            future_prefs = executor.submit(load_context_hints, db, session_id)
            future_episodes = executor.submit(load_recent_episodes, db, 24)
            future_knowledge = executor.submit(load_semantic_knowledge, db)
            future_state = executor.submit(load_last_session_state)

            # Collect results as they complete
            for future in as_completed([future_prefs, future_episodes, future_knowledge, future_state]):
                try:
                    result = future.result(timeout=1.0)

                    if future == future_prefs:
                        context["user_preferences"] = result
                    elif future == future_episodes:
                        context["recent_episodes"] = result
                    elif future == future_knowledge:
                        context["relevant_knowledge"] = result
                    elif future == future_state:
                        context["last_session_state"] = result

                except (TimeoutError, Exception):
                    # Individual task timeout or error - continue with other tasks
                    continue

        # Generate suggestions based on loaded data
        context["suggested_next_actions"] = suggest_next_actions(
            context["last_session_state"],
            context["recent_episodes"]
        )

    except Exception:
        # Graceful degradation - return partial context
        pass

    return context


def format_memory_summary(context: Dict[str, Any]) -> str:
    """Format memory context as user-friendly summary

    Args:
        context: Session context dictionary

    Returns:
        Formatted summary string
    """
    lines = []

    # Show user preferences if available
    prefs = context.get("user_preferences", {})
    if prefs:
        lines.append("💡 Your Preferences:")
        lines.append(f"   Communication: {prefs.get('communication', 'default')}")
        lines.append(f"   Workflow: {prefs.get('workflow', 'default')}")
        lines.append(f"   Expertise: {prefs.get('expertise', 'intermediate')}")
        lines.append("")

    # Show recent activity
    episodes = context.get("recent_episodes", [])
    if episodes:
        lines.append(f"📝 Recent Activity: {len(episodes)} events in last 24h")

        # Count by type
        spawn_count = sum(1 for e in episodes if e.get("event_type") == "spawn")
        complete_count = sum(1 for e in episodes if e.get("event_type") == "complete")
        error_count = sum(1 for e in episodes if e.get("event_type") == "error")

        if spawn_count:
            lines.append(f"   Agents spawned: {spawn_count}")
        if complete_count:
            lines.append(f"   Tasks completed: {complete_count}")
        if error_count:
            lines.append(f"   Errors encountered: {error_count}")
        lines.append("")

    # Show last session state
    last_state = context.get("last_session_state", {})
    if last_state:
        lines.append("📌 Last Session:")

        if last_state.get("current_branch"):
            lines.append(f"   Branch: {last_state['current_branch']}")

        uncommitted = last_state.get("uncommitted_files", 0)
        if uncommitted > 0:
            lines.append(f"   Uncommitted changes: {uncommitted} files")

        specs = last_state.get("specs_in_progress", [])
        if specs:
            lines.append(f"   In Progress: {', '.join(specs)}")

        lines.append("")

    # Show suggested next actions
    suggestions = context.get("suggested_next_actions", [])
    if suggestions:
        lines.append("🎯 Suggested Next Steps:")
        for i, suggestion in enumerate(suggestions[:3], 1):  # Limit to top 3
            lines.append(f"   {i}. {suggestion}")

    return "\n".join(lines) if lines else ""


# ============================================================================
# Main Hook Entry Point
# ============================================================================

def main() -> None:
    """Main entry point for SessionStart memory loading hook

    Loads context hints and episodic memory at session start.
    Gracefully degrades if memory system unavailable.

    Exit Codes:
        0: Success (memory loaded or gracefully degraded)
        1: Critical error (timeout, JSON parse failure)
    """
    # Set 2-second timeout for fast startup
    timeout = CrossPlatformTimeout(2)
    timeout.start()

    try:
        # Read JSON payload from stdin
        input_data = sys.stdin.read() if not sys.stdin.isatty() else "{}"
        payload = json.loads(input_data) if input_data.strip() else {}

        # Generate session ID (use timestamp for uniqueness)
        session_id = datetime.now().strftime("session-%Y%m%d-%H%M%S")

        # Initialize SwarmDB
        db = get_swarm_db()

        # Build session context (with graceful degradation)
        context = build_session_context(session_id, db)

        # Format as user-friendly summary
        memory_summary = format_memory_summary(context)

        # Save context to session state file for use by other hooks
        try:
            session_state_file = find_project_root() / ".moai" / "memory" / "session-context.json"
            session_state_file.parent.mkdir(parents=True, exist_ok=True)

            context_data = {
                "session_id": session_id,
                "loaded_at": datetime.now().isoformat(),
                "context": context
            }

            session_state_file.write_text(json.dumps(context_data, indent=2))
        except (OSError, PermissionError):
            # Failed to save context - continue anyway
            pass

        # Close database connection
        if db:
            try:
                db.close()
            except Exception:
                pass

        # Return result with memory summary
        result = {
            "continue": True,
            "systemMessage": memory_summary if memory_summary else ""
        }

        print(json.dumps(result))
        sys.exit(0)

    except PlatformTimeoutError:
        # Timeout - return minimal valid response
        timeout_response = {
            "continue": True,
            "systemMessage": "⚠️ Memory load timeout - continuing without context"
        }
        print(json.dumps(timeout_response))
        print("SessionStart memory load timeout after 2 seconds", file=sys.stderr)
        sys.exit(1)

    except json.JSONDecodeError as e:
        # JSON parse error
        error_response = {
            "continue": True,
            "hookSpecificOutput": {"error": f"JSON parse error: {e}"}
        }
        print(json.dumps(error_response))
        print(f"SessionStart memory load JSON error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        # Unexpected error - graceful degradation
        error_response = {
            "continue": True,
            "systemMessage": ""  # No memory context, but don't block session
        }
        print(json.dumps(error_response))
        print(f"SessionStart memory load error: {e}", file=sys.stderr)
        sys.exit(0)  # Exit 0 for graceful degradation

    finally:
        # Always cancel timeout
        timeout.cancel()


if __name__ == "__main__":
    main()
