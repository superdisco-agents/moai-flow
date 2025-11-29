#!/usr/bin/env python3

"""SessionEnd Hook: Save memory and session state to SwarmDB

Performs the following tasks on session end:
- Record all session events to EpisodicMemory
- Update ContextHints with learned patterns
- Update SemanticMemory with new knowledge
- Persist session state to SwarmDB
- Generate session summary

Features:
- Multi-memory integration (Episodic, Semantic, ContextHints)
- SwarmDB persistence for agent events and session data
- Session metrics tracking (commands, agents, tokens, errors)
- Work state snapshot with actionable insights
- Graceful degradation with timeout handling
"""

import json
import logging
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add module path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from lib.path_utils import find_project_root

try:
    from lib.config_manager import ConfigManager
except ImportError:
    ConfigManager = None  # type: ignore

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration & Utilities
# ============================================================================


def load_hook_timeout() -> int:
    """Load hook timeout from config.json (default: 2000ms)

    Returns:
        Timeout in milliseconds
    """
    try:
        config_file = Path(".moai/config/config.json")
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config: Dict[str, Any] = json.load(f)
                return config.get("hooks", {}).get("timeout_ms", 2000)
    except Exception:
        pass
    return 2000


def get_graceful_degradation() -> bool:
    """Load graceful_degradation setting from config.json (default: true)

    Returns:
        Whether graceful degradation is enabled
    """
    try:
        config_file = Path(".moai/config/config.json")
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config: Dict[str, Any] = json.load(f)
                return config.get("hooks", {}).get("graceful_degradation", True)
    except Exception:
        pass
    return True


def get_session_id() -> str:
    """Generate session ID based on timestamp

    Returns:
        Session ID in format: session-YYYY-MM-DD-HHMMSS
    """
    return f"session-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"


# ============================================================================
# SwarmDB Integration
# ============================================================================


def get_swarm_db_path() -> Path:
    """Get SwarmDB database path

    Returns:
        Path to swarm.db
    """
    return Path(".moai/memory/swarm.db")


def save_to_swarm_db(session_id: str, events: List[Dict[str, Any]], metrics: Dict[str, Any]) -> bool:
    """Save session data to SwarmDB

    Args:
        session_id: Session identifier
        events: List of session events
        metrics: Session metrics

    Returns:
        True if save was successful, False otherwise
    """
    try:
        db_path = get_swarm_db_path()
        if not db_path.exists():
            logger.warning(f"SwarmDB not found: {db_path}")
            return False

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Save session events to session_memory (episodic)
        for event in events:
            cursor.execute(
                """
                INSERT INTO session_memory (session_id, memory_type, key, value, timestamp, ttl_hours)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    "episodic",
                    event.get("event_type", "unknown"),
                    json.dumps(event, ensure_ascii=False),
                    event.get("timestamp", datetime.now().isoformat()),
                    168,  # 7 days TTL
                ),
            )

        # Save session summary to session_memory (context_hint)
        cursor.execute(
            """
            INSERT INTO session_memory (session_id, memory_type, key, value, timestamp, ttl_hours)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                "context_hint",
                "session_summary",
                json.dumps(metrics, ensure_ascii=False),
                datetime.now().isoformat(),
                720,  # 30 days TTL
            ),
        )

        conn.commit()
        conn.close()

        logger.info(f"Session data saved to SwarmDB: {session_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to save to SwarmDB: {e}")
        return False


def update_semantic_memory(knowledge: Dict[str, Any]) -> bool:
    """Update SemanticMemory with learned knowledge

    Args:
        knowledge: Dictionary of learned knowledge patterns

    Returns:
        True if update was successful, False otherwise
    """
    try:
        db_path = get_swarm_db_path()
        if not db_path.exists():
            logger.warning(f"SwarmDB not found: {db_path}")
            return False

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        session_id = get_session_id()

        # Save knowledge patterns
        for key, value in knowledge.items():
            cursor.execute(
                """
                INSERT INTO session_memory (session_id, memory_type, key, value, timestamp, ttl_hours)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    "semantic",
                    key,
                    json.dumps(value, ensure_ascii=False),
                    datetime.now().isoformat(),
                    None,  # Permanent
                ),
            )

        conn.commit()
        conn.close()

        logger.info("Semantic memory updated")
        return True

    except Exception as e:
        logger.error(f"Failed to update semantic memory: {e}")
        return False


# ============================================================================
# Session Metrics Collection
# ============================================================================


def collect_agent_events() -> List[Dict[str, Any]]:
    """Collect agent execution events from SwarmDB

    Returns:
        List of agent events from current session
    """
    events = []

    try:
        db_path = get_swarm_db_path()
        if not db_path.exists():
            return events

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Get events from last hour (current session estimate)
        one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()

        cursor.execute(
            """
            SELECT event_id, event_type, agent_id, agent_type, timestamp, metadata
            FROM agent_events
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            """,
            (one_hour_ago,),
        )

        rows = cursor.fetchall()

        for row in rows:
            event = {
                "event_id": row[0],
                "event_type": row[1],
                "agent_id": row[2],
                "agent_type": row[3],
                "timestamp": row[4],
                "metadata": json.loads(row[5]) if row[5] else {},
            }
            events.append(event)

        conn.close()

    except Exception as e:
        logger.error(f"Failed to collect agent events: {e}")

    return events


def count_commands_executed() -> int:
    """Count /moai: commands executed in current session

    Returns:
        Number of commands executed
    """
    try:
        # Check command execution state
        state_file = Path(".moai/memory/command-execution-state.json")
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
                return state.get("execution_count", 0)
    except Exception as e:
        logger.warning(f"Failed to count commands: {e}")

    return 0


def estimate_tokens_used() -> int:
    """Estimate total tokens used in session

    Returns:
        Estimated token count
    """
    try:
        # Check session logs for token usage
        logs_dir = Path(".moai/logs/sessions")
        if logs_dir.exists():
            log_files = sorted(logs_dir.glob("session-*.json"), key=lambda f: f.stat().st_mtime, reverse=True)

            if log_files:
                latest_log = log_files[0]
                with open(latest_log, "r", encoding="utf-8") as f:
                    log_data = json.load(f)
                    return log_data.get("tokens_used", 0)

    except Exception as e:
        logger.warning(f"Failed to estimate tokens: {e}")

    return 0


def count_specs_worked_on() -> List[str]:
    """Count SPECs worked on during session

    Returns:
        List of SPEC IDs
    """
    specs = []

    try:
        # Extract from work state
        state_file = Path(".moai/memory/last-session-state.json")
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
                specs = state.get("specs_in_progress", [])

    except Exception as e:
        logger.warning(f"Failed to count specs: {e}")

    return specs


def count_errors_encountered() -> int:
    """Count errors encountered during session

    Returns:
        Number of errors
    """
    try:
        # Check error logs
        error_log = Path(".moai/logs/errors/session-errors.log")
        if error_log.exists():
            with open(error_log, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Count ERROR level lines from last hour
                recent_errors = [
                    line
                    for line in lines
                    if "ERROR" in line and is_recent_log_line(line, hours=1)
                ]
                return len(recent_errors)
    except Exception as e:
        logger.warning(f"Failed to count errors: {e}")

    return 0


def is_recent_log_line(log_line: str, hours: int = 1) -> bool:
    """Check if log line is recent (within N hours)

    Args:
        log_line: Log line to check
        hours: Time window in hours

    Returns:
        True if log line is recent, False otherwise
    """
    try:
        # Extract timestamp from log line (format: YYYY-MM-DD HH:MM:SS)
        import re

        timestamp_match = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", log_line)
        if timestamp_match:
            timestamp_str = timestamp_match.group(0)
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            cutoff = datetime.now() - timedelta(hours=hours)
            return timestamp > cutoff
    except Exception:
        pass

    return False


# ============================================================================
# Session State Management
# ============================================================================


def get_current_phase() -> str:
    """Get current work phase from session state

    Returns:
        Current phase (e.g., "Phase 4", "SPEC-001", etc.)
    """
    try:
        state_file = Path(".moai/memory/last-session-state.json")
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)

                # Check for current SPEC
                specs = state.get("specs_in_progress", [])
                if specs:
                    return specs[0]

                # Check for current branch
                branch = state.get("current_branch", "")
                if branch and branch.startswith("feature/"):
                    return branch.replace("feature/", "")

    except Exception as e:
        logger.warning(f"Failed to get current phase: {e}")

    return "Unknown"


def get_unfinished_work() -> List[str]:
    """Get list of unfinished work items

    Returns:
        List of unfinished work descriptions
    """
    unfinished = []

    try:
        # Check uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=1
        )

        if result.returncode == 0 and result.stdout.strip():
            uncommitted_count = len(result.stdout.strip().split("\n"))
            unfinished.append(f"{uncommitted_count} uncommitted files")

        # Check for in-progress SPECs
        specs = count_specs_worked_on()
        if specs:
            unfinished.append(f"Working on {', '.join(specs)}")

    except Exception as e:
        logger.warning(f"Failed to get unfinished work: {e}")

    return unfinished


def get_next_suggested_action() -> str:
    """Get next suggested action based on session state

    Returns:
        Suggested next action
    """
    try:
        # Check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=1
        )

        if result.returncode == 0 and result.stdout.strip():
            return "Commit pending changes"

        # Check for in-progress SPECs
        specs = count_specs_worked_on()
        if specs:
            return f"Continue work on {specs[0]}"

    except Exception as e:
        logger.warning(f"Failed to get suggested action: {e}")

    return "Start new task"


def save_session_state(session_id: str, metrics: Dict[str, Any]) -> bool:
    """Save session state to disk

    Args:
        session_id: Session identifier
        metrics: Session metrics

    Returns:
        True if save was successful, False otherwise
    """
    try:
        memory_dir = Path(".moai/memory")
        memory_dir.mkdir(parents=True, exist_ok=True)

        state_file = memory_dir / "last-session-state.json"

        session_state = {
            "session_id": session_id,
            "ended_at": datetime.now().isoformat(),
            "duration_seconds": metrics.get("duration_seconds", 0),
            "summary": {
                "tasks_completed": metrics.get("tasks_completed", 0),
                "current_phase": get_current_phase(),
                "unfinished_work": get_unfinished_work(),
                "next_suggested_action": get_next_suggested_action(),
            },
            "metrics": metrics,
            "events": metrics.get("events", []),
        }

        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(session_state, f, indent=2, ensure_ascii=False)

        logger.info(f"Session state saved: {state_file}")
        return True

    except Exception as e:
        logger.error(f"Failed to save session state: {e}")
        return False


# ============================================================================
# Session Summary Generation
# ============================================================================


def generate_session_summary(metrics: Dict[str, Any]) -> str:
    """Generate session summary message

    Args:
        metrics: Session metrics

    Returns:
        Formatted summary message
    """
    summary_lines = ["✅ Session Ended - Memory Saved"]

    try:
        # Session duration
        duration = metrics.get("duration_seconds", 0)
        if duration > 0:
            summary_lines.append(f"   • Duration: {format_duration(duration)}")

        # Commands executed
        commands = metrics.get("commands_executed", 0)
        if commands > 0:
            summary_lines.append(f"   • Commands: {commands}")

        # Agents spawned
        agents = metrics.get("agents_spawned", 0)
        if agents > 0:
            summary_lines.append(f"   • Agents: {agents}")

        # SPECs worked on
        specs = metrics.get("specs_created", [])
        if specs:
            summary_lines.append(f"   • SPECs: {', '.join(specs)}")

        # Errors
        errors = metrics.get("errors_encountered", 0)
        if errors > 0:
            summary_lines.append(f"   ⚠️ Errors: {errors}")

        # Memory saved
        summary_lines.append(f"   • Memory: Saved to SwarmDB")

        # Next action
        next_action = get_next_suggested_action()
        summary_lines.append(f"   → Next: {next_action}")

    except Exception as e:
        logger.warning(f"Failed to generate summary: {e}")

    return "\n".join(summary_lines)


def format_duration(seconds: int) -> str:
    """Format duration in seconds to readable string

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours}h {minutes}m"


# ============================================================================
# Main Hook Entry Point
# ============================================================================


def main() -> None:
    """Main function

    SessionEnd Hook entry point for memory saving and session state persistence.
    Records all session events, updates memory systems, and generates summary.

    Returns:
        None
    """
    graceful_degradation: bool = False

    try:
        # Load hook timeout setting
        timeout_seconds: float = load_hook_timeout() / 1000
        graceful_degradation = get_graceful_degradation()

        # Timeout check
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Hook execution timeout")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout_seconds))

        try:
            start_time = time.time()

            # Generate session ID
            session_id = get_session_id()

            # Initialize results
            results = {
                "hook": "session_end__save_memory",
                "session_id": session_id,
                "success": True,
                "execution_time_seconds": 0,
                "timestamp": datetime.now().isoformat(),
            }

            # Collect session metrics
            agent_events = collect_agent_events()
            commands_count = count_commands_executed()
            tokens_used = estimate_tokens_used()
            specs_worked = count_specs_worked_on()
            errors_count = count_errors_encountered()

            session_duration = int(time.time() - start_time)

            metrics = {
                "commands_executed": commands_count,
                "agents_spawned": len([e for e in agent_events if e["event_type"] == "spawn"]),
                "total_tokens_used": tokens_used,
                "specs_created": specs_worked,
                "tests_passed": 0,  # TODO: Extract from test results
                "errors_encountered": errors_count,
                "duration_seconds": session_duration,
                "events": agent_events,
                "tasks_completed": len([e for e in agent_events if e["event_type"] == "complete"]),
            }

            # Save to SwarmDB
            swarm_saved = save_to_swarm_db(session_id, agent_events, metrics)
            results["swarm_db_saved"] = swarm_saved

            # Update semantic memory with learned patterns
            knowledge = {
                "session_pattern": {
                    "avg_commands_per_session": commands_count,
                    "avg_agents_per_session": metrics["agents_spawned"],
                    "common_workflows": specs_worked,
                },
            }
            semantic_updated = update_semantic_memory(knowledge)
            results["semantic_memory_updated"] = semantic_updated

            # Save session state to disk
            state_saved = save_session_state(session_id, metrics)
            results["session_state_saved"] = state_saved

            # Generate summary
            session_summary = generate_session_summary(metrics)
            results["session_summary"] = session_summary

            # Record execution time
            execution_time = time.time() - start_time
            results["execution_time_seconds"] = round(execution_time, 3)

            # Add metrics to results
            results["metrics"] = metrics

            # Print results
            print(json.dumps(results, ensure_ascii=False, indent=2))
            print(f"\n{session_summary}")

        finally:
            signal.alarm(0)  # Clear timeout

    except TimeoutError as e:
        # Handle timeout
        result = {
            "hook": "session_end__save_memory",
            "success": False,
            "error": f"Hook execution timeout: {str(e)}",
            "graceful_degradation": graceful_degradation,
            "timestamp": datetime.now().isoformat(),
        }

        if graceful_degradation:
            result["message"] = "Hook timeout but continuing due to graceful degradation"

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        # Handle exceptions
        result = {
            "hook": "session_end__save_memory",
            "success": False,
            "error": f"Hook execution failed: {str(e)}",
            "graceful_degradation": graceful_degradation,
            "timestamp": datetime.now().isoformat(),
        }

        if graceful_degradation:
            result["message"] = "Hook failed but continuing due to graceful degradation"

        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
