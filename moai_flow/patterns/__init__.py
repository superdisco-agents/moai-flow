"""
Pattern Management for MoAI-Flow
=================================

Pattern storage, schema validation, swarm coordination, and pattern collection.
"""

# Swarm coordination patterns
from .swarm_patterns import (
    PatternType as SwarmPatternType,
    PatternConfig,
    PatternResult,
    MasterWorkerPattern,
    PipelinePattern,
    BroadcastPattern,
    ReducePattern,
    SwarmPatternFactory
)

# Pattern collection
from .pattern_collector import PatternCollector

# Pattern storage and schema
from .schema import (
    PatternType,
    TaskCompletionData,
    ErrorOccurrenceData,
    AgentUsageData,
    UserCorrectionData,
    PatternContext,
    Pattern,
    PatternSchema
)

from .storage import (
    StorageConfig,
    PatternStorage
)

__all__ = [
    # Swarm Patterns
    "SwarmPatternType",
    "PatternConfig",
    "PatternResult",
    "MasterWorkerPattern",
    "PipelinePattern",
    "BroadcastPattern",
    "ReducePattern",
    "SwarmPatternFactory",

    # Pattern Collection
    "PatternCollector",

    # Pattern Schema
    "PatternType",
    "TaskCompletionData",
    "ErrorOccurrenceData",
    "AgentUsageData",
    "UserCorrectionData",
    "PatternContext",
    "Pattern",
    "PatternSchema",

    # Pattern Storage
    "StorageConfig",
    "PatternStorage"
]
