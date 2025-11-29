# Cross-Session Memory System

> Persistent memory for adaptive multi-agent coordination across sessions

## Overview

MoAI-Flow's cross-session memory system enables agents to learn from past sessions, maintain context across restarts, and build cumulative knowledge about projects and workflows. This creates adaptive systems that improve over time and provide seamless continuity between sessions.

**Key Capabilities**:
- Session-scoped preference tracking (ContextHints)
- Project-wide semantic knowledge (SemanticMemory)
- Cross-session event history (EpisodicMemory)
- Automatic context loading at session start
- Persistent memory with intelligent pruning

---

## Memory Hierarchy

MoAI-Flow implements a three-tiered memory hierarchy, each optimized for different time scales and use cases.

### 1. ContextHints (Session-Scoped)

**Purpose**: Track user preferences and adaptive patterns within and across sessions

**Lifetime**: Persists across sessions, continuously refined by user interactions

**Storage**: `.moai/memory/context-hints.json`

**Example**:

```json
{
  "hints": [
    {
      "type": "preference",
      "key": "code_style",
      "value": "explicit",
      "confidence": 0.95,
      "source": "user_correction",
      "learned_at": "2025-11-28T14:30:00Z",
      "last_used": "2025-11-29T10:15:00Z",
      "frequency": 12
    },
    {
      "type": "pattern",
      "key": "api_route_prefix",
      "value": "/api/v1",
      "confidence": 0.88,
      "source": "observed",
      "learned_at": "2025-11-25T09:00:00Z",
      "last_used": "2025-11-29T11:20:00Z",
      "frequency": 45
    },
    {
      "type": "preference",
      "key": "test_framework",
      "value": "pytest",
      "confidence": 0.92,
      "source": "config_analysis",
      "learned_at": "2025-11-20T16:00:00Z",
      "last_used": "2025-11-29T09:30:00Z",
      "frequency": 23
    },
    {
      "type": "style",
      "key": "import_order",
      "value": "stdlib,third-party,local",
      "confidence": 0.87,
      "source": "observed",
      "learned_at": "2025-11-24T13:45:00Z",
      "last_used": "2025-11-29T10:00:00Z",
      "frequency": 8
    }
  ]
}
```

**Usage Example** (Alfred loading preferences):

```javascript
// SessionStart Hook
function load_context_hints() {
  const hints = read_file(".moai/memory/context-hints.json");

  for (const hint of hints.hints) {
    // Apply hint to agent configuration
    if (hint.type === "preference") {
      agent_config[hint.key] = hint.value;
    }

    // Adjust verbosity based on frequency
    if (hint.frequency > 20) {
      agent_config.verbose = true;
    }
  }

  return hints;
}
```

### 2. SemanticMemory (Project-Scoped)

**Purpose**: Long-term knowledge and best practices about the project

**Lifetime**: Permanent (with confidence-based pruning when confidence < 0.6)

**Storage**: `.moai/memory/project-knowledge.json`

**Contains**:

```json
{
  "knowledge": {
    "architecture": {
      "pattern": "layered",
      "confidence": 0.95,
      "description": "Three-tier architecture with API, service, and data layers",
      "learned_at": "2025-11-15T10:00:00Z",
      "references": [
        "src/api/main.py",
        "src/services/core.py",
        "src/data/models.py"
      ]
    },
    "frameworks": {
      "web": {
        "name": "FastAPI",
        "version": "0.104.1",
        "confidence": 0.98,
        "learned_at": "2025-11-15T10:05:00Z"
      },
      "testing": {
        "name": "pytest",
        "version": "7.4.0",
        "confidence": 0.96,
        "learned_at": "2025-11-15T10:10:00Z"
      },
      "database": {
        "name": "PostgreSQL",
        "version": "15.0",
        "confidence": 0.92,
        "learned_at": "2025-11-20T14:00:00Z"
      }
    },
    "code_patterns": {
      "naming_convention": {
        "style": "snake_case",
        "scope": "global",
        "confidence": 0.97,
        "exceptions": []
      },
      "class_structure": {
        "pattern": "dataclass_with_validators",
        "confidence": 0.85,
        "examples": ["src/models/user.py", "src/models/product.py"]
      },
      "error_handling": {
        "pattern": "custom_exceptions_with_logging",
        "confidence": 0.89,
        "examples": ["src/exceptions.py"]
      }
    },
    "testing": {
      "framework": "pytest",
      "coverage_target": 90,
      "structure": "tests/ parallel to src/",
      "naming": "test_*.py",
      "confidence": 0.93
    },
    "key_files": {
      "entry_point": {
        "path": "src/main.py",
        "confidence": 0.99,
        "description": "Application entry point"
      },
      "config": {
        "path": "pyproject.toml",
        "confidence": 0.99,
        "description": "Project configuration"
      },
      "requirements": {
        "path": "pyproject.toml",
        "confidence": 0.99,
        "description": "Dependency management"
      }
    },
    "deployment": {
      "target": "docker",
      "confidence": 0.87,
      "config_file": "Dockerfile",
      "orchestration": "kubernetes",
      "confidence": 0.75
    }
  }
}
```

**Query Example**:

```javascript
// Agent needing to know project architecture
function get_architecture_knowledge() {
  const knowledge = read_knowledge(".moai/memory/project-knowledge.json");

  // Get high-confidence architectural patterns
  if (knowledge.architecture.confidence > 0.9) {
    return {
      pattern: knowledge.architecture.pattern,
      description: knowledge.architecture.description,
      references: knowledge.architecture.references
    };
  }
}
```

### 3. EpisodicMemory (Cross-Session)

**Purpose**: Detailed event and decision history for learning from specific sessions

**Lifetime**: Permanent (with archival to yearly compressed files after 90 days)

**Storage**:
- Active: `.moai/memory/episodes/`
- Archived: `.moai/memory/episodes/archive/`

**Episode Structure**:

```json
{
  "episode": {
    "id": "EP-2025-11-29-001",
    "session_id": "sess-abc123",
    "date": "2025-11-29",
    "task": "Implement user authentication",
    "status": "success",
    "duration_seconds": 3600,
    "tokens_used": 45000,
    "outcome": {
      "success": true,
      "quality": "high",
      "rework_needed": false
    },
    "files_changed": [
      "src/auth/handlers.py",
      "src/auth/models.py",
      "tests/test_auth_handlers.py",
      "tests/test_auth_models.py"
    ],
    "agents_involved": [
      "expert-backend",
      "expert-database",
      "manager-tdd"
    ],
    "key_decisions": [
      {
        "decision": "Use JWT with refresh tokens",
        "reasoning": "Stateless auth, better scalability",
        "alternatives_rejected": ["Session-based auth", "OAuth2 delegation"],
        "confidence": 0.95
      },
      {
        "decision": "Hash passwords with argon2",
        "reasoning": "Modern, memory-hard algorithm",
        "confidence": 0.98
      }
    ],
    "errors_encountered": [
      {
        "error": "Token expiration not handled",
        "resolution": "Added refresh token endpoint",
        "recovery_time_ms": 450,
        "prevention": "Add token endpoint validation in tests"
      }
    ],
    "patterns_observed": [
      "jwt_implementation",
      "password_hashing",
      "token_refresh"
    ],
    "insights": [
      "User model refactoring improved auth clarity",
      "Test-first approach caught edge cases early"
    ],
    "metadata": {
      "complexity": "high",
      "risk_level": "medium",
      "similar_past_episodes": ["EP-2025-11-15-003", "EP-2025-11-10-002"]
    }
  }
}
```

**Retrieval Example** (Finding similar past episodes):

```javascript
// Find similar episodes for learning
function find_similar_episodes(task_type, complexity) {
  const episodes = load_episodes(".moai/memory/episodes/");

  const similar = episodes.filter(ep => {
    return ep.task.includes(task_type) &&
           ep.metadata.complexity === complexity;
  });

  return similar
    .sort((a, b) => compare_similarity(a, b))
    .slice(0, 5);  // Top 5 most similar
}
```

---

## Integration with Hooks

The memory system integrates deeply with MoAI-Flow's hook lifecycle, enabling automatic context loading and persistence.

### SessionStart Hook

**When**: Triggered at the beginning of a new session

**Actions**:

```bash
#!/bin/bash
# session-start.sh
#
# Load cross-session memory and initialize agent context

SESSION_ID="$1"
USER_ID="$2"

# 1. Create session directory
SESSION_DIR=".moai/sessions/$SESSION_ID"
mkdir -p "$SESSION_DIR"

# 2. Load context hints from previous sessions
HINTS_FILE=".moai/memory/context-hints.json"
if [[ -f "$HINTS_FILE" ]]; then
    # Copy to session-specific cache for fast lookup
    cp "$HINTS_FILE" "$SESSION_DIR/context-hints-cache.json"
    echo "Context hints loaded: $(jq '.hints | length' "$HINTS_FILE") preferences"
fi

# 3. Load project knowledge
KNOWLEDGE_FILE=".moai/memory/project-knowledge.json"
if [[ -f "$KNOWLEDGE_FILE" ]]; then
    cp "$KNOWLEDGE_FILE" "$SESSION_DIR/project-knowledge-cache.json"

    # Extract key info for display
    ARCH=$(jq -r '.knowledge.architecture.pattern' "$KNOWLEDGE_FILE")
    FRAMEWORKS=$(jq -r '.knowledge.frameworks | keys | join(", ")' "$KNOWLEDGE_FILE")
    echo "Project Knowledge: Architecture=$ARCH, Frameworks=$FRAMEWORKS"
fi

# 4. Load last session state
LAST_STATE=".moai/memory/last-session-state.json"
if [[ -f "$LAST_STATE" ]]; then
    cp "$LAST_STATE" "$SESSION_DIR/inherited-state.json"

    # Display continuity info
    PREV_FILES=$(jq -r '.context.last_files | join(", ")' "$LAST_STATE")
    echo "Resuming from previous work with files: $PREV_FILES"
fi

# 5. Initialize memory index for fast lookup
python3 << 'PYTHON_EOF'
import json
from pathlib import Path

# Build memory index for semantic search
memory_dir = Path(".moai/memory")
index = {
    "context_hints": {},
    "semantic_memory": {},
    "episodes": {}
}

# Index context hints by type and key
hints_file = memory_dir / "context-hints.json"
if hints_file.exists():
    hints = json.load(hints_file.open())
    for hint in hints.get("hints", []):
        key = f"{hint['type']}:{hint['key']}"
        index["context_hints"][key] = hint

# Save index for fast lookups
index_file = Path(f".moai/sessions/{SESSION_ID}/memory-index.json")
index_file.write_text(json.dumps(index, indent=2))
PYTHON_EOF

echo "Memory system initialized"
exit 0
```

**Result**:
- Context hints loaded into agent configuration
- Project knowledge available for semantic queries
- Previous session state visible for context continuity
- Memory index built for fast lookups

### SessionEnd Hook

**When**: Triggered at the end of a session

**Actions**:

```bash
#!/bin/bash
# session-end.sh
#
# Persist memory from current session for future use

SESSION_ID="$1"
DURATION="$2"
STATUS="$3"  # success/failure/incomplete

SESSION_DIR=".moai/sessions/$SESSION_ID"

# 1. Save session state for rapid resume
STATE_FILE=".moai/memory/last-session-state.json"
cat > "$STATE_FILE" << EOF
{
  "session_id": "$SESSION_ID",
  "ended_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "duration_seconds": $DURATION,
  "status": "$STATUS",
  "working_directory": "$(pwd)"
}
EOF

# 2. Extract and update context hints from session
python3 << 'PYTHON_EOF'
import json
from pathlib import Path
from datetime import datetime

SESSION_ID = "$SESSION_ID"
session_dir = Path(f".moai/sessions/{SESSION_ID}")

# Load current hints
hints_file = Path(".moai/memory/context-hints.json")
hints_data = {"hints": []}

if hints_file.exists():
    hints_data = json.load(hints_file.open())

# Load session events/decisions
session_events = session_dir / "events.json"
if session_events.exists():
    events = json.load(session_events.open())

    for event in events.get("preferences_observed", []):
        # Add or update hint
        matching_hint = next(
            (h for h in hints_data["hints"]
             if h["key"] == event["key"] and h["type"] == event["type"]),
            None
        )

        if matching_hint:
            # Update existing hint
            matching_hint["frequency"] += 1
            matching_hint["last_used"] = datetime.now().isoformat() + "Z"
            matching_hint["confidence"] = min(0.99, matching_hint["confidence"] + 0.02)
        else:
            # Add new hint
            hints_data["hints"].append({
                "type": event["type"],
                "key": event["key"],
                "value": event["value"],
                "confidence": 0.70,
                "source": "observed",
                "learned_at": datetime.now().isoformat() + "Z",
                "last_used": datetime.now().isoformat() + "Z",
                "frequency": 1
            })

# Save updated hints
hints_file.write_text(json.dumps(hints_data, indent=2))
PYTHON_EOF

# 3. Archive completed episodes
python3 << 'PYTHON_EOF'
import json
from pathlib import Path
from datetime import datetime

SESSION_ID = "$SESSION_ID"
session_dir = Path(f".moai/sessions/{SESSION_ID}")

# Load completed tasks/episodes
session_log = session_dir / "session.log"
if session_log.exists():
    # Parse session log and create episode
    episode = {
        "id": f"EP-{datetime.now().strftime('%Y-%m-%d')}-{SESSION_ID[:6]}",
        "session_id": SESSION_ID,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "status": "$STATUS",
        "duration_seconds": $DURATION,
        "agents_involved": [],
        "files_changed": [],
        "key_decisions": [],
        "outcomes": []
    }

    # Store in episodes directory
    episodes_dir = Path(".moai/memory/episodes")
    episodes_dir.mkdir(parents=True, exist_ok=True)

    episode_file = episodes_dir / f"{episode['id']}.json"
    episode_file.write_text(json.dumps({"episode": episode}, indent=2))

PYTHON_EOF

echo "Memory persisted for future sessions"
exit 0
```

**Result**:
- Session state saved for immediate recall
- Context hints updated with new observations
- Completed tasks archived as episodes
- Memory available for next session

---

## Storage Architecture

The memory system uses a hierarchical file structure optimized for quick access and long-term retention.

### File Structure

```
.moai/memory/
├── context-hints.json          # Active preferences (session-level)
├── project-knowledge.json      # Semantic knowledge (project-level)
├── episodes/
│   ├── EP-2025-11-29-001.json  # Individual episode
│   ├── EP-2025-11-29-002.json
│   ├── EP-2025-11-28-001.json
│   └── archive/
│       ├── episodes-2025-11.tar.gz  # Compressed monthly archive
│       └── episodes-2025-10.tar.gz
├── indexes/
│   ├── semantic-index.json     # Quick lookup: concept→episodes
│   ├── pattern-index.json      # Quick lookup: pattern→occurrences
│   └── error-patterns.json     # Quick lookup: error→resolutions
└── last-session-state.json     # Previous session metadata
```

### SQLite Schema (Optional)

For large projects with 1000+ episodes, SQLite provides better performance:

```sql
-- Memory database schema
CREATE TABLE context_hints (
  id INTEGER PRIMARY KEY,
  type TEXT NOT NULL,
  key TEXT NOT NULL,
  value TEXT NOT NULL,
  confidence REAL NOT NULL,
  source TEXT,
  learned_at TIMESTAMP,
  last_used TIMESTAMP,
  frequency INTEGER DEFAULT 1,
  UNIQUE(type, key)
);

CREATE TABLE semantic_concepts (
  id INTEGER PRIMARY KEY,
  concept TEXT UNIQUE NOT NULL,
  category TEXT,
  confidence REAL,
  references TEXT,  -- JSON array of file references
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE episodes (
  id TEXT PRIMARY KEY,
  session_id TEXT,
  date DATE,
  task TEXT,
  status TEXT,
  duration_seconds INTEGER,
  outcome TEXT,
  files_changed TEXT,  -- JSON array
  agents_involved TEXT,  -- JSON array
  patterns_observed TEXT,  -- JSON array
  created_at TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE decisions (
  id INTEGER PRIMARY KEY,
  episode_id TEXT,
  decision TEXT,
  reasoning TEXT,
  alternatives TEXT,  -- JSON array
  confidence REAL,
  created_at TIMESTAMP,
  FOREIGN KEY (episode_id) REFERENCES episodes(id)
);

CREATE TABLE error_patterns (
  id INTEGER PRIMARY KEY,
  error_type TEXT,
  error_message TEXT,
  resolution TEXT,
  success_rate REAL,
  occurrences INTEGER,
  last_seen TIMESTAMP,
  UNIQUE(error_type, resolution)
);

-- Indexes for performance
CREATE INDEX idx_hints_type ON context_hints(type);
CREATE INDEX idx_hints_confidence ON context_hints(confidence DESC);
CREATE INDEX idx_concepts_category ON semantic_concepts(category);
CREATE INDEX idx_episodes_date ON episodes(date DESC);
CREATE INDEX idx_episodes_status ON episodes(status);
CREATE INDEX idx_patterns_frequency ON error_patterns(occurrences DESC);
```

### Query Optimization

**Memory Load Time**: <50ms (index-based)

```python
# Fast context hint lookup
def get_context_hint(hint_type: str, key: str) -> Optional[Dict]:
    with sqlite3.connect(".moai/memory/memory.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM context_hints WHERE type = ? AND key = ?",
            (hint_type, key)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
```

**Knowledge Search Time**: <20ms (indexed concepts)

```python
# Fast semantic search
def search_knowledge(concept: str, limit: int = 5) -> List[Dict]:
    with sqlite3.connect(".moai/memory/memory.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM semantic_concepts "
            "WHERE concept LIKE ? "
            "ORDER BY confidence DESC LIMIT ?",
            (f"%{concept}%", limit)
        )
        return [dict(row) for row in cursor.fetchall()]
```

**Pattern Matching Time**: <30ms (indexed patterns)

```python
# Fast error pattern lookup
def find_error_resolution(error_type: str) -> Optional[Dict]:
    with sqlite3.connect(".moai/memory/memory.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM error_patterns "
            "WHERE error_type = ? "
            "ORDER BY success_rate DESC LIMIT 1",
            (error_type,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
```

---

## Use Cases

### 1. Adaptive Communication

How ContextHints allows MoAI-Flow to adjust Alfred's behavior based on user preferences:

**Scenario**: User has corrected code style multiple times in session.

```javascript
// During next session, context hints are loaded
function initialize_alfred_behavior() {
  const hints = load_context_hints();

  // Find style correction hints
  const styleHints = hints.filter(h => h.source === "user_correction");

  if (styleHints.length > 5 && styleHints[0].confidence > 0.9) {
    // User strongly prefers explicit style
    alfred.code_style = "explicit";
    alfred.verbose_output = true;
    alfred.suggestion_level = "aggressive";
  }

  if (user.previous_session_duration < 30 * 60) {
    // User had short sessions - provide shorter output
    alfred.summary_level = "minimal";
  }
}
```

**Result**: Alfred automatically adjusts verbosity, code style, and suggestion frequency based on learned preferences.

### 2. Pattern Learning

How EpisodicMemory enables smarter task execution by finding similar past episodes:

**Scenario**: User asks to "implement authentication" for a new project.

```javascript
function execute_authentication_task() {
  // Find similar past episodes
  const similarEpisodes = find_similar_episodes("authentication", "high");

  if (similarEpisodes.length > 0) {
    const bestEpisode = similarEpisodes[0];

    // Suggest approach from successful past execution
    return {
      suggested_agents: bestEpisode.agents_involved,
      estimated_duration: bestEpisode.duration_seconds,
      key_decisions: bestEpisode.key_decisions,
      known_pitfalls: bestEpisode.errors_encountered,
      references: bestEpisode.files_changed
    };
  }
}
```

**Result**: Task executes faster with better agent selection and avoids known pitfalls.

### 3. Knowledge Retention

How SemanticMemory preserves architectural decisions and prevents regression:

**Scenario**: New agent joins the project (or session resumes months later).

```javascript
function onboard_agent_with_knowledge() {
  const projectKnowledge = load_project_knowledge();

  // Agent learns architecture immediately
  agent.architecture = projectKnowledge.architecture.pattern;
  agent.frameworks = projectKnowledge.frameworks;
  agent.naming_conventions = projectKnowledge.code_patterns.naming_convention;
  agent.testing_strategy = projectKnowledge.testing;

  // Log: Agent initialized with 9 architectural patterns
  log_confidence_summary(projectKnowledge);
}
```

**Confidence Summary Output**:
```
Architecture (0.95):    Layered with API/Service/Data tiers
Frameworks (0.97):     FastAPI, pytest, PostgreSQL
Code Patterns (0.89):   snake_case, dataclass models, custom exceptions
Testing (0.93):         pytest with 90% coverage target
Key Files (0.99):       src/main.py (entry), pyproject.toml (config)
Deployment (0.87):      Docker containerization, Kubernetes orchestration
```

---

## API Reference

### ContextHints API

**Load Context Hints**:

```python
def load_context_hints(session_id: str = None) -> List[Dict]:
    """
    Load context hints for current or specified session.

    Args:
        session_id: Optional specific session. If None, loads active hints.

    Returns:
        List of context hint dictionaries with confidence scores

    Example:
        hints = load_context_hints()
        style_hint = next((h for h in hints if h['key'] == 'code_style'), None)
        if style_hint['confidence'] > 0.85:
            use_style(style_hint['value'])
    """
```

**Store Context Hint**:

```python
def store_context_hint(
    hint_type: str,
    key: str,
    value: Any,
    confidence: float = 0.7,
    source: str = "observed"
) -> str:
    """
    Store a new context hint or update existing.

    Args:
        hint_type: Type of hint (preference, pattern, style, behavior)
        key: Hint key name
        value: Hint value
        confidence: Confidence score (0.0-1.0)
        source: How hint was learned (user_correction, observed, config_analysis)

    Returns:
        Hint ID

    Example:
        store_context_hint(
            "preference",
            "test_framework",
            "pytest",
            confidence=0.95,
            source="config_analysis"
        )
    """
```

**Update Hint Confidence**:

```python
def update_hint_confidence(
    hint_type: str,
    key: str,
    delta: float = 0.02
) -> float:
    """
    Increase confidence when hint is validated (max 0.99).

    Args:
        hint_type: Type of hint
        key: Hint key
        delta: Confidence increase (default 0.02)

    Returns:
        New confidence score

    Example:
        # User confirms preference
        new_conf = update_hint_confidence("preference", "code_style", delta=0.05)
    """
```

**Query Hints by Type**:

```python
def find_hints(
    hint_type: str = None,
    min_confidence: float = 0.7,
    limit: int = 100
) -> List[Dict]:
    """
    Find hints matching criteria.

    Args:
        hint_type: Filter by type (None = all types)
        min_confidence: Minimum confidence threshold
        limit: Maximum results

    Returns:
        List of matching hints sorted by confidence

    Example:
        style_hints = find_hints("preference", min_confidence=0.85)
    """
```

### SemanticMemory API

**Load Project Knowledge**:

```python
def load_project_knowledge() -> Dict:
    """
    Load complete semantic knowledge about project.

    Returns:
        Knowledge dictionary with architecture, frameworks, patterns, etc.

    Example:
        knowledge = load_project_knowledge()
        pattern = knowledge['architecture']['pattern']
    """
```

**Query Semantic Concept**:

```python
def query_concept(
    concept: str,
    category: str = None,
    min_confidence: float = 0.7
) -> Optional[Dict]:
    """
    Query specific semantic concept.

    Args:
        concept: Concept name (e.g., 'api_route_pattern')
        category: Optional category filter
        min_confidence: Minimum confidence threshold

    Returns:
        Concept dictionary or None if not found

    Example:
        concept = query_concept("api_route_pattern", min_confidence=0.85)
        if concept:
            apply_pattern(concept['pattern'])
    """
```

**Store Semantic Knowledge**:

```python
def store_semantic_knowledge(
    concept: str,
    category: str,
    value: Any,
    confidence: float = 0.8,
    references: List[str] = None
) -> str:
    """
    Store semantic knowledge about project.

    Args:
        concept: Concept name
        category: Knowledge category
        value: The knowledge value
        confidence: Confidence score (0.0-1.0)
        references: List of relevant file paths

    Returns:
        Concept ID

    Example:
        store_semantic_knowledge(
            "testing_framework",
            "tools",
            "pytest",
            confidence=0.96,
            references=["pyproject.toml", "tests/"]
        )
    """
```

**Search Knowledge**:

```python
def search_knowledge(
    query: str,
    category: str = None,
    limit: int = 5
) -> List[Dict]:
    """
    Semantic search across project knowledge.

    Args:
        query: Search query
        category: Optional category filter
        limit: Maximum results

    Returns:
        List of matching concepts

    Example:
        results = search_knowledge("authentication", category="patterns")
    """
```

**Prune Low-Confidence Knowledge**:

```python
def prune_knowledge(
    min_confidence_threshold: float = 0.6,
    dry_run: bool = False
) -> Dict:
    """
    Remove knowledge below confidence threshold.

    Args:
        min_confidence_threshold: Prune below this confidence
        dry_run: If True, only report what would be pruned

    Returns:
        Pruning report with count of removed entries

    Example:
        report = prune_knowledge(min_confidence=0.6, dry_run=True)
        print(f"Would remove {report['removed_count']} low-confidence entries")
    """
```

### EpisodicMemory API

**Record Episode**:

```python
def record_episode(
    task: str,
    status: str,
    duration_seconds: int,
    files_changed: List[str],
    agents_involved: List[str],
    key_decisions: List[Dict],
    errors: List[Dict] = None,
    insights: List[str] = None
) -> str:
    """
    Record a completed task episode.

    Args:
        task: Task description
        status: Outcome (success, partial, failure)
        duration_seconds: Task duration
        files_changed: Modified files
        agents_involved: Agents that worked on task
        key_decisions: Important decisions made
        errors: Errors encountered and resolutions
        insights: Lessons learned

    Returns:
        Episode ID

    Example:
        ep_id = record_episode(
            task="Implement user authentication",
            status="success",
            duration_seconds=3600,
            files_changed=["src/auth.py", "tests/test_auth.py"],
            agents_involved=["expert-backend", "manager-tdd"],
            key_decisions=[{
                "decision": "JWT tokens",
                "reasoning": "Stateless auth"
            }]
        )
    """
```

**Find Similar Episodes**:

```python
def find_similar_episodes(
    task_type: str,
    complexity: str = None,
    min_similarity: float = 0.7,
    limit: int = 5
) -> List[Dict]:
    """
    Find episodes similar to current task.

    Args:
        task_type: Type of task
        complexity: Optional complexity level (low, medium, high)
        min_similarity: Minimum similarity score
        limit: Maximum results

    Returns:
        List of similar episodes sorted by similarity

    Example:
        similar = find_similar_episodes(
            "database_migration",
            complexity="high",
            limit=3
        )
        for ep in similar:
            learn_from(ep)
    """
```

**Query Episodes by Date Range**:

```python
def query_episodes(
    start_date: str = None,
    end_date: str = None,
    status: str = None,
    task_pattern: str = None
) -> List[Dict]:
    """
    Query episodes within date range with filters.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        status: Filter by status (success, partial, failure)
        task_pattern: Filter by task pattern

    Returns:
        List of matching episodes

    Example:
        month_episodes = query_episodes(
            start_date="2025-11-01",
            end_date="2025-11-30",
            status="success"
        )
    """
```

**Extract Learning from Episodes**:

```python
def extract_learnings(
    episode_id: str = None,
    task_type: str = None,
    num_episodes: int = 5
) -> Dict:
    """
    Extract learnings and patterns from episodes.

    Args:
        episode_id: Specific episode, or None for patterns across task type
        task_type: If episode_id None, analyze this task type
        num_episodes: Number of episodes to analyze (for patterns)

    Returns:
        Dictionary with extracted patterns, errors, solutions, etc.

    Example:
        learnings = extract_learnings(task_type="api_implementation")
        apply_learnings_to_next_task(learnings)
    """
```

---

## Configuration

Memory system configuration in `.moai/config/config.json`:

```json
{
  "memory": {
    "enabled": true,
    "storage_path": ".moai/memory/",
    "persistence": {
      "auto_save": true,
      "save_interval_seconds": 300
    },
    "context_hints": {
      "enabled": true,
      "max_hints": 500,
      "confidence_decay_rate": 0.001,
      "load_on_session_start": true,
      "auto_update": true
    },
    "semantic_memory": {
      "enabled": true,
      "auto_detect": true,
      "confidence_threshold": 0.6,
      "prune_interval_days": 30,
      "references_tracking": true
    },
    "episodic_memory": {
      "enabled": true,
      "track_decisions": true,
      "track_errors": true,
      "archive_after_days": 90,
      "max_active_episodes": 1000,
      "similarity_threshold": 0.7
    },
    "performance": {
      "use_sqlite": false,
      "use_sqlite_if_episodes_exceed": 1000,
      "index_caching": true,
      "cache_ttl_seconds": 3600
    },
    "privacy": {
      "exclude_patterns": [".env", ".secret", "*.credentials"],
      "anonymize_file_paths": false,
      "encrypt_sensitive": false
    }
  }
}
```

---

## Performance

Memory system performance benchmarks:

### Load Times

- **Memory Index Load**: <50ms
- **Context Hint Lookup**: <5ms (indexed)
- **Semantic Search**: <20ms (up to 1000 concepts)
- **Episode Retrieval**: <30ms (up to 5 results)
- **Similarity Matching**: <100ms (across 1000+ episodes)

### Storage

- **Context Hints**: ~2KB per hint, 500 hints = ~1MB
- **Project Knowledge**: ~10-50KB typical
- **Individual Episode**: ~5-20KB
- **Yearly Archive**: ~10-100MB (1000+ episodes)
- **Total Typical Project**: ~50-200MB (1-2 years)

### Optimization Strategies

1. **Prune Low-Confidence Hints** (Quarterly)
   ```python
   prune_knowledge(min_confidence=0.6)
   ```

2. **Archive Old Episodes** (Automatically after 90 days)
   ```
   .moai/memory/episodes/ → .moai/memory/episodes/archive/YYYY-MM.tar.gz
   ```

3. **Use SQLite for Large Projects** (>1000 episodes)
   ```json
   {
     "memory": {
       "use_sqlite": true
     }
   }
   ```

4. **Index Caching** (TTL: 1 hour)
   ```
   Frequently accessed patterns cached in memory
   ```

---

## Future Enhancements

### 1. Distributed Memory (Redis)

For multi-agent teams:

```python
class DistributedMemory:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    async def share_context_hints(self, agent_id: str):
        """Share hints across agent team"""
        hints = await self.redis.get(f"hints:{agent_id}")
        return json.loads(hints)

    async def sync_knowledge(self, project_id: str):
        """Synchronize project knowledge across team"""
        knowledge = await self.redis.get(f"knowledge:{project_id}")
        return json.loads(knowledge)
```

### 2. Semantic Search with Embeddings

For intelligent knowledge retrieval:

```python
from sentence_transformers import SentenceTransformer

class SemanticMemoryWithEmbeddings:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def embed_concept(self, concept: str) -> List[float]:
        """Convert concept to embedding"""
        return self.model.encode(concept).tolist()

    async def semantic_search(self, query: str, limit: int = 5):
        """Find similar concepts using embeddings"""
        query_embedding = self.embed_concept(query)
        # Find most similar stored embeddings
        results = await self.similarity_search(query_embedding, limit)
        return results
```

### 3. Federated Learning Across Teams

For multi-team knowledge sharing:

```python
class FederatedMemory:
    async def aggregate_team_knowledge(self, team_ids: List[str]):
        """Aggregate knowledge from multiple teams"""
        aggregated = {}
        for team_id in team_ids:
            team_knowledge = await self.fetch_team_knowledge(team_id)
            self.merge_knowledge(aggregated, team_knowledge)
        return aggregated

    async def consensus_decision(self, teams: List[str], decision: str):
        """Reach consensus on architectural decisions"""
        votes = []
        for team in teams:
            vote = await self.team_agent.vote(decision)
            votes.append(vote)
        return determine_consensus(votes)
```

### 4. Predictive Context Hints

Using patterns to predict needs:

```python
class PredictiveMemory:
    def predict_next_task(self, current_context: Dict) -> str:
        """Predict likely next task based on history"""
        similar_episodes = self.find_similar_episodes(current_context)
        if similar_episodes:
            # Find common next tasks
            next_tasks = [ep.metadata.get('next_task') for ep in similar_episodes]
            return most_common(next_tasks)

    def predict_agent_needs(self, task: str) -> List[str]:
        """Predict which agents will be needed"""
        similar = self.find_similar_episodes(task_type=task)
        agent_patterns = self.extract_agent_patterns(similar)
        return self.rank_agents(agent_patterns)
```

---

## Summary

The MoAI-Flow cross-session memory system provides three complementary memory tiers:

1. **ContextHints** for session-level preference adaptation (loaded at session start)
2. **SemanticMemory** for project-wide knowledge retention (prevents rework)
3. **EpisodicMemory** for detailed event history (learns from past successes and failures)

Together these enable:
- Seamless session continuity
- Adaptive agent behavior tuning
- Intelligent task execution optimization
- Knowledge preservation and reuse
- Automatic learning from experience

The system integrates with hooks for automatic persistence and provides fast APIs for real-time memory access. As MoAI-ADK grows, these capabilities provide the foundation for increasingly intelligent and adaptive agent orchestration.
