# Distributed Memory Examples

Advanced integration patterns combining all memory components for intelligent multi-agent coordination.

## Example 1: Knowledge-Backed Decision Making

Integrate SemanticMemory and EpisodicMemory for intelligent decision-making based on historical knowledge.

```python
from moai_flow.memory import (
    SwarmDB,
    SemanticMemory,
    EpisodicMemory,
    KnowledgeCategory,
    EventType
)

class IntelligentDecisionMaker:
    """Make decisions backed by semantic knowledge and episodic history"""

    def __init__(self, db: SwarmDB, project_id: str):
        self.db = db
        self.semantic = SemanticMemory(db, project_id=project_id)
        self.episodic = EpisodicMemory(db, project_id=project_id)

    def make_decision(self, decision_type: str, options: list, context: dict) -> dict:
        """
        Make informed decision using:
        1. Semantic knowledge lookup
        2. Similar episode analysis
        3. Outcome statistics
        """

        # 1. Check semantic knowledge
        knowledge = self.semantic.search_knowledge(
            query=context.get('task_type', ''),
            min_confidence=0.7,
            category=KnowledgeCategory.ARCHITECTURAL_DECISION
        )

        # 2. Find similar past decisions
        similar = self.episodic.find_similar_episodes(
            current_context=context,
            event_type=EventType.DECISION_MADE,
            limit=5
        )

        # 3. Get outcome statistics
        stats = self.episodic.get_outcome_statistics(decision_type)

        # 4. Make informed choice
        if knowledge:
            # Use existing ADR
            recommended = knowledge[0]['knowledge'].get('decision')
            rationale = f"Based on ADR: {knowledge[0]['topic']} (confidence: {knowledge[0]['confidence']:.2f})"
            chosen = self._match_option(recommended, options)
        elif similar:
            # Use similar episode
            successful = [ep for ep in similar if ep.get('outcome', {}).get('status') == 'success']
            if successful:
                chosen_data = successful[0]['event_data']
                chosen = chosen_data.get('chosen')
                rationale = f"Similar past success: {successful[0]['id']}"
            else:
                chosen = options[0]
                rationale = "No successful similar episodes found, using default"
        else:
            # Default choice
            chosen = options[0]
            rationale = "No historical data, using default"

        # 5. Record decision
        decision_id = self.episodic.record_decision(
            decision_type=decision_type,
            options=options,
            chosen=chosen,
            rationale=rationale,
            context=context
        )

        return {
            'decision_id': decision_id,
            'chosen': chosen,
            'rationale': rationale,
            'confidence': knowledge[0]['confidence'] if knowledge else 0.5,
            'historical_success_rate': stats['success_rate'] if stats['total_decisions'] > 0 else None
        }

    def record_outcome(self, decision_id: str, success: bool, metrics: dict):
        """Record outcome and update semantic knowledge"""

        # Record episodic outcome
        self.episodic.record_outcome(
            decision_id,
            outcome="success" if success else "failure",
            metrics=metrics
        )

        # Update semantic knowledge if exists
        decision = self.episodic.get_event(decision_id)
        if decision:
            context = decision.get('context', {})
            task_type = context.get('task_type')

            # Search for related knowledge
            knowledge = self.semantic.search_knowledge(
                query=task_type,
                min_confidence=0.0,
                limit=1
            )

            if knowledge:
                # Update confidence
                if success:
                    self.semantic.record_success(knowledge[0]['id'])
                else:
                    self.semantic.record_failure(knowledge[0]['id'])

    def _match_option(self, recommendation: str, options: list) -> str:
        """Match recommendation to available options"""
        for option in options:
            if recommendation.lower() in option.lower():
                return option
        return options[0]


# Usage Example
db = SwarmDB()
decision_maker = IntelligentDecisionMaker(db, project_id="moai-adk")

# Store architectural knowledge
semantic = SemanticMemory(db, project_id="moai-adk")
semantic.store_knowledge(
    topic="api_framework_choice",
    knowledge={
        "decision": "Use FastAPI for async REST APIs",
        "rationale": "Modern, async-first, auto-docs, type hints",
        "alternatives": ["Flask", "Django REST"]
    },
    confidence=0.9,
    category=KnowledgeCategory.ARCHITECTURAL_DECISION,
    tags=["api", "framework", "python"]
)

# Make decision
result = decision_maker.make_decision(
    decision_type="framework_selection",
    options=["FastAPI", "Flask", "Django"],
    context={
        "task_type": "api implementation",
        "requirements": ["async", "performance"],
        "complexity": "medium"
    }
)

print(f"Decision: {result['chosen']}")
print(f"Rationale: {result['rationale']}")
print(f"Confidence: {result['confidence']:.2f}")

# Record successful outcome
decision_maker.record_outcome(
    result['decision_id'],
    success=True,
    metrics={
        "duration_ms": 5000,
        "tests_passed": 15,
        "performance_score": 0.95
    }
)

db.close()
print("✅ Example 1 complete")
```

## Example 2: Adaptive Multi-Agent Workflow

Combine ContextHints and EpisodicMemory for adaptive workflow optimization.

```python
from moai_flow.memory import (
    SwarmDB,
    ContextHints,
    EpisodicMemory,
    EventType,
    PreferenceCategory,
    WorkflowPreference
)
import time

class AdaptiveWorkflowManager:
    """Manage workflows that adapt based on user patterns and outcomes"""

    def __init__(self, db: SwarmDB, session_id: str, project_id: str):
        self.db = db
        self.hints = ContextHints(db, session_id=session_id)
        self.episodic = EpisodicMemory(db, project_id=project_id)

    def execute_task(self, task_type: str, spec_id: str, agents: list) -> dict:
        """Execute task with pattern learning"""

        # Get recommended workflow
        workflow = self.hints.get_recommended_workflow()

        # Record start
        start_time = time.time()
        task_event_id = self.episodic.record_event(
            EventType.IMPLEMENTATION_COMPLETE,
            event_data={
                "task_type": task_type,
                "spec_id": spec_id,
                "workflow": workflow,
                "agents": agents
            },
            context={
                "workflow": workflow,
                "expertise": self.hints.get_expertise_level()
            }
        )

        # Simulate task execution
        # (In real usage, this would call actual agents)
        time.sleep(0.1)
        success = True
        duration_ms = (time.time() - start_time) * 1000

        # Record outcome
        self.episodic.record_outcome(
            task_event_id,
            outcome="success" if success else "failure",
            metrics={
                "duration_ms": duration_ms,
                "tests_passed": 10 if success else 5,
                "coverage": 92.5 if success else 65.0
            }
        )

        # Record task pattern
        self.hints.record_task_pattern(
            task_type=task_type,
            metadata={
                "spec_id": spec_id,
                "agents_used": agents,
                "success": success,
                "duration_ms": duration_ms,
                "tools_used": agents,
                "workflow": workflow
            }
        )

        return {
            'success': success,
            'duration_ms': duration_ms,
            'workflow_used': workflow
        }

    def optimize_workflow(self):
        """Analyze patterns and optimize workflow preference"""

        # Analyze workflow patterns
        analysis = self.hints.analyze_workflow_patterns()

        # Get episodic statistics for different workflows
        tdd_stats = self.episodic.get_outcome_statistics("tdd_workflow")
        impl_stats = self.episodic.get_outcome_statistics("impl_first_workflow")

        print("\n--- Workflow Optimization ---")
        print(f"TDD success rate: {tdd_stats.get('success_rate', 0):.1f}%")
        print(f"Impl-first success rate: {impl_stats.get('success_rate', 0):.1f}%")

        # Optimize based on patterns
        if tdd_stats.get('success_rate', 0) > impl_stats.get('success_rate', 0) + 20:
            self.hints.set_preference(
                PreferenceCategory.WORKFLOW,
                WorkflowPreference.TDD
            )
            print("✓ Switched to TDD workflow (better success rate)")
        elif impl_stats.get('success_rate', 0) > tdd_stats.get('success_rate', 0) + 20:
            self.hints.set_preference(
                PreferenceCategory.WORKFLOW,
                WorkflowPreference.IMPL_FIRST
            )
            print("✓ Switched to impl-first workflow (better success rate)")

        # Get next suggestion
        suggestion = self.hints.suggest_next_action()
        if suggestion:
            print(f"✓ Suggested next: {suggestion}")

        return analysis


# Usage Example
db = SwarmDB()
manager = AdaptiveWorkflowManager(
    db,
    session_id="session-123",
    project_id="moai-adk"
)

# Execute multiple tasks
print("Executing tasks...")
for i in range(3):
    result = manager.execute_task(
        task_type="implementation",
        spec_id=f"SPEC-00{i+1}",
        agents=["expert-backend", "manager-tdd"]
    )
    print(f"Task {i+1}: {result['success']} ({result['duration_ms']:.0f}ms)")

# Optimize workflow
analysis = manager.optimize_workflow()

print(f"\nTotal tasks: {analysis['total_tasks']}")
print(f"Success rates: {analysis['success_rate']}")
print(f"Common sequences: {analysis['common_sequences'][:2]}")

db.close()
print("\n✅ Example 2 complete")
```

## Example 3: Distributed Knowledge Sharing

Multiple agents sharing knowledge through distributed memory pools.

```python
from moai_flow.memory import SwarmDB, SemanticMemory, KnowledgeCategory

class AgentKnowledgePool:
    """Shared knowledge pool for multi-agent coordination"""

    def __init__(self, db: SwarmDB, pool_id: str):
        self.db = db
        self.pool_id = pool_id
        self.memory = SemanticMemory(db, project_id=pool_id)

    def contribute_pattern(self, agent_id: str, pattern_name: str, pattern_data: dict):
        """Agent contributes pattern to shared pool"""

        pattern_id = self.memory.store_pattern(
            pattern_name=pattern_name,
            pattern_data={
                **pattern_data,
                "contributor": agent_id,
                "contributed_at": datetime.now().isoformat()
            },
            category=KnowledgeCategory.CODE_PATTERN,
            confidence=0.5  # Start with moderate confidence
        )

        print(f"✓ Agent {agent_id} contributed pattern: {pattern_name}")
        return pattern_id

    def use_pattern(self, agent_id: str, pattern_name: str, success: bool):
        """Agent uses pattern and reports outcome"""

        pattern = self.memory.get_pattern(pattern_name)
        if not pattern:
            print(f"✗ Pattern not found: {pattern_name}")
            return

        # Record usage outcome
        if success:
            self.memory.record_success(pattern['id'])
            print(f"✓ Agent {agent_id} successfully used: {pattern_name}")
        else:
            self.memory.record_failure(pattern['id'])
            print(f"✗ Agent {agent_id} failed using: {pattern_name}")

        # Show updated stats
        updated = self.memory.get_pattern(pattern_name)
        print(f"  Usage: {updated['usage_count']} | Confidence: {updated['confidence']:.2f}")

    def get_popular_patterns(self, limit: int = 5) -> list:
        """Get most popular patterns in pool"""

        all_patterns = self.memory.list_patterns(limit=100)
        sorted_patterns = sorted(
            all_patterns,
            key=lambda p: (p['confidence'], p['usage_count']),
            reverse=True
        )

        return sorted_patterns[:limit]

    def prune_low_quality_patterns(self):
        """Remove low-confidence patterns"""

        pruned = self.memory.prune_low_confidence(threshold=0.3, min_age_days=7)
        print(f"✓ Pruned {pruned} low-quality patterns")
        return pruned


# Usage Example
from datetime import datetime

db = SwarmDB()
pool = AgentKnowledgePool(db, pool_id="team-shared")

# Agent 1 contributes pattern
pool.contribute_pattern(
    agent_id="agent-001",
    pattern_name="error_handler_decorator",
    pattern_data={
        "code": "@handle_errors\ndef endpoint(): ...",
        "description": "Standard error handling decorator",
        "language": "python"
    }
)

# Agent 2 uses pattern successfully
pool.use_pattern("agent-002", "error_handler_decorator", success=True)

# Agent 3 uses pattern successfully
pool.use_pattern("agent-003", "error_handler_decorator", success=True)

# Agent 4 uses pattern but fails
pool.use_pattern("agent-004", "error_handler_decorator", success=False)

# Agent 5 contributes another pattern
pool.contribute_pattern(
    agent_id="agent-005",
    pattern_name="async_batch_processor",
    pattern_data={
        "code": "async def process_batch(items): ...",
        "description": "Batch processing with async",
        "language": "python"
    }
)

# Get popular patterns
print("\n--- Popular Patterns ---")
popular = pool.get_popular_patterns(3)
for i, pattern in enumerate(popular, 1):
    print(f"{i}. {pattern['pattern_name']}")
    print(f"   Confidence: {pattern['confidence']:.2f}")
    print(f"   Usage: {pattern['usage_count']} times")
    print(f"   Contributor: {pattern['pattern_data'].get('contributor')}")

db.close()
print("\n✅ Example 3 complete")
```

## Example 4: Cross-Session Learning

Persist and reuse knowledge across multiple sessions.

```python
from moai_flow.memory import (
    SwarmDB,
    SemanticMemory,
    EpisodicMemory,
    ContextHints,
    KnowledgeCategory
)

class CrossSessionLearner:
    """Learn and persist knowledge across sessions"""

    def __init__(self, db: SwarmDB, project_id: str):
        self.db = db
        self.project_id = project_id
        self.semantic = SemanticMemory(db, project_id=project_id)
        self.episodic = EpisodicMemory(db, project_id=project_id)

    def start_session(self, session_id: str) -> dict:
        """Start new session with historical context"""

        hints = ContextHints(self.db, session_id=session_id)

        # Load previous session patterns
        stats = self.semantic.get_statistics()
        recent_decisions = self.episodic.get_recent_events(limit=10)

        # Get knowledge summary
        high_confidence = self.semantic.list_knowledge(
            min_confidence=0.8,
            limit=10
        )

        return {
            'session_id': session_id,
            'total_knowledge': stats['knowledge']['total_knowledge'],
            'avg_confidence': stats['knowledge']['avg_confidence'],
            'recent_decisions': len(recent_decisions),
            'high_confidence_knowledge': len(high_confidence),
            'hints': hints
        }

    def end_session(self, session_id: str, session_summary: dict):
        """End session and persist learnings"""

        # Store session summary as knowledge
        self.semantic.store_knowledge(
            topic=f"session_{session_id}",
            knowledge={
                "session_id": session_id,
                "summary": session_summary,
                "ended_at": datetime.now().isoformat()
            },
            confidence=0.6,
            category="convention",
            tags=["session", "summary"]
        )

        # Record session completion event
        self.episodic.record_event(
            "session_complete",
            event_data={
                "session_id": session_id,
                "duration_ms": session_summary.get('duration_ms'),
                "tasks_completed": session_summary.get('tasks_completed')
            }
        )

        print(f"✓ Session {session_id} knowledge persisted")

    def get_session_insights(self) -> dict:
        """Analyze all sessions for insights"""

        # Get all session knowledge
        sessions = self.semantic.search_knowledge(
            query="session",
            category="convention",
            limit=100
        )

        # Analyze session outcomes
        stats = self.semantic.get_statistics()

        return {
            'total_sessions': len(sessions),
            'total_knowledge': stats['knowledge']['total_knowledge'],
            'knowledge_by_category': stats['categories']
        }


# Usage Example - Multiple Sessions
db = SwarmDB()
learner = CrossSessionLearner(db, project_id="moai-adk")

# Session 1
print("\n=== Session 1 ===")
session1 = learner.start_session("session-001")
print(f"Started session with {session1['total_knowledge']} knowledge items")

# Simulate work
semantic = SemanticMemory(db, project_id="moai-adk")
semantic.store_knowledge(
    topic="session1_pattern",
    knowledge={"pattern": "Test-first approach worked well"},
    confidence=0.8,
    category=KnowledgeCategory.BEST_PRACTICE
)

learner.end_session("session-001", {
    "duration_ms": 300000,
    "tasks_completed": 5,
    "success_rate": 0.8
})

# Session 2 - Reuses knowledge from Session 1
print("\n=== Session 2 ===")
session2 = learner.start_session("session-002")
print(f"Started session with {session2['total_knowledge']} knowledge items (includes Session 1)")

# Add more knowledge
semantic.store_knowledge(
    topic="session2_improvement",
    knowledge={"improvement": "Automated testing increased success rate"},
    confidence=0.85,
    category=KnowledgeCategory.BEST_PRACTICE
)

learner.end_session("session-002", {
    "duration_ms": 250000,
    "tasks_completed": 7,
    "success_rate": 0.9
})

# Analyze insights
print("\n=== Session Insights ===")
insights = learner.get_session_insights()
print(f"Total sessions: {insights['total_sessions']}")
print(f"Total knowledge: {insights['total_knowledge']}")
print(f"Knowledge by category: {insights['knowledge_by_category']}")

db.close()
print("\n✅ Example 4 complete")
```

## Running Distributed Examples

```bash
# Run all distributed examples
python examples/distributed-memory.py

# Or run individually
python -c "from examples.distributed_memory import example1; example1()"
python -c "from examples.distributed_memory import example2; example2()"
python -c "from examples.distributed_memory import example3; example3()"
python -c "from examples.distributed_memory import example4; example4()"
```

## Key Patterns Demonstrated

1. **Knowledge-Backed Decisions**: Use SemanticMemory + EpisodicMemory for intelligent decision-making
2. **Adaptive Workflows**: ContextHints + EpisodicMemory for pattern-based optimization
3. **Distributed Sharing**: Multiple agents contributing to and learning from shared knowledge pools
4. **Cross-Session Learning**: Persistent knowledge that accumulates across multiple sessions

All examples use the same `.moai/memory/swarm.db` database, demonstrating true distributed memory coordination.
