"""
MoAI-Flow Memory Module

Cross-session memory system:
- SwarmDB: SQLite wrapper for persistent storage
- SemanticMemory: Long-term knowledge and patterns
- EpisodicMemory: Event and decision history
- ContextHints: Session hints and user preferences
"""

from .swarm_db import SwarmDB
from .context_hints import (
    ContextHints,
    PreferenceCategory,
    ExpertiseLevel,
    WorkflowPreference,
    CommunicationStyle,
    ValidationStrictness,
)

# Future exports (Phase 4)
# from .semantic_memory import SemanticMemory
# from .episodic_memory import EpisodicMemory

__all__ = [
    "SwarmDB",
    "ContextHints",
    "PreferenceCategory",
    "ExpertiseLevel",
    "WorkflowPreference",
    "CommunicationStyle",
    "ValidationStrictness",
    # Future: "SemanticMemory",
    # Future: "EpisodicMemory",
]
