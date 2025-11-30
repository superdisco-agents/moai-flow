"""
Pre-task hook for moai-flow swarm coordination.
Initializes coordination context before task execution.
"""

import sys
from pathlib import Path

# Add moai_flow to path
moai_flow_path = Path(__file__).parent.parent.parent.parent / "src"
if moai_flow_path.exists():
    sys.path.insert(0, str(moai_flow_path))

def execute(context):
    """
    Execute pre-task coordination setup.

    Args:
        context: Task context with metadata

    Returns:
        dict: Updated context with coordination state
    """
    try:
        from moai_flow.core.swarm_coordinator import SwarmCoordinator
        from moai_flow.memory.swarm_db import SwarmDB

        # Initialize coordination if not already active
        if not context.get("swarm_active"):
            coordinator = SwarmCoordinator()
            db = SwarmDB()

            context["swarm_active"] = True
            context["coordinator"] = coordinator
            context["swarm_db"] = db

        return {"success": True, "context": context}

    except Exception as e:
        return {"success": False, "error": str(e)}
