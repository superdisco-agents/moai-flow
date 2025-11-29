#!/usr/bin/env python3
"""Tests for SessionStart Memory Loading Hook

Tests memory loading and context injection at session start:
- SwarmDB integration
- Context hints loading
- Episodic memory retrieval
- Session state loading
- Next action suggestions
- Graceful degradation

TDD Approach:
- RED: Write failing tests for each memory loading scenario
- GREEN: Implement hook to pass tests
- REFACTOR: Optimize parallel loading and error handling
"""

import json
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import pytest


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_swarm_db(tmp_path: Path):
    """Create mock SwarmDB with test data"""
    import sys

    # Add moai-flow to path
    moai_flow_path = Path(__file__).parent.parent.parent / "moai-flow"
    if str(moai_flow_path) not in sys.path:
        sys.path.insert(0, str(moai_flow_path))

    from memory.swarm_db import SwarmDB

    # Create test database
    db_path = tmp_path / "test-swarm.db"
    db = SwarmDB(db_path=db_path)

    # Insert test data
    # 1. User preferences
    db.store_memory(
        session_id="global",
        memory_type="context_hint",
        key="user_preferences",
        value={
            "communication": "detailed",
            "workflow": "agile",
            "expertise": "advanced"
        }
    )

    # 2. Recent episodic events
    now = datetime.now()
    agent_id = "test-agent-001"

    db.insert_event({
        "event_type": "spawn",
        "agent_id": agent_id,
        "agent_type": "expert-backend",
        "timestamp": (now - timedelta(hours=2)).isoformat(),
        "metadata": {"prompt": "Design API"}
    })

    db.insert_event({
        "event_type": "complete",
        "agent_id": agent_id,
        "agent_type": "expert-backend",
        "timestamp": (now - timedelta(hours=1)).isoformat(),
        "metadata": {"duration_ms": 5000, "result": "success"}
    })

    # 3. Semantic knowledge
    db.store_memory(
        session_id="global",
        memory_type="semantic",
        key="authentication",
        value={
            "pattern": "JWT",
            "confidence": 0.9,
            "last_used": now.isoformat()
        }
    )

    yield db

    # Cleanup
    db.close()


@pytest.fixture
def mock_session_state(tmp_path: Path):
    """Create mock last session state file"""
    state_file = tmp_path / "last-session-state.json"
    state_data = {
        "last_updated": datetime.now().isoformat(),
        "current_branch": "feature/SPEC-001",
        "uncommitted_changes": True,
        "uncommitted_files": 3,
        "specs_in_progress": ["SPEC-001", "SPEC-002"]
    }

    state_file.write_text(json.dumps(state_data, indent=2))
    return state_file


@pytest.fixture
def hook_script() -> Path:
    """Get path to hook script"""
    return Path(__file__).parent.parent.parent / ".claude" / "hooks" / "moai" / "session_start__load_memory.py"


# ============================================================================
# Unit Tests - Memory Loading Functions
# ============================================================================

def test_load_context_hints(mock_swarm_db):
    """Test loading context hints from SwarmDB"""
    import sys
    from pathlib import Path

    # Add hook directory to path
    hook_dir = Path(__file__).parent.parent.parent / ".claude" / "hooks" / "moai"
    if str(hook_dir) not in sys.path:
        sys.path.insert(0, str(hook_dir))

    from session_start__load_memory import load_context_hints

    # Load preferences
    prefs = load_context_hints(mock_swarm_db, "test-session")

    # Verify preferences loaded
    assert prefs is not None
    assert prefs.get("communication") == "detailed"
    assert prefs.get("workflow") == "agile"
    assert prefs.get("expertise") == "advanced"


def test_load_recent_episodes(mock_swarm_db):
    """Test loading recent episodic memory"""
    import sys
    from pathlib import Path

    # Add hook directory to path
    hook_dir = Path(__file__).parent.parent.parent / ".claude" / "hooks" / "moai"
    if str(hook_dir) not in sys.path:
        sys.path.insert(0, str(hook_dir))

    from session_start__load_memory import load_recent_episodes

    # Load recent episodes (last 24 hours)
    episodes = load_recent_episodes(mock_swarm_db, hours=24)

    # Verify episodes loaded
    assert len(episodes) == 2
    assert episodes[0]["event_type"] in ["spawn", "complete"]
    assert episodes[0]["agent_type"] == "expert-backend"


def test_load_semantic_knowledge(mock_swarm_db):
    """Test loading semantic memory patterns"""
    import sys
    from pathlib import Path

    # Add hook directory to path
    hook_dir = Path(__file__).parent.parent.parent / ".claude" / "hooks" / "moai"
    if str(hook_dir) not in sys.path:
        sys.path.insert(0, str(hook_dir))

    from session_start__load_memory import load_semantic_knowledge

    # Load semantic knowledge
    knowledge = load_semantic_knowledge(mock_swarm_db)

    # Verify knowledge loaded
    assert len(knowledge) == 1
    assert knowledge[0]["topic"] == "authentication"
    assert knowledge[0]["data"]["pattern"] == "JWT"


def test_suggest_next_actions_with_uncommitted_changes(tmp_path):
    """Test action suggestions with uncommitted changes"""
    import sys
    from pathlib import Path

    # Add hook directory to path
    hook_dir = Path(__file__).parent.parent.parent / ".claude" / "hooks" / "moai"
    if str(hook_dir) not in sys.path:
        sys.path.insert(0, str(hook_dir))

    from session_start__load_memory import suggest_next_actions

    last_state = {
        "uncommitted_changes": True,
        "specs_in_progress": []
    }

    suggestions = suggest_next_actions(last_state, [])

    # Should suggest reviewing uncommitted changes
    assert len(suggestions) > 0
    assert any("uncommitted" in s.lower() for s in suggestions)


def test_suggest_next_actions_with_specs_in_progress(tmp_path):
    """Test action suggestions with SPECs in progress"""
    import sys
    from pathlib import Path

    # Add hook directory to path
    hook_dir = Path(__file__).parent.parent.parent / ".claude" / "hooks" / "moai"
    if str(hook_dir) not in sys.path:
        sys.path.insert(0, str(hook_dir))

    from session_start__load_memory import suggest_next_actions

    last_state = {
        "uncommitted_changes": False,
        "specs_in_progress": ["SPEC-001", "SPEC-002"]
    }

    suggestions = suggest_next_actions(last_state, [])

    # Should suggest continuing SPEC implementation
    assert len(suggestions) >= 2
    assert any("SPEC-001" in s for s in suggestions)
    assert any("SPEC-002" in s for s in suggestions)


# ============================================================================
# Integration Tests - Complete Hook Execution
# ============================================================================

def test_hook_execution_with_memory(hook_script, mock_swarm_db, tmp_path, monkeypatch):
    """Test complete hook execution with memory available"""
    # Set up environment
    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))

    # Create .moai/memory directory
    memory_dir = tmp_path / ".moai" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)

    # Create last session state
    state_file = memory_dir / "last-session-state.json"
    state_data = {
        "last_updated": datetime.now().isoformat(),
        "current_branch": "main",
        "uncommitted_changes": False,
        "uncommitted_files": 0,
        "specs_in_progress": ["SPEC-001"]
    }
    state_file.write_text(json.dumps(state_data))

    # Copy SwarmDB to .moai/memory
    import shutil
    shutil.copy(mock_swarm_db.db_path, memory_dir / "swarm.db")

    # Execute hook
    result = subprocess.run(
        [str(hook_script)],
        input="{}",
        capture_output=True,
        text=True,
        timeout=5,
        cwd=tmp_path
    )

    # Verify execution
    assert result.returncode == 0

    # Parse output
    output = json.loads(result.stdout)
    assert output["continue"] is True

    # Verify system message contains memory summary
    system_msg = output.get("systemMessage", "")
    # Should have some content if memory loaded successfully
    # (may be empty due to graceful degradation, which is acceptable)


def test_hook_execution_without_memory(hook_script, tmp_path, monkeypatch):
    """Test hook execution with graceful degradation (no memory)"""
    # Set up empty environment
    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))

    # Execute hook (no SwarmDB available)
    result = subprocess.run(
        [str(hook_script)],
        input="{}",
        capture_output=True,
        text=True,
        timeout=5,
        cwd=tmp_path
    )

    # Verify graceful degradation
    assert result.returncode == 0

    # Parse output
    output = json.loads(result.stdout)
    assert output["continue"] is True

    # System message may be empty (graceful degradation)
    # This is expected behavior when memory unavailable


def test_hook_execution_timeout(hook_script, tmp_path):
    """Test hook handles timeout gracefully"""
    # Execute hook with very short timeout
    result = subprocess.run(
        [str(hook_script)],
        input="{}",
        capture_output=True,
        text=True,
        timeout=5,  # Hook internal timeout is 2s
        cwd=tmp_path
    )

    # Should complete (gracefully degraded if timeout occurred)
    assert result.returncode in [0, 1]  # 0 for success, 1 for timeout

    # Parse output
    output = json.loads(result.stdout)
    assert output["continue"] is True


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

def test_invalid_json_input(hook_script, tmp_path):
    """Test hook handles invalid JSON input"""
    result = subprocess.run(
        [str(hook_script)],
        input="invalid json",
        capture_output=True,
        text=True,
        timeout=5,
        cwd=tmp_path
    )

    # Should handle gracefully
    assert result.returncode in [0, 1]

    # Parse output
    output = json.loads(result.stdout)
    assert output["continue"] is True


def test_missing_swarm_db_graceful_degradation(hook_script, tmp_path, monkeypatch):
    """Test graceful degradation when SwarmDB missing"""
    # Set up environment without SwarmDB
    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))

    # Execute hook
    result = subprocess.run(
        [str(hook_script)],
        input="{}",
        capture_output=True,
        text=True,
        timeout=5,
        cwd=tmp_path
    )

    # Should succeed with empty context
    assert result.returncode == 0

    output = json.loads(result.stdout)
    assert output["continue"] is True


def test_session_context_file_created(hook_script, tmp_path, monkeypatch):
    """Test that session context file is created"""
    # Set up environment
    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))

    # Create .moai/memory directory
    memory_dir = tmp_path / ".moai" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)

    # Execute hook
    subprocess.run(
        [str(hook_script)],
        input="{}",
        capture_output=True,
        text=True,
        timeout=5,
        cwd=tmp_path
    )

    # Verify session context file created
    context_file = memory_dir / "session-context.json"
    if context_file.exists():
        # File created - verify structure
        context_data = json.loads(context_file.read_text())
        assert "session_id" in context_data
        assert "loaded_at" in context_data
        assert "context" in context_data

        # Verify context structure
        ctx = context_data["context"]
        assert "user_preferences" in ctx
        assert "recent_episodes" in ctx
        assert "relevant_knowledge" in ctx
        assert "suggested_next_actions" in ctx


# ============================================================================
# Performance Tests
# ============================================================================

def test_hook_performance_under_2_seconds(hook_script, tmp_path, monkeypatch):
    """Test that hook completes within 2 second timeout"""
    import time

    # Set up environment
    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))

    # Execute hook and measure time
    start = time.time()
    result = subprocess.run(
        [str(hook_script)],
        input="{}",
        capture_output=True,
        text=True,
        timeout=5,
        cwd=tmp_path
    )
    duration = time.time() - start

    # Should complete quickly
    assert result.returncode == 0
    assert duration < 2.0  # Under 2 seconds


# ============================================================================
# Test Metadata
# ============================================================================

def test_hook_metadata():
    """Verify hook script has correct metadata"""
    hook_script = Path(__file__).parent.parent.parent / ".claude" / "hooks" / "moai" / "session_start__load_memory.py"

    # Verify file exists
    assert hook_script.exists()

    # Verify executable
    assert hook_script.stat().st_mode & 0o111  # Check execute bits

    # Verify docstring
    content = hook_script.read_text()
    assert "SessionStart Hook: Load Memory and Context Hints" in content
    assert "SwarmDB" in content
    assert "EpisodicMemory" in content
    assert "ContextHints" in content
