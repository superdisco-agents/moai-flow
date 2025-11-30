"""
Load Testing for MoAI-Flow Production Deployment

Simulates concurrent agent operations and measures performance under load.
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
from datetime import datetime, UTC
import psutil
import pytest

from moai_flow.memory import SwarmDB
from moai_flow.core.swarm_coordinator import SwarmCoordinator, AgentState


class LoadTestMetrics:
    """Collect and analyze performance metrics during load testing."""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.response_times: List[float] = []
        self.errors: List[str] = []
        self.cpu_samples: List[float] = []
        self.memory_samples: List[float] = []

    def record_response(self, duration: float):
        """Record individual operation response time."""
        self.response_times.append(duration)

    def record_error(self, error: str):
        """Record error during testing."""
        self.errors.append(error)

    def sample_resources(self):
        """Sample current CPU and memory usage."""
        process = psutil.Process()
        self.cpu_samples.append(process.cpu_percent())
        self.memory_samples.append(process.memory_info().rss / (1024 * 1024))  # MB

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        if not self.response_times:
            return {"error": "No response times recorded"}

        sorted_times = sorted(self.response_times)
        total_operations = len(self.response_times)

        return {
            "total_operations": total_operations,
            "total_time_seconds": (self.end_time - self.start_time).total_seconds() if self.end_time else 0,
            "throughput_ops_per_second": total_operations / max((self.end_time - self.start_time).total_seconds(), 0.001),
            "response_time": {
                "mean_ms": statistics.mean(self.response_times) * 1000,
                "median_ms": statistics.median(self.response_times) * 1000,
                "p50_ms": sorted_times[int(len(sorted_times) * 0.50)] * 1000,
                "p95_ms": sorted_times[int(len(sorted_times) * 0.95)] * 1000,
                "p99_ms": sorted_times[int(len(sorted_times) * 0.99)] * 1000,
                "min_ms": min(self.response_times) * 1000,
                "max_ms": max(self.response_times) * 1000,
            },
            "resource_usage": {
                "cpu_avg_percent": statistics.mean(self.cpu_samples) if self.cpu_samples else 0,
                "cpu_max_percent": max(self.cpu_samples) if self.cpu_samples else 0,
                "memory_avg_mb": statistics.mean(self.memory_samples) if self.memory_samples else 0,
                "memory_max_mb": max(self.memory_samples) if self.memory_samples else 0,
            },
            "errors": {
                "count": len(self.errors),
                "rate_percent": (len(self.errors) / total_operations) * 100,
                "messages": self.errors[:10]  # First 10 errors
            }
        }


class LoadTestRunner:
    """Execute load tests with configurable concurrency."""

    def __init__(self, num_agents: int = 100):
        self.num_agents = num_agents
        self.metrics = LoadTestMetrics()
        self.db = SwarmDB()

    async def simulate_agent_lifecycle(self, agent_id: str) -> float:
        """Simulate complete agent lifecycle: spawn → task → complete."""
        start_time = time.perf_counter()

        try:
            # Spawn agent
            await asyncio.to_thread(
                self.db.insert_event,
                {
                    "event_type": "agent_spawned",
                    "agent_id": agent_id,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "parent_id": "load_test_coordinator",
                    "capabilities": ["test_capability"]
                }
            )

            # Agent executes task
            await asyncio.sleep(0.001)  # Simulate minimal work

            await asyncio.to_thread(
                self.db.insert_event,
                {
                    "event_type": "task_completed",
                    "agent_id": agent_id,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "result": "success"
                }
            )

            # Agent completes
            await asyncio.to_thread(
                self.db.insert_event,
                {
                    "event_type": "agent_completed",
                    "agent_id": agent_id,
                    "timestamp": datetime.now(UTC).isoformat()
                }
            )

            duration = time.perf_counter() - start_time
            self.metrics.record_response(duration)
            return duration

        except Exception as e:
            self.metrics.record_error(str(e))
            return time.perf_counter() - start_time

    async def run_concurrent_agents(self) -> Dict[str, Any]:
        """Run multiple agents concurrently."""
        self.metrics.start_time = datetime.now(UTC)

        # Start resource monitoring
        monitor_task = asyncio.create_task(self._monitor_resources())

        # Create agent tasks
        tasks = [
            self.simulate_agent_lifecycle(f"load_test_agent_{i}")
            for i in range(self.num_agents)
        ]

        # Execute concurrently
        await asyncio.gather(*tasks)

        self.metrics.end_time = datetime.now(UTC)
        monitor_task.cancel()

        return self.metrics.get_summary()

    async def _monitor_resources(self):
        """Continuously monitor resource usage."""
        try:
            while True:
                self.metrics.sample_resources()
                await asyncio.sleep(0.1)  # Sample every 100ms
        except asyncio.CancelledError:
            pass


# ============================================================================
# Load Test Cases
# ============================================================================

@pytest.mark.asyncio
async def test_load_10_agents():
    """Test with 10 concurrent agents (baseline)."""
    runner = LoadTestRunner(num_agents=10)
    summary = await runner.run_concurrent_agents()

    print("\n=== Load Test: 10 Agents ===")
    print(f"Throughput: {summary['throughput_ops_per_second']:.2f} ops/sec")
    print(f"Mean response time: {summary['response_time']['mean_ms']:.2f}ms")
    print(f"P95 response time: {summary['response_time']['p95_ms']:.2f}ms")
    print(f"Error rate: {summary['errors']['rate_percent']:.2f}%")

    # Assertions
    assert summary['errors']['rate_percent'] < 1.0, "Error rate too high"
    assert summary['response_time']['p95_ms'] < 500, "P95 latency too high"


@pytest.mark.asyncio
async def test_load_50_agents():
    """Test with 50 concurrent agents (moderate load)."""
    runner = LoadTestRunner(num_agents=50)
    summary = await runner.run_concurrent_agents()

    print("\n=== Load Test: 50 Agents ===")
    print(f"Throughput: {summary['throughput_ops_per_second']:.2f} ops/sec")
    print(f"Mean response time: {summary['response_time']['mean_ms']:.2f}ms")
    print(f"P95 response time: {summary['response_time']['p95_ms']:.2f}ms")
    print(f"P99 response time: {summary['response_time']['p99_ms']:.2f}ms")
    print(f"CPU avg: {summary['resource_usage']['cpu_avg_percent']:.1f}%")
    print(f"Memory avg: {summary['resource_usage']['memory_avg_mb']:.1f}MB")
    print(f"Error rate: {summary['errors']['rate_percent']:.2f}%")

    # Assertions
    assert summary['errors']['rate_percent'] < 1.0, "Error rate too high"
    assert summary['response_time']['p95_ms'] < 1000, "P95 latency too high"
    assert summary['resource_usage']['memory_avg_mb'] < 500, "Memory usage too high"


@pytest.mark.asyncio
async def test_load_100_agents():
    """Test with 100 concurrent agents (target production load)."""
    runner = LoadTestRunner(num_agents=100)
    summary = await runner.run_concurrent_agents()

    print("\n=== Load Test: 100 Agents ===")
    print(f"Total operations: {summary['total_operations']}")
    print(f"Total time: {summary['total_time_seconds']:.2f}s")
    print(f"Throughput: {summary['throughput_ops_per_second']:.2f} ops/sec")
    print(f"Mean response time: {summary['response_time']['mean_ms']:.2f}ms")
    print(f"Median response time: {summary['response_time']['median_ms']:.2f}ms")
    print(f"P95 response time: {summary['response_time']['p95_ms']:.2f}ms")
    print(f"P99 response time: {summary['response_time']['p99_ms']:.2f}ms")
    print(f"CPU avg: {summary['resource_usage']['cpu_avg_percent']:.1f}%")
    print(f"CPU max: {summary['resource_usage']['cpu_max_percent']:.1f}%")
    print(f"Memory avg: {summary['resource_usage']['memory_avg_mb']:.1f}MB")
    print(f"Memory max: {summary['resource_usage']['memory_max_mb']:.1f}MB")
    print(f"Error count: {summary['errors']['count']}")
    print(f"Error rate: {summary['errors']['rate_percent']:.2f}%")

    # Production-level assertions
    assert summary['errors']['rate_percent'] < 1.0, "Error rate exceeds 1%"
    assert summary['response_time']['mean_ms'] < 2000, "Mean response time > 2s"
    assert summary['response_time']['p95_ms'] < 3000, "P95 latency > 3s"
    assert summary['resource_usage']['memory_avg_mb'] < 2048, "Memory usage > 2GB"


@pytest.mark.asyncio
async def test_load_200_agents_stress():
    """Stress test with 200 concurrent agents."""
    runner = LoadTestRunner(num_agents=200)
    summary = await runner.run_concurrent_agents()

    print("\n=== Stress Test: 200 Agents ===")
    print(f"Throughput: {summary['throughput_ops_per_second']:.2f} ops/sec")
    print(f"P50: {summary['response_time']['p50_ms']:.2f}ms")
    print(f"P95: {summary['response_time']['p95_ms']:.2f}ms")
    print(f"P99: {summary['response_time']['p99_ms']:.2f}ms")
    print(f"Max response: {summary['response_time']['max_ms']:.2f}ms")
    print(f"CPU max: {summary['resource_usage']['cpu_max_percent']:.1f}%")
    print(f"Memory max: {summary['resource_usage']['memory_max_mb']:.1f}MB")
    print(f"Error rate: {summary['errors']['rate_percent']:.2f}%")

    # Stress test allows higher error rates
    assert summary['errors']['rate_percent'] < 5.0, "Error rate exceeds 5%"


# ============================================================================
# Database Performance Tests
# ============================================================================

@pytest.mark.asyncio
async def test_database_query_performance_under_load():
    """Test database query performance with concurrent operations."""
    db = SwarmDB()
    metrics = LoadTestMetrics()
    metrics.start_time = datetime.now(UTC)

    async def run_query():
        start = time.perf_counter()
        try:
            # Test query performance
            await asyncio.to_thread(
                db.get_active_agents,
                agent_type="load_test_agent"
            )
            metrics.record_response(time.perf_counter() - start)
        except Exception as e:
            metrics.record_error(str(e))

    # Run 1000 concurrent queries
    tasks = [run_query() for _ in range(1000)]
    await asyncio.gather(*tasks)

    metrics.end_time = datetime.now(UTC)
    summary = metrics.get_summary()

    print("\n=== Database Query Performance ===")
    print(f"Total queries: {summary['total_operations']}")
    print(f"Mean query time: {summary['response_time']['mean_ms']:.2f}ms")
    print(f"P95 query time: {summary['response_time']['p95_ms']:.2f}ms")
    print(f"Error rate: {summary['errors']['rate_percent']:.2f}%")

    # Database performance targets
    assert summary['response_time']['mean_ms'] < 20, "Mean query time > 20ms"
    assert summary['response_time']['p95_ms'] < 50, "P95 query time > 50ms"
    assert summary['errors']['rate_percent'] < 0.1, "Query error rate too high"


if __name__ == "__main__":
    """Run load tests directly for manual testing."""
    import sys

    async def run_all_tests():
        print("=" * 70)
        print("MoAI-Flow Production Load Testing")
        print("=" * 70)

        # Baseline
        runner = LoadTestRunner(num_agents=10)
        summary = await runner.run_concurrent_agents()
        print(f"\n✅ 10 agents: {summary['throughput_ops_per_second']:.2f} ops/sec")

        # Moderate
        runner = LoadTestRunner(num_agents=50)
        summary = await runner.run_concurrent_agents()
        print(f"✅ 50 agents: {summary['throughput_ops_per_second']:.2f} ops/sec")

        # Target
        runner = LoadTestRunner(num_agents=100)
        summary = await runner.run_concurrent_agents()
        print(f"✅ 100 agents: {summary['throughput_ops_per_second']:.2f} ops/sec")
        print(f"   P95 latency: {summary['response_time']['p95_ms']:.2f}ms")
        print(f"   Memory: {summary['resource_usage']['memory_avg_mb']:.1f}MB")

        # Stress
        runner = LoadTestRunner(num_agents=200)
        summary = await runner.run_concurrent_agents()
        print(f"✅ 200 agents (stress): {summary['throughput_ops_per_second']:.2f} ops/sec")
        print(f"   P99 latency: {summary['response_time']['p99_ms']:.2f}ms")

        print("\n" + "=" * 70)
        print("Load testing completed successfully!")
        print("=" * 70)

    asyncio.run(run_all_tests())
