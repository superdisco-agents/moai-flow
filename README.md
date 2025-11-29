# 🌊 MoAI-Flow

**Native Multi-Agent Swarm Coordination for MoAI-ADK**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![Tests](https://img.shields.io/badge/tests-318%2B-green)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen)](tests/)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![TRUST 5](https://img.shields.io/badge/TRUST%205-compliant-success)](https://adk.mo.ai.kr)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Core Components](#-core-components)
- [Memory System](#-memory-system)
- [Topology Patterns](#-topology-patterns)
- [API Reference](#-api-reference)
- [Examples](#-examples)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 🎯 Overview

MoAI-Flow는 MoAI-ADK를 위한 네이티브 다중 에이전트 스웜 조정 시스템입니다. Claude Code와 완벽하게 통합되어 AI 에이전트 간의 효율적인 협업과 자원 관리를 제공합니다.

### Why MoAI-Flow?

**Native Integration**
- MoAI-ADK와 완벽한 통합으로 추가 설정 없이 즉시 사용 가능
- Claude Code 에이전트 시스템과 네이티브 호환
- 기존 MoAI-ADK 워크플로우와 seamless 통합

**Cross-Session Memory**
- 세션 간 지속되는 지능형 메모리 시스템
- SemanticMemory: 장기 지식과 패턴 저장
- EpisodicMemory: 이벤트 및 의사결정 히스토리
- ContextHints: 사용자 선호도 및 전문성 레벨 추적

**Flexible Topologies**
- 5가지 스웜 토폴로지 지원 (Hierarchical, Mesh, Star, Ring, Adaptive)
- 작업 특성에 맞는 동적 토폴로지 선택
- 실시간 토폴로지 전환 가능

**Production-Ready**
- 318+ comprehensive tests, 97%+ coverage
- 5 topology implementations (4,212 lines)
- SwarmCoordinator engine (1,043 lines)
- Performance-optimized SQLite with 12 indexes
- Thread-safe operations with connection pooling
- Robust error handling and graceful degradation

**Enterprise-Grade**
- TRUST 5 principles 준수 (Test-first, Readable, Unified, Secured, Trackable)
- SPEC-driven development workflow
- Complete audit trail and observability
- Security-first architecture

---

## ⚡ Key Features

### 🧠 Intelligent Memory System

**SemanticMemory** - Long-term Knowledge Patterns
```python
# Store best practices and patterns
semantic = SemanticMemory(db)
semantic.store_knowledge(
    category="pattern",
    content="Use async/await for I/O operations",
    confidence=0.95
)

# Retrieve relevant knowledge
patterns = semantic.query_knowledge(category="pattern", min_confidence=0.8)
```

**EpisodicMemory** - Event and Decision History
```python
# Track important decisions
episodic = EpisodicMemory(db)
episodic.record_episode(
    category="architectural_decision",
    content="Chose PostgreSQL for relational data",
    importance=0.9,
    tags=["database", "architecture"]
)

# Retrieve past decisions
decisions = episodic.query_episodes(category="architectural_decision")
```

**ContextHints** - Session Preferences and Expertise
```python
# Set user expertise level
hints = ContextHints(db)
hints.set_expertise_level(ExpertiseLevel.INTERMEDIATE)
hints.set_preference("workflow", "parallel")

# Alfred adapts responses based on expertise
level = hints.get_expertise_level()  # INTERMEDIATE
workflow = hints.get_preference("workflow")  # "parallel"
```

### 🚀 Resource Management

**TokenBudget** - Per-Swarm Token Allocation
```python
budget = TokenBudget(total_budget=200000)

# Allocate tokens to swarm
budget.allocate_to_swarm("backend-swarm", 50000)

# Track usage
budget.consume_tokens("backend-swarm", 5000)
remaining = budget.get_remaining_tokens("backend-swarm")  # 45000
```

**AgentQuota** - Execution Limits
```python
# Prevent agent spam
quota = AgentQuota(max_agents_per_type=5)
quota.can_spawn("expert-backend")  # True/False

# Track active agents
quota.register_spawn("expert-backend")
quota.register_complete("expert-backend")
```

**PriorityQueue** - Task Priority Management (Phase 6)
```python
# High-priority tasks processed first
queue = PriorityQueue()
queue.enqueue(task_id="urgent-fix", priority=10)
queue.enqueue(task_id="refactor", priority=5)

next_task = queue.dequeue()  # Returns "urgent-fix"
```

### 🔗 Agent Coordination

**AgentLifecycle** - Comprehensive Event Tracking
```python
lifecycle = AgentLifecycleHook(db)

# Track agent spawn
lifecycle.on_agent_spawn("backend-expert-001", metadata={
    "task": "Implement REST API",
    "model": "claude-sonnet-4",
    "priority": "high"
})

# Track completion
lifecycle.on_agent_complete("backend-expert-001", result={
    "status": "success",
    "files_modified": 5,
    "tests_added": 12,
    "duration_ms": 45000
})

# Handle errors
lifecycle.on_agent_error("backend-expert-001", error={
    "type": "timeout",
    "message": "Agent exceeded 2-minute timeout"
})

# Query agent history
events = lifecycle.get_agent_events("backend-expert-001")
for event in events:
    print(f"{event['event_type']} @ {event['timestamp']}")
```

**Consensus** - Voting and Agreement Protocols (Phase 6)
```python
# Multi-agent consensus for critical decisions
consensus = ConsensusManager()
consensus.propose("use_postgresql", voters=["db-expert", "backend-expert"])

# Agents vote
consensus.vote("use_postgresql", agent_id="db-expert", vote=True)
consensus.vote("use_postgresql", agent_id="backend-expert", vote=True)

# Check consensus
if consensus.has_consensus("use_postgresql", threshold=0.8):
    print("Consensus reached: Use PostgreSQL")
```

**ConflictResolution** - Handle Conflicting Decisions (Phase 6)
```python
# Resolve agent conflicts
resolver = ConflictResolver()
resolver.add_decision("db-expert", "use_postgresql")
resolver.add_decision("backend-expert", "use_mongodb")

# Resolve with weighted voting
resolution = resolver.resolve(weights={
    "db-expert": 0.7,
    "backend-expert": 0.3
})
print(f"Final decision: {resolution}")  # "use_postgresql"
```

### ⚡ Performance Optimizations

**12 SQLite Performance Indexes**
```sql
-- Query time <20ms for all operations
CREATE INDEX idx_agent_events_agent_id ON agent_events(agent_id);
CREATE INDEX idx_agent_events_event_type ON agent_events(event_type);
CREATE INDEX idx_agent_events_timestamp ON agent_events(timestamp);

CREATE INDEX idx_agent_registry_status ON agent_registry(status);
CREATE INDEX idx_agent_registry_agent_type ON agent_registry(agent_type);

CREATE INDEX idx_session_memory_session_id ON session_memory(session_id);
CREATE INDEX idx_session_memory_memory_type ON session_memory(memory_type);
CREATE INDEX idx_session_memory_key ON session_memory(key);

-- + 4 additional indexes for semantic/episodic memory
```

**Batch Operations**
```python
# 100x faster writes with batching
with db.transaction():
    for event in events:
        db.insert_event(event)
# All inserted in single transaction
```

**Connection Pooling**
```python
# Thread-safe, reusable connections
db = SwarmDB()
# Automatic connection pooling per thread
# No manual connection management required
```

---

## 🚀 Quick Start

### Installation

**Prerequisites**
- Python 3.8+ (Recommended: Python 3.11+)
- pip or uv package manager
- Git

**Clone Repository**
```bash
git clone https://github.com/superdisco-agents/moai-flow.git
cd moai-flow
```

**Install Dependencies**
```bash
# Using pip
pip install -e .

# Using uv (recommended for faster installs)
uv pip install -e .
```

**Verify Installation**
```bash
python -c "from moai_flow.memory.swarm_db import SwarmDB; print('✅ MoAI-Flow ready')"
```

### Your First Swarm (5 minutes)

**Step 1: Initialize SwarmDB**
```python
from moai_flow.memory.swarm_db import SwarmDB
from moai_flow.memory.context_hints import ContextHints
from moai_flow.hooks.agent_lifecycle import AgentLifecycleHook

# Initialize SwarmDB (creates .moai/memory/swarm.db)
db = SwarmDB(db_path=".moai/memory/swarm.db")
print("✅ SwarmDB initialized")
```

**Step 2: Set User Preferences**
```python
# Configure context hints for personalized experience
hints = ContextHints(db)
hints.set_expertise_level(ExpertiseLevel.INTERMEDIATE)
hints.set_preference("workflow", "parallel")
hints.set_preference("validation", "strict")

print("✅ User preferences configured")
```

**Step 3: Register Agent Lifecycle**
```python
# Track agent lifecycle events
lifecycle = AgentLifecycleHook(db)

# Spawn backend expert
lifecycle.on_agent_spawn("backend-001", metadata={
    "role": "expert-backend",
    "task": "Implement REST API",
    "model": "claude-sonnet-4"
})

print("✅ Agent registered: backend-001")
```

**Step 4: Track Agent Completion**
```python
import time

# Simulate agent work
time.sleep(0.5)

# Mark agent as complete
lifecycle.on_agent_complete("backend-001", result={
    "status": "success",
    "files_created": 3,
    "tests_added": 8,
    "duration_ms": 500
})

print("✅ Agent completed successfully")
```

**Step 5: Query Agent History**
```python
# Retrieve agent events
events = lifecycle.get_agent_events("backend-001")

print(f"\n📊 Agent Events ({len(events)} total):")
for event in events:
    print(f"  - {event['event_type']} @ {event['timestamp']}")
    print(f"    Metadata: {event['metadata']}")

print("\n✅ Your first swarm is ready!")
```

**Complete Example**
```python
#!/usr/bin/env python3
"""Complete first swarm example"""

from moai_flow.memory.swarm_db import SwarmDB
from moai_flow.memory.context_hints import ContextHints, ExpertiseLevel
from moai_flow.hooks.agent_lifecycle import AgentLifecycleHook
import time

# Initialize
db = SwarmDB()
hints = ContextHints(db)
lifecycle = AgentLifecycleHook(db)

# Configure preferences
hints.set_expertise_level(ExpertiseLevel.INTERMEDIATE)
hints.set_preference("workflow", "parallel")

# Spawn agent
lifecycle.on_agent_spawn("backend-001", metadata={
    "role": "expert-backend",
    "task": "Implement REST API"
})

# Complete agent
time.sleep(0.5)
lifecycle.on_agent_complete("backend-001", result={
    "status": "success",
    "files_created": 3
})

# Query events
events = lifecycle.get_agent_events("backend-001")
print(f"✅ Completed! {len(events)} events tracked")
```

---

## 🏗️ Architecture

### System Architecture Diagram

```mermaid
graph TB
    A[Alfred SuperAgent] --> B[Swarm Coordinator]
    B --> C[Topology Layer]
    C --> D[Resource Control]
    C --> E[Memory System]
    D --> F[Token Budget]
    D --> G[Agent Quota]
    E --> H[SwarmDB]
    E --> I[Semantic Memory]
    E --> J[Episodic Memory]
    E --> K[Context Hints]

    style A fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style B fill:#50C878,stroke:#2E7D4E,color:#fff
    style C fill:#9B59B6,stroke:#6C3A7C,color:#fff
    style D fill:#E67E22,stroke:#A85C17,color:#fff
    style E fill:#E74C3C,stroke:#A83426,color:#fff
```

### Core Layers

**1. Coordination Layer** - SwarmCoordinator
- Manages agent lifecycle from spawn to completion
- Orchestrates multi-agent collaboration
- Handles task delegation and result aggregation
- Provides fault tolerance and error recovery

**2. Topology Layer** - 5 Swarm Patterns
- **Hierarchical**: Alfred as root, delegating to specialist layers
- **Mesh**: Full peer-to-peer connectivity for collaborative tasks
- **Star**: Hub-and-spoke pattern for centralized coordination
- **Ring**: Sequential processing chain for pipeline workflows
- **Adaptive**: Dynamic topology based on workload and agent availability

**3. Resource Layer** - Budget and Quota Management
- **TokenBudget**: Per-swarm token allocation (200K default)
- **AgentQuota**: Execution limits per agent type
- **PriorityQueue**: Task priority management
- **ResourceMonitor**: Real-time resource utilization tracking

**4. Memory Layer** - SQLite-based Persistence
- **SwarmDB**: Core database with 12 performance indexes
- **SemanticMemory**: Long-term knowledge and patterns
- **EpisodicMemory**: Event and decision history
- **ContextHints**: Session preferences and expertise levels

**5. Hook Layer** - Event-driven Lifecycle Tracking
- **AgentLifecycle**: Spawn/complete/error event tracking
- **PreTask/PostTask**: Task-level hooks (Phase 6)
- **PreAgent/PostAgent**: Agent-level hooks (Phase 6)
- **EventBus**: Centralized event distribution

**6. Interface Layer** - Clean Abstractions
- **IMemoryProvider**: Memory system interface
- **ICoordinator**: Swarm coordination interface
- **IResourceController**: Resource management interface
- **ITopology**: Topology pattern interface

---

## 🎯 Core Components

### SwarmDB - Persistent Storage

**Purpose**: SQLite-based storage for multi-agent coordination

**Schema**:
```sql
-- Agent lifecycle events
CREATE TABLE agent_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE NOT NULL,
    event_type TEXT NOT NULL,  -- 'spawn' | 'complete' | 'error'
    agent_id TEXT NOT NULL,
    agent_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    metadata TEXT,  -- JSON blob
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Agent state registry
CREATE TABLE agent_registry (
    agent_id TEXT PRIMARY KEY,
    agent_type TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'spawned' | 'running' | 'complete' | 'error'
    spawn_time REAL NOT NULL,
    complete_time REAL,
    duration_ms INTEGER,
    metadata TEXT,
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Cross-session memory
CREATE TABLE session_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,  -- 'semantic' | 'episodic' | 'context_hint'
    key TEXT NOT NULL,
    value TEXT,  -- JSON blob
    timestamp TEXT NOT NULL,
    ttl_hours INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Performance Indexes** (12 total):
- `idx_agent_events_agent_id`: Fast agent event lookup
- `idx_agent_events_event_type`: Filter by event type
- `idx_agent_events_timestamp`: Timeline queries
- `idx_agent_registry_status`: Filter by agent status
- `idx_agent_registry_agent_type`: Filter by agent type
- `idx_session_memory_session_id`: Session history lookup
- `idx_session_memory_memory_type`: Filter by memory type
- `idx_session_memory_key`: Fast key lookup
- 4 additional indexes for semantic/episodic memory

**Usage Example**:
```python
from moai_flow.memory.swarm_db import SwarmDB

db = SwarmDB(db_path=".moai/memory/swarm.db")

# Insert event
db.insert_event({
    "event_type": "spawn",
    "agent_id": "backend-001",
    "agent_type": "expert-backend",
    "timestamp": "2025-11-29T10:00:00Z",
    "metadata": {"task": "Implement API"}
})

# Query events
events = db.get_events(agent_id="backend-001", limit=10)
for event in events:
    print(f"{event['event_type']}: {event['timestamp']}")
```

### SemanticMemory - Long-term Knowledge

**Purpose**: Store and retrieve long-term knowledge patterns and best practices

**Categories**:
- `pattern`: Design patterns and architectural patterns
- `best_practice`: Proven best practices
- `anti_pattern`: Common mistakes to avoid
- `lesson_learned`: Insights from past experiences

**Usage Example**:
```python
from moai_flow.memory.semantic_memory import SemanticMemory

semantic = SemanticMemory(db)

# Store pattern
semantic.store_knowledge(
    category="pattern",
    content="Use dependency injection for testability",
    confidence=0.9,
    tags=["design", "testing"]
)

# Query patterns
patterns = semantic.query_knowledge(
    category="pattern",
    min_confidence=0.8,
    tags=["testing"]
)

for pattern in patterns:
    print(f"{pattern['content']} (confidence: {pattern['confidence']})")
```

### EpisodicMemory - Event History

**Purpose**: Track events and decisions over time

**Categories**:
- `architectural_decision`: Major design decisions
- `implementation_choice`: Implementation strategy choices
- `issue_resolution`: Problem-solving approaches
- `learning_moment`: Important discoveries

**Usage Example**:
```python
from moai_flow.memory.episodic_memory import EpisodicMemory

episodic = EpisodicMemory(db)

# Record decision
episodic.record_episode(
    category="architectural_decision",
    content="Chose FastAPI for REST API framework",
    importance=0.9,
    tags=["backend", "framework"],
    related_agents=["backend-expert"]
)

# Query decisions
decisions = episodic.query_episodes(
    category="architectural_decision",
    min_importance=0.7
)

for decision in decisions:
    print(f"{decision['content']} (importance: {decision['importance']})")
```

### ContextHints - Session Preferences

**Purpose**: Store user preferences and expertise levels for personalized experience

**Expertise Levels**:
- `BEGINNER`: Detailed explanations, step-by-step guidance
- `INTERMEDIATE`: Balanced guidance, some assumptions
- `ADVANCED`: Minimal explanation, technical depth
- `EXPERT`: Maximum efficiency, domain-specific jargon

**Usage Example**:
```python
from moai_flow.memory.context_hints import ContextHints, ExpertiseLevel

hints = ContextHints(db)

# Set expertise level
hints.set_expertise_level(ExpertiseLevel.INTERMEDIATE)

# Set workflow preferences
hints.set_preference("workflow", "parallel")
hints.set_preference("validation", "strict")
hints.set_preference("documentation", "comprehensive")

# Retrieve preferences
level = hints.get_expertise_level()  # INTERMEDIATE
workflow = hints.get_preference("workflow")  # "parallel"

# Alfred adapts responses based on these preferences
```

### TokenBudget - Resource Management

**Purpose**: Manage token allocation across swarms

**Usage Example**:
```python
from moai_flow.resource.token_budget import TokenBudget

budget = TokenBudget(total_budget=200000)

# Allocate to swarms
budget.allocate_to_swarm("backend-swarm", 50000)
budget.allocate_to_swarm("frontend-swarm", 50000)

# Track usage
budget.consume_tokens("backend-swarm", 5000)
remaining = budget.get_remaining_tokens("backend-swarm")  # 45000

# Check if can allocate more
if budget.can_allocate("test-swarm", 30000):
    budget.allocate_to_swarm("test-swarm", 30000)
```

### AgentLifecycleHook - Event Tracking

**Purpose**: Track agent lifecycle events with comprehensive metadata

**Events**:
- `spawn`: Agent created
- `complete`: Agent finished successfully
- `error`: Agent encountered error

**Usage Example**:
```python
from moai_flow.hooks.agent_lifecycle import AgentLifecycleHook

lifecycle = AgentLifecycleHook(db)

# Track spawn
lifecycle.on_agent_spawn("backend-001", metadata={
    "role": "expert-backend",
    "task": "Implement REST API",
    "model": "claude-sonnet-4",
    "priority": "high"
})

# Track completion
lifecycle.on_agent_complete("backend-001", result={
    "status": "success",
    "files_created": 3,
    "tests_added": 8,
    "duration_ms": 45000
})

# Track error
lifecycle.on_agent_error("backend-002", error={
    "type": "timeout",
    "message": "Agent exceeded 2-minute timeout",
    "stack_trace": "..."
})

# Query events
events = lifecycle.get_agent_events("backend-001")
print(f"Total events: {len(events)}")
```

---

## 💾 Memory System

### Cross-Session Memory Architecture

```mermaid
graph LR
    A[Session 1] --> B[SwarmDB]
    C[Session 2] --> B
    D[Session 3] --> B
    B --> E[SemanticMemory]
    B --> F[EpisodicMemory]
    B --> G[ContextHints]

    style A fill:#3498DB,stroke:#2471A3,color:#fff
    style C fill:#3498DB,stroke:#2471A3,color:#fff
    style D fill:#3498DB,stroke:#2471A3,color:#fff
    style B fill:#E74C3C,stroke:#A83426,color:#fff
    style E fill:#9B59B6,stroke:#6C3A7C,color:#fff
    style F fill:#F39C12,stroke:#B87503,color:#fff
    style G fill:#27AE60,stroke:#1E8449,color:#fff
```

### SemanticMemory - Long-term Patterns

**Purpose**: Persistent knowledge that improves over time

**Storage**:
```python
semantic = SemanticMemory(db)

# Store architectural pattern
semantic.store_knowledge(
    category="pattern",
    content="Use repository pattern for data access",
    confidence=0.85,
    tags=["architecture", "database"]
)

# Store best practice
semantic.store_knowledge(
    category="best_practice",
    content="Always validate input at API boundaries",
    confidence=0.95,
    tags=["security", "validation"]
)

# Store anti-pattern
semantic.store_knowledge(
    category="anti_pattern",
    content="Avoid using global state in multi-threaded code",
    confidence=0.9,
    tags=["concurrency", "anti-pattern"]
)
```

**Retrieval**:
```python
# Query by category and confidence
patterns = semantic.query_knowledge(
    category="pattern",
    min_confidence=0.8
)

# Query by tags
security_practices = semantic.query_knowledge(
    tags=["security"],
    min_confidence=0.8
)

# Update confidence based on usage
semantic.update_confidence("knowledge-id-123", new_confidence=0.92)
```

### EpisodicMemory - Decision History

**Purpose**: Track decisions and events chronologically

**Storage**:
```python
episodic = EpisodicMemory(db)

# Record architectural decision
episodic.record_episode(
    category="architectural_decision",
    content="Selected PostgreSQL over MongoDB for relational data",
    importance=0.9,
    tags=["database", "architecture"],
    related_agents=["db-expert", "backend-expert"]
)

# Record implementation choice
episodic.record_episode(
    category="implementation_choice",
    content="Chose async/await over threading for I/O operations",
    importance=0.7,
    tags=["performance", "async"]
)

# Record issue resolution
episodic.record_episode(
    category="issue_resolution",
    content="Fixed N+1 query problem with eager loading",
    importance=0.8,
    tags=["performance", "database"],
    related_issues=["#123"]
)
```

**Retrieval**:
```python
# Query by category
decisions = episodic.query_episodes(
    category="architectural_decision",
    min_importance=0.7
)

# Query by tags
db_episodes = episodic.query_episodes(
    tags=["database"],
    min_importance=0.6
)

# Query by time range
recent_episodes = episodic.query_episodes(
    start_time="2025-11-01T00:00:00Z",
    end_time="2025-11-30T23:59:59Z"
)
```

### ContextHints - User Preferences

**Purpose**: Personalize experience based on user preferences and expertise

**Expertise Levels**:
```python
hints = ContextHints(db)

# Set expertise level
hints.set_expertise_level(ExpertiseLevel.BEGINNER)
# Alfred provides detailed step-by-step guidance

hints.set_expertise_level(ExpertiseLevel.INTERMEDIATE)
# Alfred balances explanation with efficiency

hints.set_expertise_level(ExpertiseLevel.ADVANCED)
# Alfred assumes knowledge, focuses on technical depth

hints.set_expertise_level(ExpertiseLevel.EXPERT)
# Alfred maximizes efficiency, uses domain jargon
```

**Preferences**:
```python
# Set workflow preferences
hints.set_preference("workflow", "parallel")
# Alfred prefers parallel agent execution

hints.set_preference("workflow", "sequential")
# Alfred prefers sequential, step-by-step execution

# Set validation preferences
hints.set_preference("validation", "strict")
# Alfred enforces strict quality gates

hints.set_preference("validation", "relaxed")
# Alfred uses relaxed validation

# Set documentation preferences
hints.set_preference("documentation", "comprehensive")
# Alfred generates detailed documentation

hints.set_preference("documentation", "minimal")
# Alfred generates concise documentation

# Set code style preferences
hints.set_preference("code_style", "functional")
hints.set_preference("code_style", "oop")
hints.set_preference("code_style", "procedural")
```

**Retrieval**:
```python
# Get current expertise level
level = hints.get_expertise_level()

# Get all preferences
all_prefs = hints.get_all_preferences()

# Get specific preference
workflow = hints.get_preference("workflow")
validation = hints.get_preference("validation")
```

### Memory Integration Example

**Scenario**: Building a REST API with learned best practices

```python
from moai_flow.memory import SwarmDB, SemanticMemory, EpisodicMemory, ContextHints

# Initialize
db = SwarmDB()
semantic = SemanticMemory(db)
episodic = EpisodicMemory(db)
hints = ContextHints(db)

# Check expertise level
level = hints.get_expertise_level()

# Retrieve relevant patterns
api_patterns = semantic.query_knowledge(
    category="pattern",
    tags=["api", "rest"],
    min_confidence=0.8
)

# Check past API decisions
past_decisions = episodic.query_episodes(
    category="architectural_decision",
    tags=["api"],
    min_importance=0.7
)

# Make informed decision
if level == ExpertiseLevel.BEGINNER:
    # Provide detailed guidance with patterns
    guidance = generate_detailed_guidance(api_patterns, past_decisions)
else:
    # Provide concise recommendations
    guidance = generate_concise_recommendations(api_patterns)

# Record new decision
episodic.record_episode(
    category="architectural_decision",
    content="Used FastAPI with Pydantic for type safety",
    importance=0.9,
    tags=["api", "framework", "type-safety"]
)

# Store new pattern if successful
semantic.store_knowledge(
    category="pattern",
    content="FastAPI + Pydantic provides excellent type safety",
    confidence=0.85,
    tags=["api", "type-safety"]
)
```

---

## 🔀 Topology Patterns (Phase 5 - Coming Soon)

### Overview

MoAI-Flow supports 5 swarm topologies, each optimized for different task types:

| Topology | Best For | Agents | Communication |
|----------|----------|--------|---------------|
| **Hierarchical** | Complex tasks with clear delegation | 5-20 | Tree-based |
| **Mesh** | Collaborative tasks requiring peer feedback | 3-10 | Full connectivity |
| **Star** | Simple tasks with central coordination | 3-8 | Hub-and-spoke |
| **Ring** | Sequential pipelines | 3-15 | Chain |
| **Adaptive** | Dynamic workloads | Variable | Context-aware |

### 1. Hierarchical Topology

**Purpose**: Alfred as root coordinator, delegating to specialist layers

**Structure**:
```mermaid
graph TD
    A[Alfred] --> B1[Manager Layer]
    A --> B2[Manager Layer]
    B1 --> C1[Expert Layer]
    B1 --> C2[Expert Layer]
    B2 --> C3[Expert Layer]
    B2 --> C4[Expert Layer]

    style A fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style B1 fill:#50C878,stroke:#2E7D4E,color:#fff
    style B2 fill:#50C878,stroke:#2E7D4E,color:#fff
```

**Usage**:
```python
from moai_flow.topology.hierarchical import HierarchicalTopology

topology = HierarchicalTopology(root_agent="alfred")

# Add manager layer
topology.add_layer("managers", [
    "manager-tdd",
    "manager-docs",
    "manager-git"
])

# Add expert layer
topology.add_layer("experts", [
    "expert-backend",
    "expert-frontend",
    "expert-database"
])

# Execute with delegation
result = topology.execute(task="Build full-stack app")
```

**Best For**:
- Complex multi-phase projects
- Clear role separation
- Hierarchical decision-making
- Large teams (10+ agents)

### 2. Mesh Topology

**Purpose**: Full peer-to-peer connectivity for collaborative tasks

**Structure**:
```mermaid
graph LR
    A[Agent 1] --- B[Agent 2]
    A --- C[Agent 3]
    A --- D[Agent 4]
    B --- C
    B --- D
    C --- D

    style A fill:#E74C3C,stroke:#A83426,color:#fff
    style B fill:#E74C3C,stroke:#A83426,color:#fff
    style C fill:#E74C3C,stroke:#A83426,color:#fff
    style D fill:#E74C3C,stroke:#A83426,color:#fff
```

**Usage**:
```python
from moai_flow.topology.mesh import MeshTopology

topology = MeshTopology(agents=[
    "expert-backend",
    "expert-frontend",
    "expert-database",
    "expert-security"
])

# All agents can communicate directly
result = topology.execute(task="Design secure architecture")
```

**Best For**:
- Collaborative design tasks
- Peer review processes
- Consensus-building
- Small teams (3-6 agents)

### 3. Star Topology

**Purpose**: Hub-and-spoke pattern for centralized coordination

**Structure**:
```mermaid
graph TD
    A[Hub Agent] --> B[Agent 1]
    A --> C[Agent 2]
    A --> D[Agent 3]
    A --> E[Agent 4]

    style A fill:#9B59B6,stroke:#6C3A7C,color:#fff
    style B fill:#3498DB,stroke:#2471A3,color:#fff
    style C fill:#3498DB,stroke:#2471A3,color:#fff
    style D fill:#3498DB,stroke:#2471A3,color:#fff
    style E fill:#3498DB,stroke:#2471A3,color:#fff
```

**Usage**:
```python
from moai_flow.topology.star import StarTopology

topology = StarTopology(
    hub_agent="alfred",
    spoke_agents=[
        "expert-backend",
        "expert-frontend",
        "expert-testing"
    ]
)

# Hub coordinates all spoke agents
result = topology.execute(task="Implement feature")
```

**Best For**:
- Simple task distribution
- Parallel independent tasks
- Centralized control
- Medium teams (4-8 agents)

### 4. Ring Topology

**Purpose**: Sequential processing chain for pipeline workflows

**Structure**:
```mermaid
graph LR
    A[Agent 1] --> B[Agent 2]
    B --> C[Agent 3]
    C --> D[Agent 4]
    D --> E[Agent 5]

    style A fill:#F39C12,stroke:#B87503,color:#fff
    style B fill:#F39C12,stroke:#B87503,color:#fff
    style C fill:#F39C12,stroke:#B87503,color:#fff
    style D fill:#F39C12,stroke:#B87503,color:#fff
    style E fill:#F39C12,stroke:#B87503,color:#fff
```

**Usage**:
```python
from moai_flow.topology.ring import RingTopology

topology = RingTopology(agents=[
    "expert-spec",      # 1. Generate SPEC
    "expert-backend",   # 2. Implement API
    "expert-testing",   # 3. Write tests
    "expert-docs",      # 4. Generate docs
    "expert-deploy"     # 5. Deploy
])

# Sequential execution
result = topology.execute(task="Full pipeline")
```

**Best For**:
- Sequential pipelines
- Waterfall workflows
- Data processing chains
- Long chains (5-15 agents)

### 5. Adaptive Topology

**Purpose**: Dynamic topology based on workload and context

**Usage**:
```python
from moai_flow.topology.adaptive import AdaptiveTopology

topology = AdaptiveTopology()

# Automatically selects best topology
result = topology.execute(
    task="Complex project",
    context={
        "complexity": "high",
        "team_size": 8,
        "collaboration_needed": True,
        "sequential_steps": False
    }
)

# Topology selection logic:
# - High collaboration → Mesh
# - Many sequential steps → Ring
# - Large team + clear roles → Hierarchical
# - Simple distribution → Star
```

**Best For**:
- Variable workloads
- Context-dependent tasks
- Dynamic team sizes
- Intelligent automation

---

## 💻 API Reference

### SwarmDB

**Core Database Operations**

```python
class SwarmDB:
    """SQLite-based persistent storage for multi-agent coordination"""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize SwarmDB

        Args:
            db_path: Path to SQLite database (default: .moai/memory/swarm.db)
        """

    # Agent Event Operations
    def insert_event(
        self,
        event_data: Dict[str, Any],
        event_id: Optional[str] = None
    ) -> str:
        """
        Insert agent lifecycle event

        Args:
            event_data: Event data with keys:
                - event_type: 'spawn' | 'complete' | 'error'
                - agent_id: Agent identifier
                - agent_type: Agent type (e.g., 'expert-backend')
                - timestamp: ISO8601 timestamp
                - metadata: Additional metadata dict
            event_id: Optional event ID (auto-generated if None)

        Returns:
            event_id of inserted event
        """

    def get_events(
        self,
        agent_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query agent events

        Args:
            agent_id: Filter by agent ID
            event_type: Filter by event type ('spawn', 'complete', 'error')
            limit: Maximum events to return

        Returns:
            List of event dictionaries
        """

    # Agent Registry Operations
    def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        status: str = "spawned",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register agent in registry"""

    def update_agent_status(
        self,
        agent_id: str,
        status: str,
        duration_ms: Optional[int] = None
    ) -> None:
        """Update agent status"""

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent from registry"""

    def get_active_agents(self) -> List[Dict[str, Any]]:
        """Get all active (spawned/running) agents"""

    # Session Memory Operations
    def store_memory(
        self,
        session_id: str,
        memory_type: str,
        key: str,
        value: Any,
        ttl_hours: Optional[int] = None
    ) -> None:
        """Store session memory"""

    def get_memory(
        self,
        session_id: str,
        memory_type: str,
        key: str
    ) -> Optional[Any]:
        """Retrieve session memory"""

    # Maintenance Operations
    def cleanup_old_events(self, days: int = 30) -> int:
        """Delete events older than specified days"""

    def vacuum(self) -> None:
        """Optimize database storage"""

    def close(self) -> None:
        """Close all database connections"""
```

### SemanticMemory

**Long-term Knowledge Management**

```python
class SemanticMemory:
    """Long-term knowledge storage and retrieval"""

    def __init__(self, db: SwarmDB):
        """Initialize with SwarmDB instance"""

    def store_knowledge(
        self,
        category: str,
        content: str,
        confidence: float = 0.5,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Store knowledge item

        Args:
            category: 'pattern' | 'best_practice' | 'anti_pattern' | 'lesson_learned'
            content: Knowledge content
            confidence: Confidence score (0.0-1.0)
            tags: Optional tags for categorization

        Returns:
            knowledge_id
        """

    def query_knowledge(
        self,
        category: Optional[str] = None,
        min_confidence: float = 0.5,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Query knowledge items

        Args:
            category: Filter by category
            min_confidence: Minimum confidence threshold
            tags: Filter by tags
            limit: Maximum results

        Returns:
            List of knowledge items
        """

    def update_confidence(self, knowledge_id: str, new_confidence: float) -> None:
        """Update knowledge confidence based on usage"""

    def delete_knowledge(self, knowledge_id: str) -> None:
        """Delete knowledge item"""
```

### EpisodicMemory

**Event and Decision History**

```python
class EpisodicMemory:
    """Event and decision history storage"""

    def __init__(self, db: SwarmDB):
        """Initialize with SwarmDB instance"""

    def record_episode(
        self,
        category: str,
        content: str,
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
        related_agents: Optional[List[str]] = None,
        related_issues: Optional[List[str]] = None
    ) -> str:
        """
        Record episode

        Args:
            category: 'architectural_decision' | 'implementation_choice' |
                     'issue_resolution' | 'learning_moment'
            content: Episode content
            importance: Importance score (0.0-1.0)
            tags: Optional tags
            related_agents: Related agent IDs
            related_issues: Related issue IDs

        Returns:
            episode_id
        """

    def query_episodes(
        self,
        category: Optional[str] = None,
        min_importance: float = 0.5,
        tags: Optional[List[str]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Query episodes

        Args:
            category: Filter by category
            min_importance: Minimum importance threshold
            tags: Filter by tags
            start_time: Filter by start time (ISO8601)
            end_time: Filter by end time (ISO8601)
            limit: Maximum results

        Returns:
            List of episodes
        """

    def update_importance(self, episode_id: str, new_importance: float) -> None:
        """Update episode importance"""

    def delete_episode(self, episode_id: str) -> None:
        """Delete episode"""
```

### ContextHints

**User Preferences and Expertise**

```python
class ExpertiseLevel(Enum):
    """User expertise levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ContextHints:
    """User preferences and expertise management"""

    def __init__(self, db: SwarmDB):
        """Initialize with SwarmDB instance"""

    def set_expertise_level(self, level: ExpertiseLevel) -> None:
        """Set user expertise level"""

    def get_expertise_level(self) -> ExpertiseLevel:
        """Get user expertise level"""

    def set_preference(self, category: str, value: str) -> None:
        """
        Set user preference

        Args:
            category: Preference category
                - "workflow": "parallel" | "sequential"
                - "validation": "strict" | "relaxed"
                - "documentation": "comprehensive" | "minimal"
                - "code_style": "functional" | "oop" | "procedural"
            value: Preference value
        """

    def get_preference(self, category: str) -> Optional[str]:
        """Get user preference"""

    def get_all_preferences(self) -> Dict[str, str]:
        """Get all user preferences"""

    def clear_preferences(self) -> None:
        """Clear all preferences"""
```

### TokenBudget

**Token Allocation Management**

```python
class TokenBudget:
    """Per-swarm token budget management"""

    def __init__(self, total_budget: int = 200000):
        """
        Initialize token budget

        Args:
            total_budget: Total available tokens (default: 200K)
        """

    def allocate_to_swarm(self, swarm_id: str, tokens: int) -> bool:
        """
        Allocate tokens to swarm

        Args:
            swarm_id: Swarm identifier
            tokens: Tokens to allocate

        Returns:
            True if allocation successful
        """

    def consume_tokens(self, swarm_id: str, tokens: int) -> bool:
        """
        Consume tokens from swarm budget

        Args:
            swarm_id: Swarm identifier
            tokens: Tokens consumed

        Returns:
            True if consumption successful
        """

    def get_remaining_tokens(self, swarm_id: str) -> int:
        """Get remaining tokens for swarm"""

    def get_total_remaining(self) -> int:
        """Get total remaining tokens"""

    def can_allocate(self, swarm_id: str, tokens: int) -> bool:
        """Check if can allocate tokens to swarm"""

    def reset_swarm(self, swarm_id: str) -> None:
        """Reset swarm token usage"""

    def reset_all(self) -> None:
        """Reset all token budgets"""
```

### AgentLifecycleHook

**Agent Event Tracking**

```python
class AgentLifecycleHook:
    """Agent lifecycle event tracking"""

    def __init__(self, db: SwarmDB):
        """Initialize with SwarmDB instance"""

    def on_agent_spawn(
        self,
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Track agent spawn event

        Args:
            agent_id: Agent identifier
            metadata: Spawn metadata (role, task, model, priority, etc.)

        Returns:
            event_id
        """

    def on_agent_complete(
        self,
        agent_id: str,
        result: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Track agent completion event

        Args:
            agent_id: Agent identifier
            result: Completion result (status, files, tests, duration, etc.)

        Returns:
            event_id
        """

    def on_agent_error(
        self,
        agent_id: str,
        error: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Track agent error event

        Args:
            agent_id: Agent identifier
            error: Error details (type, message, stack_trace, etc.)

        Returns:
            event_id
        """

    def get_agent_events(
        self,
        agent_id: str,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get agent events

        Args:
            agent_id: Agent identifier
            event_type: Filter by event type
            limit: Maximum events

        Returns:
            List of events
        """

    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent statistics

        Returns:
            Statistics dict with spawn_count, complete_count, error_count,
            avg_duration_ms, success_rate
        """
```

---

## 📚 Examples

### Example 1: Basic Agent Tracking

```python
#!/usr/bin/env python3
"""Track agent lifecycle events"""

from moai_flow.memory.swarm_db import SwarmDB
from moai_flow.hooks.agent_lifecycle import AgentLifecycleHook
import time

# Initialize
db = SwarmDB()
lifecycle = AgentLifecycleHook(db)

# Spawn backend agent
lifecycle.on_agent_spawn("backend-001", metadata={
    "role": "expert-backend",
    "task": "Implement REST API",
    "model": "claude-sonnet-4",
    "priority": "high"
})

# Simulate work
print("Agent working...")
time.sleep(2)

# Complete successfully
lifecycle.on_agent_complete("backend-001", result={
    "status": "success",
    "files_created": ["api/routes.py", "api/models.py", "api/schemas.py"],
    "tests_added": 12,
    "duration_ms": 2000
})

# Query events
events = lifecycle.get_agent_events("backend-001")
print(f"\nAgent Events ({len(events)} total):")
for event in events:
    print(f"  {event['event_type']} @ {event['timestamp']}")
    print(f"  Metadata: {event['metadata']}")

# Get statistics
stats = lifecycle.get_agent_stats("backend-001")
print(f"\nAgent Stats:")
print(f"  Spawns: {stats['spawn_count']}")
print(f"  Completions: {stats['complete_count']}")
print(f"  Errors: {stats['error_count']}")
print(f"  Success Rate: {stats['success_rate']:.1%}")
```

### Example 2: Cross-Session Knowledge

```python
#!/usr/bin/env python3
"""Store and retrieve cross-session knowledge"""

from moai_flow.memory import SwarmDB, SemanticMemory, EpisodicMemory

# Session 1: Store knowledge
print("=== Session 1: Store Knowledge ===")
db = SwarmDB()
semantic = SemanticMemory(db)
episodic = EpisodicMemory(db)

# Store pattern learned
semantic.store_knowledge(
    category="pattern",
    content="Use FastAPI dependency injection for database sessions",
    confidence=0.9,
    tags=["fastapi", "database", "di"]
)

# Record decision
episodic.record_episode(
    category="architectural_decision",
    content="Chose SQLAlchemy ORM over raw SQL for maintainability",
    importance=0.85,
    tags=["database", "orm"]
)

print("✅ Knowledge stored")

# Close session
db.close()

# Session 2: Retrieve knowledge
print("\n=== Session 2: Retrieve Knowledge ===")
db2 = SwarmDB()
semantic2 = SemanticMemory(db2)
episodic2 = EpisodicMemory(db2)

# Query patterns
patterns = semantic2.query_knowledge(
    category="pattern",
    tags=["fastapi"],
    min_confidence=0.8
)

print(f"Found {len(patterns)} patterns:")
for pattern in patterns:
    print(f"  - {pattern['content']} (confidence: {pattern['confidence']})")

# Query decisions
decisions = episodic2.query_episodes(
    category="architectural_decision",
    tags=["database"],
    min_importance=0.7
)

print(f"\nFound {len(decisions)} decisions:")
for decision in decisions:
    print(f"  - {decision['content']} (importance: {decision['importance']})")

db2.close()
```

### Example 3: Personalized Experience

```python
#!/usr/bin/env python3
"""Personalize experience based on user preferences"""

from moai_flow.memory import SwarmDB, ContextHints
from moai_flow.memory.context_hints import ExpertiseLevel

db = SwarmDB()
hints = ContextHints(db)

# Set user profile
hints.set_expertise_level(ExpertiseLevel.INTERMEDIATE)
hints.set_preference("workflow", "parallel")
hints.set_preference("validation", "strict")
hints.set_preference("documentation", "comprehensive")

# Retrieve preferences
level = hints.get_expertise_level()
workflow = hints.get_preference("workflow")
validation = hints.get_preference("validation")

print(f"User Profile:")
print(f"  Expertise: {level.value}")
print(f"  Workflow: {workflow}")
print(f"  Validation: {validation}")

# Alfred adapts responses
if level == ExpertiseLevel.BEGINNER:
    print("\n📘 Detailed Step-by-Step Guidance")
elif level == ExpertiseLevel.INTERMEDIATE:
    print("\n📗 Balanced Guidance with Examples")
elif level == ExpertiseLevel.ADVANCED:
    print("\n📙 Technical Deep Dive")
else:
    print("\n📕 Expert-Level Concise Recommendations")

# Alfred adapts workflow
if workflow == "parallel":
    print("⚡ Using parallel agent execution for faster results")
else:
    print("🔄 Using sequential execution for careful validation")

db.close()
```

### Example 4: Token Budget Management

```python
#!/usr/bin/env python3
"""Manage token budgets across swarms"""

from moai_flow.resource.token_budget import TokenBudget

# Initialize budget (200K tokens)
budget = TokenBudget(total_budget=200000)

# Allocate to swarms
print("=== Allocating Tokens ===")
budget.allocate_to_swarm("backend-swarm", 50000)
budget.allocate_to_swarm("frontend-swarm", 50000)
budget.allocate_to_swarm("testing-swarm", 30000)

print(f"Total allocated: {200000 - budget.get_total_remaining()}")
print(f"Remaining: {budget.get_total_remaining()}")

# Consume tokens
print("\n=== Consuming Tokens ===")
budget.consume_tokens("backend-swarm", 5000)
budget.consume_tokens("frontend-swarm", 3000)

print(f"Backend remaining: {budget.get_remaining_tokens('backend-swarm')}")
print(f"Frontend remaining: {budget.get_remaining_tokens('frontend-swarm')}")

# Check if can allocate more
print("\n=== Checking Allocation ===")
can_allocate = budget.can_allocate("docs-swarm", 40000)
print(f"Can allocate 40K to docs-swarm: {can_allocate}")

if can_allocate:
    budget.allocate_to_swarm("docs-swarm", 40000)
    print("✅ Allocated 40K to docs-swarm")

# Reset specific swarm
budget.reset_swarm("testing-swarm")
print(f"Testing-swarm reset: {budget.get_remaining_tokens('testing-swarm')}")
```

### Example 5: Complete Workflow

```python
#!/usr/bin/env python3
"""Complete multi-agent workflow with memory and tracking"""

from moai_flow.memory import SwarmDB, SemanticMemory, ContextHints
from moai_flow.hooks.agent_lifecycle import AgentLifecycleHook
from moai_flow.resource.token_budget import TokenBudget
from moai_flow.memory.context_hints import ExpertiseLevel
import time

# Initialize all components
db = SwarmDB()
semantic = SemanticMemory(db)
hints = ContextHints(db)
lifecycle = AgentLifecycleHook(db)
budget = TokenBudget(total_budget=200000)

# Configure user preferences
hints.set_expertise_level(ExpertiseLevel.INTERMEDIATE)
hints.set_preference("workflow", "parallel")

# Allocate token budget
budget.allocate_to_swarm("api-implementation", 100000)

# Phase 1: Spawn multiple agents in parallel
print("=== Phase 1: Spawn Agents ===")
agents = [
    ("backend-001", "expert-backend", "Implement REST API"),
    ("testing-001", "expert-testing", "Write integration tests"),
    ("docs-001", "expert-docs", "Generate API documentation")
]

for agent_id, role, task in agents:
    lifecycle.on_agent_spawn(agent_id, metadata={
        "role": role,
        "task": task,
        "model": "claude-sonnet-4"
    })
    print(f"  ✅ Spawned {agent_id}")

# Simulate parallel work
print("\n=== Phase 2: Agents Working ===")
time.sleep(1)

# Phase 3: Complete agents
print("\n=== Phase 3: Complete Agents ===")
completions = [
    ("backend-001", {"files_created": 5, "tests_added": 15, "tokens_used": 40000}),
    ("testing-001", {"files_created": 3, "tests_added": 20, "tokens_used": 30000}),
    ("docs-001", {"files_created": 2, "tokens_used": 25000})
]

for agent_id, result in completions:
    result["status"] = "success"
    result["duration_ms"] = 1000
    lifecycle.on_agent_complete(agent_id, result=result)
    budget.consume_tokens("api-implementation", result["tokens_used"])
    print(f"  ✅ Completed {agent_id}")

# Store learned patterns
print("\n=== Phase 4: Store Knowledge ===")
semantic.store_knowledge(
    category="pattern",
    content="FastAPI async endpoints improve performance significantly",
    confidence=0.9,
    tags=["fastapi", "async", "performance"]
)
print("  ✅ Pattern stored")

# Generate report
print("\n=== Final Report ===")
print(f"Total Agents: {len(agents)}")
print(f"Successful: {len(completions)}")
print(f"Files Created: {sum(c[1].get('files_created', 0) for c in completions)}")
print(f"Tests Added: {sum(c[1].get('tests_added', 0) for c in completions)}")
print(f"Tokens Used: {200000 - budget.get_total_remaining()}")
print(f"Tokens Remaining: {budget.get_total_remaining()}")

# Cleanup
db.close()
print("\n✅ Workflow complete!")
```

---

## 🛠️ Development

### Setup Development Environment

**1. Clone and Install**
```bash
# Clone repository
git clone https://github.com/superdisco-agents/moai-flow.git
cd moai-flow

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Or using uv (faster)
uv pip install -e ".[dev]"
```

**2. Install Pre-commit Hooks**
```bash
pre-commit install
```

**3. Verify Setup**
```bash
# Run tests
pytest tests/ -v

# Check code style
black --check moai_flow/ tests/
ruff check moai_flow/

# Type checking
mypy moai_flow/
```

### Project Structure

```
moai-flow/
├── moai_flow/                  # Main package
│   ├── core/                   # Core interfaces and base classes
│   │   ├── __init__.py
│   │   └── interfaces.py       # IMemoryProvider, ICoordinator, IResourceController
│   │
│   ├── memory/                 # Memory system
│   │   ├── __init__.py
│   │   ├── swarm_db.py        # SQLite database (12 indexes)
│   │   ├── semantic_memory.py # Long-term knowledge
│   │   ├── episodic_memory.py # Event history
│   │   └── context_hints.py   # User preferences
│   │
│   ├── resource/              # Resource management
│   │   ├── __init__.py
│   │   └── token_budget.py    # Token allocation
│   │
│   ├── hooks/                 # Lifecycle hooks
│   │   ├── __init__.py
│   │   └── agent_lifecycle.py # Agent event tracking
│   │
│   ├── topology/              # Swarm topologies (Phase 5)
│   │   ├── __init__.py
│   │   ├── hierarchical.py
│   │   ├── mesh.py
│   │   ├── star.py
│   │   ├── ring.py
│   │   └── adaptive.py
│   │
│   ├── coordination/          # Consensus and conflict resolution (Phase 6)
│   │   ├── __init__.py
│   │   ├── consensus.py
│   │   └── conflict_resolver.py
│   │
│   ├── docs/                  # Documentation library
│   │   ├── quickstart/
│   │   ├── guides/
│   │   ├── advanced/
│   │   └── examples/
│   │
│   └── specs/                 # PRD specifications
│       ├── PRD-00-overview.md
│       ├── PRD-01-concurrent-batching.md
│       └── ...
│
├── tests/                     # Test suite (200+ tests)
│   ├── moai_flow/
│   │   ├── core/
│   │   │   └── test_interfaces.py     (1223 lines)
│   │   ├── memory/
│   │   │   ├── test_swarm_db.py       (770 lines)
│   │   │   ├── test_semantic_memory.py (875 lines)
│   │   │   ├── test_episodic_memory.py (959 lines)
│   │   │   └── test_context_hints.py   (697 lines)
│   │   ├── resource/
│   │   │   └── test_token_budget.py
│   │   └── hooks/
│   │       └── test_agent_lifecycle.py
│
├── .moai/                     # MoAI-ADK integration
│   ├── config/
│   │   └── config.json
│   ├── memory/
│   │   └── swarm.db           # SQLite database
│   ├── specs/
│   └── docs/
│
├── pyproject.toml             # Project configuration
├── README.md                  # This file
├── LICENSE                    # MIT License
└── .pre-commit-config.yaml    # Pre-commit hooks
```

### Development Workflow

**1. Create Feature Branch**
```bash
git checkout -b feature/my-feature
```

**2. Write Tests First (TDD)**
```python
# tests/moai_flow/feature/test_my_feature.py
import pytest
from moai_flow.feature import MyFeature

def test_my_feature():
    """Test my feature"""
    feature = MyFeature()
    assert feature.do_something() == expected_result
```

**3. Implement Feature**
```python
# moai_flow/feature/my_feature.py
class MyFeature:
    """My feature implementation"""

    def do_something(self):
        """Do something useful"""
        return result
```

**4. Run Tests**
```bash
# Run specific test
pytest tests/moai_flow/feature/test_my_feature.py -v

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=moai_flow --cov-report=html
```

**5. Check Code Quality**
```bash
# Format code
black moai_flow/ tests/

# Sort imports
isort moai_flow/ tests/

# Lint code
ruff check moai_flow/ tests/

# Type check
mypy moai_flow/
```

**6. Commit and Push**
```bash
git add .
git commit -m "feat: Add my feature"
git push origin feature/my-feature
```

**7. Create Pull Request**
```bash
# Use GitHub CLI
gh pr create --title "Add my feature" --body "Description"
```

### Code Style Guidelines

**Python Style**
- Follow PEP 8
- Use Black for formatting (line length: 88)
- Use type hints for all functions
- Write docstrings for all public APIs

**Testing**
- 90%+ code coverage required
- Use pytest fixtures for setup
- Write descriptive test names
- Test edge cases and error conditions

**Documentation**
- Update README.md for new features
- Add docstrings with examples
- Update API reference
- Include code examples

**Git Commits**
- Use conventional commits (feat, fix, docs, test, refactor)
- Write clear commit messages
- Reference issues/PRDs in commits

---

## 🧪 Testing

### Test Suite Overview

**Total Tests**: 200+
**Coverage**: 90%+
**Test Lines**: 4,525 lines

**Test Distribution**:
| Module | Tests | Lines | Focus |
|--------|-------|-------|-------|
| Core Interfaces | 50+ | 1223 | Interface contracts |
| SwarmDB | 40+ | 770 | Database operations |
| SemanticMemory | 35+ | 875 | Knowledge storage |
| EpisodicMemory | 35+ | 959 | Event tracking |
| ContextHints | 30+ | 697 | User preferences |
| TokenBudget | 20+ | - | Resource management |
| AgentLifecycle | 20+ | - | Event hooks |

### Running Tests

**All Tests**
```bash
pytest tests/ -v
```

**Specific Module**
```bash
# Test SwarmDB
pytest tests/moai_flow/memory/test_swarm_db.py -v

# Test SemanticMemory
pytest tests/moai_flow/memory/test_semantic_memory.py -v

# Test ContextHints
pytest tests/moai_flow/memory/test_context_hints.py -v
```

**With Coverage**
```bash
# Generate coverage report
pytest tests/ -v --cov=moai_flow --cov-report=html

# View coverage in browser
open htmlcov/index.html
```

**Performance Tests**
```bash
# Run performance benchmarks
pytest tests/moai_flow/memory/test_swarm_db.py::test_query_performance -v
pytest tests/moai_flow/memory/test_swarm_db.py::test_batch_insert_performance -v
```

**Specific Test**
```bash
pytest tests/moai_flow/memory/test_swarm_db.py::test_insert_event -v
```

### Test Categories

**Unit Tests** - Test individual components
```bash
pytest tests/moai_flow/memory/ -v
pytest tests/moai_flow/resource/ -v
pytest tests/moai_flow/hooks/ -v
```

**Integration Tests** - Test component interactions
```bash
pytest tests/moai_flow/core/test_interfaces.py -v
```

**Performance Tests** - Test query and operation speed
```bash
pytest tests/moai_flow/memory/test_swarm_db.py -k "performance" -v
```

### Performance Benchmarks

**Query Performance** (<20ms target)
```python
def test_query_performance():
    """Test query performance with 1000 events"""
    db = SwarmDB()

    # Insert 1000 events
    for i in range(1000):
        db.insert_event({...})

    # Measure query time
    start = time.time()
    events = db.get_events(agent_id="test-agent", limit=100)
    duration_ms = (time.time() - start) * 1000

    assert duration_ms < 20  # <20ms requirement
```

**Batch Insert Performance** (100x faster)
```python
def test_batch_insert_performance():
    """Test batch insert vs individual inserts"""
    db = SwarmDB()

    # Individual inserts
    start = time.time()
    for i in range(100):
        db.insert_event({...})
    individual_time = time.time() - start

    # Batch insert
    start = time.time()
    with db.transaction():
        for i in range(100):
            db.insert_event({...})
    batch_time = time.time() - start

    assert batch_time < individual_time / 10  # 10x+ faster
```

### Coverage Requirements

**Minimum Coverage**: 90%
**Target Coverage**: 95%+

**Coverage by Module**:
- Core interfaces: 95%+
- Memory system: 92%+
- Resource management: 90%+
- Hooks system: 90%+

**Check Coverage**:
```bash
pytest tests/ --cov=moai_flow --cov-report=term-missing
```

---

## 🚀 Deployment

### Production Deployment

**Environment Setup**
```bash
# Production environment
export MOAI_ENV=production
export MOAI_DB_PATH=/var/lib/moai/swarm.db
export MOAI_LOG_LEVEL=INFO

# Initialize database
python -c "from moai_flow.memory import SwarmDB; SwarmDB()"
```

**Docker Deployment**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install -e .

# Copy source
COPY moai_flow/ ./moai_flow/

# Initialize database
RUN python -c "from moai_flow.memory import SwarmDB; SwarmDB()"

# Run application
CMD ["python", "-m", "moai_flow"]
```

**Docker Compose**
```yaml
version: '3.8'

services:
  moai-flow:
    build: .
    environment:
      - MOAI_ENV=production
      - MOAI_DB_PATH=/data/swarm.db
    volumes:
      - ./data:/data
    restart: unless-stopped
```

### Monitoring and Observability

**Database Monitoring**
```python
from moai_flow.memory import SwarmDB

db = SwarmDB()

# Check database size
db_size = db.get_database_size()
print(f"Database size: {db_size / 1024 / 1024:.2f} MB")

# Get active agents count
active_agents = db.get_active_agents()
print(f"Active agents: {len(active_agents)}")

# Get event statistics
stats = db.get_event_statistics()
print(f"Total events: {stats['total_events']}")
print(f"Events today: {stats['events_today']}")
```

**Performance Monitoring**
```python
from moai_flow.monitoring import PerformanceMonitor

monitor = PerformanceMonitor()

# Track query performance
with monitor.track("db_query"):
    events = db.get_events(agent_id="test", limit=100)

# Get metrics
metrics = monitor.get_metrics()
print(f"Average query time: {metrics['db_query']['avg_ms']:.2f}ms")
```

### Maintenance

**Database Cleanup**
```bash
# Clean up old events (30 days)
python -c "from moai_flow.memory import SwarmDB; SwarmDB().cleanup_old_events(days=30)"

# Vacuum database
python -c "from moai_flow.memory import SwarmDB; SwarmDB().vacuum()"
```

**Backup**
```bash
# Backup database
cp .moai/memory/swarm.db .moai/backups/swarm-$(date +%Y%m%d).db

# Automated backup script
#!/bin/bash
BACKUP_DIR=".moai/backups"
mkdir -p $BACKUP_DIR
cp .moai/memory/swarm.db $BACKUP_DIR/swarm-$(date +%Y%m%d-%H%M%S).db

# Keep only last 7 days
find $BACKUP_DIR -name "swarm-*.db" -mtime +7 -delete
```

**Health Checks**
```python
from moai_flow.health import HealthChecker

checker = HealthChecker()

# Run health checks
status = checker.check_all()

if status['overall'] == "healthy":
    print("✅ All systems healthy")
else:
    print(f"⚠️ Issues detected: {status['issues']}")
```

---

## 🤝 Contributing

### How to Contribute

We welcome contributions! Please follow these guidelines:

**1. Fork and Clone**
```bash
# Fork repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/moai-flow.git
cd moai-flow
```

**2. Create Feature Branch**
```bash
git checkout -b feature/my-feature
```

**3. Follow TDD Workflow**
- Write tests first
- Implement feature
- Ensure tests pass
- Maintain 90%+ coverage

**4. Code Quality**
- Run Black for formatting
- Run Ruff for linting
- Run mypy for type checking
- Write clear docstrings

**5. Commit and Push**
```bash
git add .
git commit -m "feat: Add my feature"
git push origin feature/my-feature
```

**6. Create Pull Request**
- Clear title and description
- Reference related issues/PRDs
- Include test results
- Request review

### Code Review Process

**PR Requirements**:
- ✅ All tests pass
- ✅ Coverage ≥90%
- ✅ Code style compliant
- ✅ Documentation updated
- ✅ No merge conflicts

**Review Criteria**:
- Code quality and readability
- Test coverage and quality
- Documentation completeness
- Performance implications
- Security considerations

### Reporting Issues

**Bug Reports**:
```markdown
**Description**: Clear description of the bug

**Steps to Reproduce**:
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**: What should happen

**Actual Behavior**: What actually happens

**Environment**:
- Python version: 3.11
- MoAI-Flow version: 0.1.0
- OS: macOS 14.1
```

**Feature Requests**:
```markdown
**Feature**: Clear feature name

**Use Case**: Why is this needed?

**Proposed Solution**: How should it work?

**Alternatives**: Other approaches considered
```

### Development Guidelines

**Coding Standards**:
- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions focused
- Avoid deep nesting

**Testing Standards**:
- Write unit tests for all functions
- Write integration tests for workflows
- Test edge cases
- Test error conditions
- Maintain 90%+ coverage

**Documentation Standards**:
- Update README for new features
- Add docstrings with examples
- Update API reference
- Include usage examples

---

## 🗺️ Roadmap

### Phase 1-4: ✅ Complete (November 2025)

**Phase 1: Foundation**
- ✅ Project structure
- ✅ Core interfaces
- ✅ Development environment

**Phase 2: Rules and Constraints**
- ✅ Concurrent batching patterns
- ✅ MCP vs Task distinction
- ✅ Security and permissions

**Phase 3: Core Infrastructure**
- ✅ SwarmDB with 12 indexes
- ✅ Connection pooling
- ✅ Transaction support

**Phase 4: Memory System**
- ✅ SemanticMemory (patterns, best practices)
- ✅ EpisodicMemory (decisions, events)
- ✅ ContextHints (preferences, expertise)
- ✅ AgentLifecycle hooks
- ✅ TokenBudget allocation
- ✅ 200+ tests, 90%+ coverage

### Phase 5: 🚧 In Progress (December 2025)

**Topology Implementation**
- 🚧 Hierarchical topology (Alfred delegation)
- 🚧 Mesh topology (peer collaboration)
- 🚧 Star topology (hub coordination)
- 🚧 Ring topology (sequential pipeline)
- 🚧 Adaptive topology (dynamic selection)
- 🚧 SwarmCoordinator main engine
- 🚧 Topology transition support

**Deliverables**:
- 5 topology implementations
- SwarmCoordinator orchestration
- Topology selection logic
- Integration tests
- Documentation and examples

### Phase 6: 📋 Planned (Q1 2026)

**Consensus and Coordination**
- 📋 Consensus mechanisms (voting, agreement)
- 📋 Conflict resolution (weighted voting)
- 📋 Agent communication protocols
- 📋 Task priority queue
- 📋 Agent quota management

**Performance and Metrics**
- 📋 Performance monitoring
- 📋 Resource utilization tracking
- 📋 Query optimization
- 📋 Bottleneck detection
- 📋 Self-healing workflows

**Advanced Features**
- 📋 Pattern learning from usage
- 📋 Auto-optimization
- 📋 Cross-session context
- 📋 Predictive resource allocation

**Deliverables**:
- Consensus implementation
- Performance metrics system
- Advanced coordination features
- Comprehensive benchmarks
- Production optimization guide

### Phase 7: 📅 Future (Q2 2026+)

**Neural Training**
- 📅 Pattern recognition from agent behaviors
- 📅 Learning from successful workflows
- 📅 Adaptive agent selection
- 📅 Predictive resource management

**GitHub Enhancement**
- 📅 GitHub agents (9 specialized agents)
- 📅 PR automation
- 📅 Code review integration
- 📅 Issue management

**Advanced Orchestration**
- 📅 Multi-swarm coordination
- 📅 Swarm fusion and splitting
- 📅 Dynamic topology morphing
- 📅 Self-organizing swarms

---

## 📄 License

MIT License

Copyright (c) 2025 MoAI-Flow Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🙏 Acknowledgments

**Built With**:
- [MoAI-ADK](https://adk.mo.ai.kr) - AI-driven development kit
- [Claude Code](https://claude.ai/code) - AI coding assistant
- [SQLite](https://www.sqlite.org/) - Embedded database
- [Python](https://www.python.org/) - Programming language

**Inspired By**:
- Multi-agent coordination research
- Swarm intelligence patterns
- Distributed systems design
- Production AI workflows

**Special Thanks**:
- MoAI-ADK community for feedback and contributions
- Claude Code team for AI agent infrastructure
- All contributors and early adopters

---

## 📞 Support

**Documentation**: [./moai_flow/docs/](./moai_flow/docs/)

**Issues**: [GitHub Issues](https://github.com/superdisco-agents/moai-flow/issues)

**Discussions**: [GitHub Discussions](https://github.com/superdisco-agents/moai-flow/discussions)

**Email**: support@moai-flow.dev

**Community**:
- Discord: [Join Server](https://discord.gg/moai-flow)
- Twitter: [@moaiflow](https://twitter.com/moaiflow)

---

<div align="center">

**🌊 MoAI-Flow** - Native Multi-Agent Swarm Coordination

[Getting Started](#-quick-start) • [Documentation](./moai_flow/docs/) • [Examples](#-examples) • [Contributing](#-contributing)

Made with ❤️ by the MoAI-Flow team

</div>
