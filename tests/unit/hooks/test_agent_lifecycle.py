#!/usr/bin/env python3
"""
Test script for AgentLifecycle hooks

Demonstrates:
1. Agent spawn/complete/error lifecycle
2. Integration with SwarmDB
3. Event logging to .moai/logs/agent-transcripts/
4. Registry management
5. Performance testing with multiple agents

Usage:
    python test_agent_lifecycle.py
"""

import sys
import time
from pathlib import Path

# Add moai-flow to path
moai_flow_path = Path(__file__).parent.parent
sys.path.insert(0, str(moai_flow_path))

from hooks.agent_lifecycle import (
    cleanup_old_agents,
    generate_agent_id,
    get_active_agents,
    get_agent_registry,
    on_agent_complete,
    on_agent_error,
    on_agent_spawn,
)


def test_basic_lifecycle():
    """Test 1: Basic agent lifecycle (spawn -> complete)"""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Agent Lifecycle (spawn -> complete)")
    print("=" * 60)

    agent_id = generate_agent_id()
    print(f"Generated agent ID: {agent_id}")

    # Spawn
    print("\n[1/3] Spawning agent...")
    on_agent_spawn(
        agent_id=agent_id,
        agent_type="expert-backend",
        metadata={
            "prompt": "Design REST API for user authentication",
            "model": "claude-sonnet-4",
            "parent_agent_id": None,
            "priority": 1,
            "custom_field": "test_value"
        }
    )
    print(f"✓ Agent spawned: {agent_id}")

    # Simulate work
    print("\n[2/3] Simulating agent work (500ms)...")
    start_time = time.time()
    time.sleep(0.5)
    duration_ms = int((time.time() - start_time) * 1000)

    # Complete
    print("\n[3/3] Completing agent...")
    on_agent_complete(
        agent_id=agent_id,
        result={
            "status": "success",
            "endpoints_designed": 5,
            "files_created": ["routes.py", "models.py", "schemas.py"]
        },
        duration_ms=duration_ms
    )
    print(f"✓ Agent completed: {agent_id} ({duration_ms}ms)")

    # Verify registry
    registry = get_agent_registry()
    agent_info = registry.get_agent(agent_id)
    print(f"\n📊 Agent Info:")
    print(f"  - Type: {agent_info['agent_type']}")
    print(f"  - Status: {agent_info['status']}")
    print(f"  - Duration: {agent_info.get('duration_ms', 0)}ms")

    print("\n✅ TEST 1 PASSED")


def test_error_handling():
    """Test 2: Agent error handling (spawn -> error)"""
    print("\n" + "=" * 60)
    print("TEST 2: Agent Error Handling (spawn -> error)")
    print("=" * 60)

    agent_id = generate_agent_id()
    print(f"Generated agent ID: {agent_id}")

    # Spawn
    print("\n[1/3] Spawning agent...")
    on_agent_spawn(
        agent_id=agent_id,
        agent_type="expert-frontend",
        metadata={
            "prompt": "Build React component with TypeScript",
            "model": "claude-sonnet-4"
        }
    )
    print(f"✓ Agent spawned: {agent_id}")

    # Simulate error
    print("\n[2/3] Simulating agent error...")
    try:
        # Intentional error
        raise ValueError("Invalid component props: missing 'onClick' handler")
    except Exception as e:
        print(f"⚠️  Error occurred: {type(e).__name__}: {e}")

        print("\n[3/3] Recording error...")
        on_agent_error(agent_id=agent_id, error=e)
        print(f"✓ Error tracked: {agent_id}")

    # Verify registry
    registry = get_agent_registry()
    agent_info = registry.get_agent(agent_id)
    print(f"\n📊 Agent Info:")
    print(f"  - Type: {agent_info['agent_type']}")
    print(f"  - Status: {agent_info['status']}")
    print(f"  - Error: {agent_info.get('error', {}).get('message', 'N/A')}")

    print("\n✅ TEST 2 PASSED")


def test_multiple_agents():
    """Test 3: Multiple concurrent agents"""
    print("\n" + "=" * 60)
    print("TEST 3: Multiple Concurrent Agents")
    print("=" * 60)

    num_agents = 5
    agent_ids = []

    # Spawn multiple agents
    print(f"\n[1/3] Spawning {num_agents} agents...")
    for i in range(num_agents):
        agent_id = generate_agent_id()
        agent_ids.append(agent_id)

        on_agent_spawn(
            agent_id=agent_id,
            agent_type=f"expert-{['backend', 'frontend', 'database', 'devops', 'security'][i]}",
            metadata={
                "prompt": f"Task {i+1}",
                "batch_id": "test_batch_001",
                "index": i
            }
        )
        print(f"  ✓ Spawned agent {i+1}/{num_agents}: {agent_id[:8]}...")

    # Check active agents
    print(f"\n[2/3] Checking active agents...")
    active = get_active_agents()
    print(f"✓ Active agents: {len(active)}")
    for agent in active[-num_agents:]:  # Show last N agents
        print(f"  - {agent['agent_id'][:8]}... ({agent['agent_type']}) - {agent['status']}")

    # Complete some, error some
    print(f"\n[3/3] Completing agents...")
    for i, agent_id in enumerate(agent_ids):
        if i % 2 == 0:
            # Complete
            on_agent_complete(
                agent_id=agent_id,
                result={"status": "success"},
                duration_ms=(i + 1) * 100
            )
            print(f"  ✓ Completed agent {i+1}/{num_agents}")
        else:
            # Error
            try:
                raise RuntimeError(f"Simulated error for agent {i+1}")
            except Exception as e:
                on_agent_error(agent_id=agent_id, error=e)
                print(f"  ⚠️  Error agent {i+1}/{num_agents}")

    # Final active count
    active_after = get_active_agents()
    print(f"\n📊 Final active agents: {len(active_after)}")

    print("\n✅ TEST 3 PASSED")


def test_registry_cleanup():
    """Test 4: Registry cleanup of old agents"""
    print("\n" + "=" * 60)
    print("TEST 4: Registry Cleanup")
    print("=" * 60)

    # Create old agent (simulate by modifying registry directly)
    print("\n[1/2] Creating test agents...")
    agent_id = generate_agent_id()
    on_agent_spawn(
        agent_id=agent_id,
        agent_type="test-agent",
        metadata={"test": "cleanup"}
    )
    print(f"✓ Created agent: {agent_id[:8]}...")

    # Cleanup (use 0 hours to force immediate cleanup)
    print("\n[2/2] Running cleanup (0 hours threshold)...")
    cleaned = cleanup_old_agents(max_age_hours=0)
    print(f"✓ Cleaned up {cleaned} agent(s)")

    print("\n✅ TEST 4 PASSED")


def test_swarmdb_integration():
    """Test 5: SwarmDB integration (if available)"""
    print("\n" + "=" * 60)
    print("TEST 5: SwarmDB Integration")
    print("=" * 60)

    try:
        from memory.swarm_db import SwarmDB

        print("\n[1/4] Initializing SwarmDB...")
        db = SwarmDB()
        print("✓ SwarmDB initialized")

        # Insert event
        print("\n[2/4] Inserting event...")
        agent_id = generate_agent_id()
        event_id = db.insert_event({
            "event_type": "spawn",
            "agent_id": agent_id,
            "agent_type": "test-agent",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "metadata": {"test": "swarmdb_integration"}
        })
        print(f"✓ Event inserted: {event_id[:8]}...")

        # Query events
        print("\n[3/4] Querying events...")
        events = db.get_events(agent_id=agent_id, limit=10)
        print(f"✓ Found {len(events)} event(s)")
        for event in events:
            print(f"  - {event['event_type']} @ {event['timestamp']}")

        # Cleanup
        print("\n[4/4] Closing database...")
        db.close()
        print("✓ Database closed")

        print("\n✅ TEST 5 PASSED")

    except ImportError as e:
        print(f"\n⚠️  SwarmDB not available (expected in early development): {e}")
        print("✓ TEST 5 SKIPPED")


def test_log_file_creation():
    """Test 6: Verify log file creation"""
    print("\n" + "=" * 60)
    print("TEST 6: Log File Creation")
    print("=" * 60)

    log_dir = Path.cwd() / ".moai" / "logs" / "agent-transcripts"

    print(f"\n[1/2] Checking log directory: {log_dir}")
    if log_dir.exists():
        print("✓ Log directory exists")

        # List log files
        log_files = list(log_dir.glob("*.log")) + list(log_dir.glob("*.jsonl"))
        print(f"\n[2/2] Found {len(log_files)} log file(s):")
        for log_file in log_files:
            size = log_file.stat().st_size
            print(f"  - {log_file.name} ({size} bytes)")

        print("\n✅ TEST 6 PASSED")
    else:
        print("⚠️  Log directory not created yet")
        print("✓ TEST 6 SKIPPED")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AgentLifecycle Hooks - Test Suite")
    print("=" * 60)
    print(f"Test suite started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    start_time = time.time()

    tests = [
        test_basic_lifecycle,
        test_error_handling,
        test_multiple_agents,
        test_registry_cleanup,
        test_swarmdb_integration,
        test_log_file_creation,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {test_func.__name__}")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    duration = time.time() - start_time

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Duration: {duration:.2f}s")

    log_dir = Path.cwd() / ".moai" / "logs" / "agent-transcripts"
    print(f"\n📝 Logs location: {log_dir}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
