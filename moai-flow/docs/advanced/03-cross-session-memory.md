# Cross-Session Memory

> Persistent context across Claude Code sessions

## Overview

Cross-session memory enables agents to remember context, preferences, and learnings across multiple sessions. **MoAI has partial support** through session state saving.

---

## Memory Types

### 1. Short-Term Memory

Within-session context (both systems have this):

```
Session Start → Context Building → Task Execution → Session End
                     ▲                   │
                     └───────────────────┘
                        (within session)
```

### 2. Long-Term Memory

Cross-session persistence:

```
Session 1 → Save State → [Gap] → Session 2 → Load State
                │                      ▲
                └──────────────────────┘
                    (persisted data)
```

### 3. Semantic Memory

Learned concepts and relationships:

```json
{
  "concepts": {
    "project_architecture": "layered",
    "coding_style": "explicit",
    "test_framework": "pytest",
    "api_pattern": "REST"
  }
}
```

### 4. Episodic Memory

Specific events and interactions:

```json
{
  "episodes": [
    {
      "date": "2025-11-28",
      "task": "Refactored authentication",
      "outcome": "success",
      "files_changed": ["src/auth.py", "tests/test_auth.py"]
    }
  ]
}
```

---

## MoAI-Flow Memory System

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   MEMORY SYSTEM                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   Working   │    │   Short     │    │    Long     │ │
│  │   Memory    │◄──►│    Term     │◄──►│    Term     │ │
│  │  (active)   │    │  (session)  │    │ (persisted) │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Memory Index                        │   │
│  │  • Semantic search                              │   │
│  │  • Relevance scoring                            │   │
│  │  • Context retrieval                            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Memory Operations

```javascript
// Store memory
mcp__moai-flow__memory_store {
  key: "project_preferences",
  value: {
    style: "explicit",
    testing: "tdd",
    framework: "fastapi"
  },
  ttl: null  // permanent
}

// Retrieve memory
mcp__moai-flow__memory_get {
  key: "project_preferences"
}

// Search memory
mcp__moai-flow__memory_search {
  query: "authentication implementation",
  limit: 5
}

// Memory usage stats
mcp__moai-flow__memory_usage {}
```

---

## MoAI Current State

### Session State Saving

MoAI saves session state:

```json
{
  "session_end": {
    "work_state": {
      "enabled": true,
      "save_location": ".moai/memory/last-session-state.json"
    }
  }
}
```

### Last Session State Format

```json
{
  "session_id": "abc123",
  "ended_at": "2025-11-29T12:00:00Z",
  "duration_seconds": 7200,
  "working_directory": "/path/to/project",
  "last_files": ["src/main.py", "tests/test_main.py"],
  "pending_todos": []
}
```

### Configuration Memory

MoAI persists preferences in config:

```json
{
  "user": {
    "name": "John"
  },
  "language": {
    "conversation_language": "ko"
  },
  "constitution": {
    "enforce_tdd": true,
    "test_coverage_target": 90
  }
}
```

---

## Comparison

| Feature | MoAI-Flow | MoAI |
|---------|-------------|------|
| Session State | Yes | Yes |
| Working Memory | Yes | Yes |
| Long-Term Storage | Yes | Partial |
| Semantic Memory | Yes | No |
| Episodic Memory | Yes | No |
| Memory Search | Yes | No |
| Memory Index | Yes | No |
| TTL Support | Yes | No |
| Memory Stats | Yes | No |

---

## Memory Types Comparison

### MoAI-Flow Memory Categories

```
┌────────────────────────────────────┐
│          MoAI-Flow Memory        │
├────────────────────────────────────┤
│ • Working Memory (active context)  │
│ • Short-Term (within session)      │
│ • Long-Term (cross-session)        │
│ • Semantic (concepts)              │
│ • Episodic (events)                │
│ • Procedural (how-to patterns)     │
│ • Agent Memory (per-agent state)   │
│ • Swarm Memory (shared state)      │
└────────────────────────────────────┘
```

### MoAI Memory Categories

```
┌────────────────────────────────────┐
│            MoAI Memory             │
├────────────────────────────────────┤
│ • Working Memory (active context)  │
│ • Session State (last-session)     │
│ • Config Preferences               │
│ • SPEC Documents (project memory)  │
│                                    │
│ Missing:                           │
│ • Semantic Memory                  │
│ • Episodic Memory                  │
│ • Agent Memory                     │
│ • Memory Search                    │
└────────────────────────────────────┘
```

---

## Implementation Options

### Option 1: Enhance Session State

Extend MoAI's session state with more context:

```json
{
  "session_end": {
    "work_state": {
      "enabled": true,
      "save_location": ".moai/memory/last-session-state.json",
      "include_context_hints": true,
      "include_recent_tasks": true,
      "include_file_history": true
    }
  }
}
```

### Option 2: Add Memory Directory

Create dedicated memory storage:

```
.moai/memory/
├── last-session-state.json
├── context-hints.json
├── learned-patterns.json
├── project-knowledge.json
└── episodes/
    ├── 2025-11-28.json
    └── 2025-11-29.json
```

### Option 3: Add Memory Agent

Create a memory management agent:

```yaml
name: manager-memory
description: Cross-session memory management

capabilities:
  - Store context
  - Retrieve relevant memory
  - Index project knowledge
  - Track episodes
```

---

## Proposed MoAI Memory System

### Memory Structure

```json
{
  "memory": {
    "enabled": true,
    "storage_path": ".moai/memory/",
    "types": {
      "session_state": {
        "enabled": true,
        "retention_days": 30
      },
      "context_hints": {
        "enabled": true,
        "max_hints": 100
      },
      "project_knowledge": {
        "enabled": true,
        "auto_update": true
      },
      "episodes": {
        "enabled": true,
        "retention_days": 90
      }
    }
  }
}
```

### Context Hints Format

```json
{
  "hints": [
    {
      "type": "preference",
      "key": "code_style",
      "value": "explicit",
      "confidence": 0.95,
      "source": "user_correction"
    },
    {
      "type": "pattern",
      "key": "api_route_structure",
      "value": "/api/v1/{resource}",
      "confidence": 0.88,
      "source": "observed"
    }
  ]
}
```

### Project Knowledge Format

```json
{
  "knowledge": {
    "architecture": "layered",
    "frameworks": ["FastAPI", "React"],
    "testing": {
      "framework": "pytest",
      "coverage_target": 90
    },
    "code_patterns": {
      "naming": "snake_case",
      "imports": "grouped"
    },
    "key_files": {
      "entry_point": "src/main.py",
      "config": "pyproject.toml"
    }
  }
}
```

---

## Recommendation

### Priority: P2 (Medium)

Cross-session memory enhances user experience significantly.

### Phase 1: Enhance Session State (Week 1)

```json
{
  "session_end": {
    "work_state": {
      "include_context_hints": true,
      "include_recent_tasks": true
    }
  }
}
```

### Phase 2: Add Context Hints (Week 2)

```json
{
  "memory": {
    "context_hints": {
      "enabled": true,
      "load_on_session_start": true
    }
  }
}
```

### Phase 3: Add Project Knowledge (Week 3-4)

```json
{
  "memory": {
    "project_knowledge": {
      "enabled": true,
      "auto_detect": true
    }
  }
}
```

### Phase 4: Add Episodes (Month 2)

```json
{
  "memory": {
    "episodes": {
      "enabled": true,
      "track_major_changes": true
    }
  }
}
```

---

## Summary

Cross-session memory is crucial for continuity. MoAI has basic session state saving but lacks the rich memory capabilities of MoAI-Flow. Enhancing MoAI's memory system would improve user experience and enable smarter agent behavior over time. This is a medium-priority enhancement that builds on existing infrastructure.
