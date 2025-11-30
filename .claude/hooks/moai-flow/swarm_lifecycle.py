"""
Session lifecycle hook for moai-flow swarm coordination.
Manages swarm initialization and cleanup.
"""

import sys
from pathlib import Path

moai_flow_path = Path(__file__).parent.parent.parent.parent / "moai_flow"
if moai_flow_path.exists():
    sys.path.insert(0, str(moai_flow_path.parent))

def execute(context):
    """
    Execute session lifecycle management.

    Args:
        context: Session context with event type (session_start/session_end)

    Returns:
        dict: Lifecycle operation status
    """
    try:
        event = context.get("event", "session_start")

        if event == "session_start":
            from moai_flow.core.swarm_coordinator import SwarmCoordinator

            # Initialize swarm session
            coordinator = SwarmCoordinator()
            session_id = coordinator.initialize_session()

            return {
                "success": True,
                "event": "session_start",
                "session_id": session_id
            }

        elif event == "session_end":
            from moai_flow.memory.swarm_db import SwarmDB

            # Cleanup and persist state
            db = SwarmDB()
            state_file = db.persist_session_state()
            cleanup_stats = db.cleanup()

            return {
                "success": True,
                "event": "session_end",
                "persisted": True,
                "state_file": state_file,
                "cleanup": cleanup_stats
            }

        return {"success": True, "skipped": f"unknown event: {event}"}

    except Exception as e:
        return {"success": False, "error": str(e)}
