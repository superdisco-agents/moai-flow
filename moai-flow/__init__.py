"""
MoAI-Flow: Native Multi-Agent Swarm Coordination for MoAI-ADK

This module provides swarm coordination, cross-session memory,
network topologies, and resource control for multi-agent orchestration.

Example:
    >>> from moai_flow import SwarmCoordinator
    >>> swarm = SwarmCoordinator(topology="hierarchical")

Modules:
    - core: SwarmCoordinator, interfaces, message bus
    - topology: mesh, hierarchical, star, ring, adaptive
    - memory: swarm_db, semantic, episodic, context_hints
    - coordination: consensus, conflict resolution, heartbeat
    - resource: token budget, agent quotas, priority queue
    - hooks: pre_task, post_task, agent_lifecycle
"""

__version__ = "0.1.0"
__author__ = "MoAI-ADK Team"

# Future exports (Phase 3+)
# from .core.swarm import SwarmCoordinator
# from .core.interfaces import IMemoryProvider, ICoordinator, IResourceController
# from .topology import HierarchicalTopology, MeshTopology, StarTopology
# from .memory import ContextHints, SemanticMemory, EpisodicMemory

__all__ = [
    "__version__",
    # Future: "SwarmCoordinator",
    # Future: "IMemoryProvider", "ICoordinator", "IResourceController",
    # Future: "HierarchicalTopology", "MeshTopology", "StarTopology",
    # Future: "ContextHints", "SemanticMemory", "EpisodicMemory",
]
