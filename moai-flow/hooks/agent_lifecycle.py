#!/usr/bin/env python3
"""
AgentLifecycle Hooks - Agent spawn/complete event tracking

Integrates with .claude/hooks/moai/ infrastructure to track agent lifecycle events.
Events are stored in SwarmDB and logged to .moai/logs/agent-transcripts/.

Architecture:
- Hook into HookStateManager singleton pattern from .claude/hooks/moai/lib/state_tracking.py
- Store events in SwarmDB (future integration with moai-flow/memory/swarm_db.py)
- Log to .moai/logs/agent-transcripts/ with rotation
- Thread-safe event handling with proper error recovery

Event Schema:
{
    "event_type": "spawn" | "complete" | "error",
    "agent_id": str,
    "agent_type": str,
    "timestamp": ISO8601,
    "metadata": {...}
}
"""

import json
import logging
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import HookStateManager for state persistence integration
try:
    import sys
    from pathlib import Path as PathLib

    # Add .claude/hooks/moai to path for importing state_tracking
    claude_hooks_path = PathLib(__file__).resolve().parents[3] / ".claude" / "hooks" / "moai"
    if str(claude_hooks_path) not in sys.path:
        sys.path.insert(0, str(claude_hooks_path))

    from lib.state_tracking import HookStateManager, get_state_manager
    STATE_TRACKING_AVAILABLE = True
except ImportError:
    STATE_TRACKING_AVAILABLE = False
    HookStateManager = None
    get_state_manager = None


# ============================================================================
# Event Schema Definitions
# ============================================================================

@dataclass
class AgentLifecycleEvent:
    """Base schema for agent lifecycle events"""
    event_type: str  # "spawn" | "complete" | "error"
    agent_id: str
    agent_type: str
    timestamp: str  # ISO8601 format
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class AgentSpawnEvent(AgentLifecycleEvent):
    """Event emitted when agent spawns via Task()"""
    prompt: Optional[str] = None
    model: Optional[str] = None
    parent_agent_id: Optional[str] = None
    priority: Optional[int] = None

    def __post_init__(self):
        self.event_type = "spawn"


@dataclass
class AgentCompleteEvent(AgentLifecycleEvent):
    """Event emitted when agent completes task"""
    result: Any = None
    duration_ms: int = 0
    success: bool = True

    def __post_init__(self):
        self.event_type = "complete"


@dataclass
class AgentErrorEvent(AgentLifecycleEvent):
    """Event emitted when agent encounters error"""
    error_type: str = ""
    error_message: str = ""
    traceback: Optional[str] = None

    def __post_init__(self):
        self.event_type = "error"


# ============================================================================
# Agent Registry - In-Memory State
# ============================================================================

class AgentRegistry:
    """
    Thread-safe in-memory registry of active agents.
    Tracks agent state, spawn time, and heartbeat.
    """

    def __init__(self):
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)

    def register_spawn(self, agent_id: str, agent_type: str, metadata: Dict[str, Any]) -> None:
        """Register agent spawn"""
        with self._lock:
            self._agents[agent_id] = {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "status": "spawned",
                "spawn_time": time.time(),
                "last_heartbeat": time.time(),
                "metadata": metadata.copy()
            }
            self.logger.debug(f"Registered spawn: {agent_id} ({agent_type})")

    def update_complete(self, agent_id: str, result: Any, duration_ms: int) -> None:
        """Update agent status to complete"""
        with self._lock:
            if agent_id in self._agents:
                self._agents[agent_id]["status"] = "complete"
                self._agents[agent_id]["complete_time"] = time.time()
                self._agents[agent_id]["duration_ms"] = duration_ms
                self._agents[agent_id]["result"] = result
                self.logger.debug(f"Updated complete: {agent_id} ({duration_ms}ms)")
            else:
                self.logger.warning(f"Agent not found in registry: {agent_id}")

    def update_error(self, agent_id: str, error: Exception) -> None:
        """Update agent status to error"""
        with self._lock:
            if agent_id in self._agents:
                self._agents[agent_id]["status"] = "error"
                self._agents[agent_id]["error_time"] = time.time()
                self._agents[agent_id]["error"] = {
                    "type": type(error).__name__,
                    "message": str(error)
                }
                self.logger.debug(f"Updated error: {agent_id} ({type(error).__name__})")
            else:
                self.logger.warning(f"Agent not found in registry: {agent_id}")

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent information"""
        with self._lock:
            return self._agents.get(agent_id, {}).copy() if agent_id in self._agents else None

    def get_active_agents(self) -> List[Dict[str, Any]]:
        """Get list of active (spawned but not complete/error) agents"""
        with self._lock:
            return [
                agent.copy() for agent in self._agents.values()
                if agent["status"] == "spawned"
            ]

    def cleanup_old_agents(self, max_age_hours: int = 24) -> int:
        """Remove agents older than max_age_hours"""
        with self._lock:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            removed_count = 0

            for agent_id in list(self._agents.keys()):
                agent = self._agents[agent_id]
                spawn_time = agent.get("spawn_time", 0)

                if current_time - spawn_time > max_age_seconds:
                    del self._agents[agent_id]
                    removed_count += 1

            if removed_count > 0:
                self.logger.info(f"Cleaned up {removed_count} old agents")

            return removed_count


# ============================================================================
# Event Logger - File-based Persistent Storage
# ============================================================================

class AgentLifecycleLogger:
    """
    File-based logger for agent lifecycle events.
    Logs to .moai/logs/agent-transcripts/ with rotation.
    """

    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize logger

        Args:
            log_dir: Log directory path (defaults to .moai/logs/agent-transcripts/)
        """
        self.log_dir = log_dir or Path.cwd() / ".moai" / "logs" / "agent-transcripts"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup Python logging with rotation
        self.logger = self._setup_logger()

        # Lock for thread safety
        self._lock = threading.RLock()

    def _setup_logger(self) -> logging.Logger:
        """Setup Python logger with file rotation"""
        logger = logging.getLogger("agent_lifecycle")
        logger.setLevel(logging.INFO)

        # Prevent duplicate handlers
        if logger.handlers:
            return logger

        # File handler with rotation (10MB per file, keep 5 backups)
        from logging.handlers import RotatingFileHandler

        log_file = self.log_dir / "agent_lifecycle.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )

        # Format: timestamp | level | message
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def log_event(self, event: AgentLifecycleEvent) -> None:
        """Log lifecycle event"""
        with self._lock:
            try:
                # Log to Python logger
                log_message = f"{event.event_type.upper()} | {event.agent_id} | {event.agent_type}"
                if event.event_type == "spawn":
                    self.logger.info(f"{log_message} | metadata={event.metadata}")
                elif event.event_type == "complete":
                    duration = event.metadata.get("duration_ms", 0)
                    self.logger.info(f"{log_message} | duration={duration}ms")
                elif event.event_type == "error":
                    error_msg = event.metadata.get("error_message", "Unknown error")
                    self.logger.error(f"{log_message} | error={error_msg}")

                # Also write JSON event to daily log file
                self._write_json_event(event)

            except Exception as e:
                # Fail gracefully - log error but don't raise
                self.logger.error(f"Failed to log event: {e}")

    def _write_json_event(self, event: AgentLifecycleEvent) -> None:
        """Write JSON event to daily log file"""
        try:
            # Daily log file: agent_lifecycle_YYYY-MM-DD.jsonl
            date_str = datetime.now().strftime("%Y-%m-%d")
            json_log_file = self.log_dir / f"agent_lifecycle_{date_str}.jsonl"

            # Append event as JSON line
            with open(json_log_file, "a", encoding="utf-8") as f:
                f.write(event.to_json() + "\n")

        except Exception as e:
            self.logger.error(f"Failed to write JSON event: {e}")


# ============================================================================
# SwarmDB Integration (Future)
# ============================================================================

class SwarmDBIntegration:
    """
    Future integration with moai-flow/memory/swarm_db.py
    Currently stubbed for future implementation.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path.cwd() / ".moai" / "memory" / "swarm.db"
        self.logger = logging.getLogger(__name__)
        self.enabled = False  # Enable when SwarmDB is implemented

    def store_event(self, event: AgentLifecycleEvent) -> bool:
        """Store event in SwarmDB (future implementation)"""
        if not self.enabled:
            return False

        try:
            # TODO: Integrate with SwarmDB when implemented
            # from moai_flow.memory.swarm_db import SwarmDB
            # db = SwarmDB(self.db_path)
            # db.insert_event(event.to_dict())
            self.logger.debug(f"SwarmDB integration not yet implemented: {event.agent_id}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to store event in SwarmDB: {e}")
            return False


# ============================================================================
# AgentLifecycle Hook Functions (Public API)
# ============================================================================

# Global instances (thread-safe singletons)
_agent_registry: Optional[AgentRegistry] = None
_lifecycle_logger: Optional[AgentLifecycleLogger] = None
_swarm_db: Optional[SwarmDBIntegration] = None
_state_manager: Optional[Any] = None  # HookStateManager instance
_init_lock = threading.RLock()


def _ensure_initialized(cwd: Optional[str] = None) -> None:
    """Ensure global instances are initialized"""
    global _agent_registry, _lifecycle_logger, _swarm_db, _state_manager

    with _init_lock:
        if _agent_registry is None:
            _agent_registry = AgentRegistry()

        if _lifecycle_logger is None:
            log_dir = Path(cwd or ".") / ".moai" / "logs" / "agent-transcripts"
            _lifecycle_logger = AgentLifecycleLogger(log_dir)

        if _swarm_db is None:
            _swarm_db = SwarmDBIntegration()

        # Initialize HookStateManager if available
        if _state_manager is None and STATE_TRACKING_AVAILABLE and get_state_manager:
            try:
                _state_manager = get_state_manager(cwd or ".")
            except Exception as e:
                logging.getLogger(__name__).warning(
                    f"Failed to initialize HookStateManager: {e}"
                )


def on_agent_spawn(
    agent_id: str,
    agent_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Called when a new agent is spawned via Task().

    Args:
        agent_id: Unique agent identifier (UUID)
        agent_type: Agent subagent_type (e.g., "expert-backend", "manager-tdd")
        metadata: Additional spawn metadata:
            - prompt: Task prompt string
            - model: Model name (e.g., "claude-sonnet-4")
            - parent_agent_id: Parent agent ID for nested spawns
            - priority: Task priority level
            - [custom fields...]

    Example:
        >>> on_agent_spawn(
        ...     agent_id="a1b2c3d4",
        ...     agent_type="expert-backend",
        ...     metadata={
        ...         "prompt": "Design REST API",
        ...         "model": "claude-sonnet-4",
        ...         "parent_agent_id": "parent123"
        ...     }
        ... )
    """
    _ensure_initialized()

    metadata = metadata or {}
    timestamp = datetime.now().isoformat()

    # Create spawn event
    event = AgentSpawnEvent(
        event_type="spawn",
        agent_id=agent_id,
        agent_type=agent_type,
        timestamp=timestamp,
        metadata=metadata,
        prompt=metadata.get("prompt"),
        model=metadata.get("model"),
        parent_agent_id=metadata.get("parent_agent_id"),
        priority=metadata.get("priority")
    )

    # Update registry
    _agent_registry.register_spawn(agent_id, agent_type, metadata)

    # Log event
    _lifecycle_logger.log_event(event)

    # Store in SwarmDB (future)
    _swarm_db.store_event(event)

    # Track in HookStateManager if available
    if _state_manager:
        try:
            _state_manager.track_hook_execution(
                hook_name="AgentLifecycle.spawn",
                phase=agent_type
            )
        except Exception as e:
            logging.getLogger(__name__).warning(
                f"Failed to track spawn in HookStateManager: {e}"
            )


def on_agent_complete(
    agent_id: str,
    result: Any = None,
    duration_ms: int = 0
) -> None:
    """
    Called when an agent completes its task.

    Args:
        agent_id: Agent identifier
        result: Agent result/report (can be dict, str, or any serializable type)
        duration_ms: Execution time in milliseconds

    Example:
        >>> on_agent_complete(
        ...     agent_id="a1b2c3d4",
        ...     result={"status": "success", "files_created": 3},
        ...     duration_ms=15230
        ... )
    """
    _ensure_initialized()

    # Get agent info from registry
    agent_info = _agent_registry.get_agent(agent_id)
    if not agent_info:
        logging.getLogger(__name__).warning(
            f"Agent not found in registry: {agent_id}"
        )
        agent_type = "unknown"
    else:
        agent_type = agent_info.get("agent_type", "unknown")

    timestamp = datetime.now().isoformat()

    # Create complete event
    event = AgentCompleteEvent(
        event_type="complete",
        agent_id=agent_id,
        agent_type=agent_type,
        timestamp=timestamp,
        metadata={
            "duration_ms": duration_ms,
            "result_type": type(result).__name__ if result is not None else "None",
            "result_summary": str(result)[:200] if result is not None else None
        },
        result=result,
        duration_ms=duration_ms,
        success=True
    )

    # Update registry
    _agent_registry.update_complete(agent_id, result, duration_ms)

    # Log event
    _lifecycle_logger.log_event(event)

    # Store in SwarmDB (future)
    _swarm_db.store_event(event)

    # Track in HookStateManager if available
    if _state_manager:
        try:
            _state_manager.track_hook_execution(
                hook_name="AgentLifecycle.complete",
                phase=agent_type
            )
        except Exception as e:
            logging.getLogger(__name__).warning(
                f"Failed to track complete in HookStateManager: {e}"
            )


def on_agent_error(
    agent_id: str,
    error: Exception
) -> None:
    """
    Called when an agent encounters an error.

    Args:
        agent_id: Agent identifier
        error: Exception that occurred

    Example:
        >>> try:
        ...     # Agent task execution
        ...     pass
        ... except Exception as e:
        ...     on_agent_error(agent_id="a1b2c3d4", error=e)
    """
    _ensure_initialized()

    # Get agent info from registry
    agent_info = _agent_registry.get_agent(agent_id)
    if not agent_info:
        logging.getLogger(__name__).warning(
            f"Agent not found in registry: {agent_id}"
        )
        agent_type = "unknown"
    else:
        agent_type = agent_info.get("agent_type", "unknown")

    timestamp = datetime.now().isoformat()

    # Extract traceback if available
    import traceback as tb
    traceback_str = "".join(tb.format_exception(type(error), error, error.__traceback__))

    # Create error event
    event = AgentErrorEvent(
        event_type="error",
        agent_id=agent_id,
        agent_type=agent_type,
        timestamp=timestamp,
        metadata={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback_preview": traceback_str[:500]
        },
        error_type=type(error).__name__,
        error_message=str(error),
        traceback=traceback_str
    )

    # Update registry
    _agent_registry.update_error(agent_id, error)

    # Log event
    _lifecycle_logger.log_event(event)

    # Store in SwarmDB (future)
    _swarm_db.store_event(event)

    # Track in HookStateManager if available
    if _state_manager:
        try:
            _state_manager.track_hook_execution(
                hook_name="AgentLifecycle.error",
                phase=agent_type
            )
        except Exception as e:
            logging.getLogger(__name__).warning(
                f"Failed to track error in HookStateManager: {e}"
            )


# ============================================================================
# Utility Functions
# ============================================================================

def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry instance"""
    _ensure_initialized()
    return _agent_registry


def get_active_agents() -> List[Dict[str, Any]]:
    """Get list of currently active agents"""
    _ensure_initialized()
    return _agent_registry.get_active_agents()


def cleanup_old_agents(max_age_hours: int = 24) -> int:
    """Cleanup agents older than max_age_hours"""
    _ensure_initialized()
    return _agent_registry.cleanup_old_agents(max_age_hours)


def generate_agent_id() -> str:
    """Generate unique agent ID (UUID4)"""
    return str(uuid.uuid4())


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example 1: Basic agent lifecycle
    print("=== Example 1: Basic Agent Lifecycle ===")

    agent_id = generate_agent_id()
    print(f"Generated agent ID: {agent_id}")

    # Spawn
    on_agent_spawn(
        agent_id=agent_id,
        agent_type="expert-backend",
        metadata={
            "prompt": "Design REST API for user authentication",
            "model": "claude-sonnet-4",
            "parent_agent_id": None,
            "priority": 1
        }
    )
    print(f"✓ Agent spawned: {agent_id}")

    # Simulate work
    import time
    start_time = time.time()
    time.sleep(0.1)  # Simulate 100ms of work
    duration_ms = int((time.time() - start_time) * 1000)

    # Complete
    on_agent_complete(
        agent_id=agent_id,
        result={"status": "success", "endpoints_designed": 5},
        duration_ms=duration_ms
    )
    print(f"✓ Agent completed: {agent_id} ({duration_ms}ms)")

    # Example 2: Error handling
    print("\n=== Example 2: Error Handling ===")

    error_agent_id = generate_agent_id()
    on_agent_spawn(
        agent_id=error_agent_id,
        agent_type="expert-frontend",
        metadata={"prompt": "Build React component"}
    )
    print(f"✓ Agent spawned: {error_agent_id}")

    try:
        raise ValueError("Invalid component props")
    except Exception as e:
        on_agent_error(agent_id=error_agent_id, error=e)
        print(f"✓ Error tracked: {error_agent_id}")

    # Example 3: Query active agents
    print("\n=== Example 3: Active Agents ===")
    active_agents = get_active_agents()
    print(f"Active agents: {len(active_agents)}")
    for agent in active_agents:
        print(f"  - {agent['agent_id']}: {agent['agent_type']} ({agent['status']})")

    print("\n✅ AgentLifecycle hooks demonstration complete")
    print(f"📝 Logs written to: {Path.cwd() / '.moai' / 'logs' / 'agent-transcripts'}")
