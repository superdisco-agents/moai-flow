"""
Post-task hook for moai-flow swarm coordination.
Collects metrics and applies self-healing after task execution.
"""

import sys
from pathlib import Path

moai_flow_path = Path(__file__).parent.parent.parent.parent / "moai_flow"
if moai_flow_path.exists():
    sys.path.insert(0, str(moai_flow_path.parent))

def execute(context):
    """
    Execute post-task metrics collection and healing.

    Args:
        context: Task context with metadata and results

    Returns:
        dict: Metrics and healing status
    """
    try:
        from moai_flow.optimization.auto_healer import AutoHealer
        from moai_flow.monitoring.metrics_collector import MetricsCollector

        # Collect task metrics
        if context.get("swarm_active"):
            from datetime import datetime
            from pathlib import Path
            import json

            collector = MetricsCollector()
            metrics = collector.collect_task_metrics(context)

            # Check for anomalies and apply healing
            healer = AutoHealer()
            healing_result = healer.check_and_heal(metrics)

            # Persist metrics to .moai/memory/moai-flow/
            metrics_file = Path(".moai/memory/moai-flow/latest-metrics.json")
            metrics_file.parent.mkdir(parents=True, exist_ok=True)
            with metrics_file.open("w") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "metrics": metrics,
                    "healing": healing_result
                }, f, indent=2)

            return {
                "success": True,
                "metrics": metrics,
                "healing": healing_result,
                "persisted": str(metrics_file)
            }

        return {"success": True, "skipped": "swarm not active"}

    except Exception as e:
        return {"success": False, "error": str(e)}
