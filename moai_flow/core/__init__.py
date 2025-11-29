"""
MoAI-Flow Core Module

Provides the core coordination infrastructure:
- SwarmCoordinator: Main orchestration engine (✅ Implemented)
- Interfaces: Abstract protocols (IMemoryProvider, ICoordinator, IResourceController)
- AgentRegistry: Agent discovery and registration (Future)
- MessageBus: Inter-agent communication (Future)
"""

# Phase 5 exports
from .swarm_coordinator import SwarmCoordinator, AgentState, TopologyHealth
from .interfaces import IMemoryProvider, ICoordinator, IResourceController, Priority

# Future exports (Phase 6+)
# from .agent_registry import AgentRegistry
# from .message_bus import MessageBus

__all__ = [
    "SwarmCoordinator",
    "AgentState",
    "TopologyHealth",
    "IMemoryProvider",
    "ICoordinator",
    "IResourceController",
    "Priority",
    # Future: "AgentRegistry",
    # Future: "MessageBus",
]
