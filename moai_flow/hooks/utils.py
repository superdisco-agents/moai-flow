"""
Coordination utility functions for moai-flow hooks.
"""

def validate_topology(topology: str) -> bool:
    """Validate topology type."""
    valid_topologies = {"hierarchical", "mesh", "star", "ring", "adaptive"}
    return topology in valid_topologies

def get_default_config():
    """Get default swarm configuration."""
    return {
        "topology": "adaptive",
        "agent_count": 3,
        "consensus_timeout_ms": 5000
    }
"""
Metrics utility functions for moai-flow hooks.
"""

from typing import Dict, Any

def format_metrics(metrics: Dict[str, Any]) -> str:
    """Format metrics for display."""
    lines = []
    for key, value in metrics.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)

def calculate_performance_score(metrics: Dict[str, Any]) -> float:
    """Calculate overall performance score from metrics."""
    # Simple scoring based on throughput and latency
    throughput = metrics.get("throughput", 0)
    latency = metrics.get("latency_ms", 1000)

    # Score = throughput / latency (higher is better)
    return throughput / max(latency, 1)
