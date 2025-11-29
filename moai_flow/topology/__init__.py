"""
MoAI-Flow Topology Module

Network topologies for multi-agent coordination:
- Mesh: Full connectivity between all agents (✅ Implemented)
- Hierarchical: Tree structure with Alfred as root (✅ Implemented)
- Star: Hub-and-spoke pattern (✅ Implemented)
- Ring: Sequential chain (✅ Implemented)
- Adaptive: Dynamic topology switching based on workload (✅ Implemented)
"""

# Phase 5 exports - All topologies now implemented
from .hierarchical import HierarchicalTopology, Agent
from .ring import RingTopology, RingAgent, create_ring_from_agents
from .star import StarTopology
from .star import Agent as StarAgent
from .mesh import MeshTopology
from .mesh import Agent as MeshAgent, Message
from .adaptive import AdaptiveTopology, TopologyMode, PerformanceMetrics

__all__ = [
    # Hierarchical
    "HierarchicalTopology",
    "Agent",
    # Ring
    "RingTopology",
    "RingAgent",
    "create_ring_from_agents",
    # Star
    "StarTopology",
    "StarAgent",
    # Mesh
    "MeshTopology",
    "MeshAgent",
    "Message",
    # Adaptive
    "AdaptiveTopology",
    "TopologyMode",
    "PerformanceMetrics",
]
