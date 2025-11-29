# MoAI-Flow Pattern Analysis Scripts

**PRD-05 Phase 2: Pattern Analysis**

Analyze collected patterns and generate reports WITHOUT ML.

---

## Features

✅ **Agent Performance Analysis**
- Task completion metrics
- Success rate tracking
- Duration analysis
- File modification counts
- Token usage tracking

✅ **Error Pattern Detection**
- Error type frequency analysis
- Trend identification
- Severity categorization

✅ **Task Pattern Recognition**
- Common workflow detection
- Performance benchmarking
- Success rate analysis

✅ **Actionable Recommendations**
- AI-generated insights
- Performance optimization suggestions
- Error mitigation strategies

✅ **Multi-Format Reporting**
- JSON output (machine-readable)
- Markdown output (human-readable)
- Configurable retention policies

---

## Quick Start

### 1. Basic Usage

```bash
# Analyze last 7 days (default)
python -m moai_flow.scripts.analyze_patterns

# Analyze last 30 days
python -m moai_flow.scripts.analyze_patterns --days 30

# Generate markdown report only
python -m moai_flow.scripts.analyze_patterns --format markdown

# Generate both JSON and markdown
python -m moai_flow.scripts.analyze_patterns --format both
```

### 2. Custom Output Location

```bash
# Save to custom directory
python -m moai_flow.scripts.analyze_patterns --output /path/to/reports/
```

### 3. Verbose Mode

```bash
# Enable detailed logging
python -m moai_flow.scripts.analyze_patterns --verbose
```

---

## Usage Examples

### Example 1: Weekly Performance Report

```bash
# Generate weekly report
python -m moai_flow.scripts.analyze_patterns --days 7 --format both
```

**Output**:
```
Summary (7 days):
  Total tasks: 140
  Success rate: 85.0%
  Avg duration: 43.0s

Top recommendations:
  1. expert-backend has low success rate (50.0%) - review error handling and test coverage
  2. TypeError errors frequent (14 occurrences) - implement specific handling or prevention
  3. api_implementation pattern has low success rate (50.0%) - review implementation

Full report saved to: .moai/reports/patterns/pattern-analysis-20251129_225025.json, .moai/reports/patterns/pattern-analysis-20251129_225025.md
```

### Example 2: Monthly Analysis

```bash
# Generate monthly report with verbose logging
python -m moai_flow.scripts.analyze_patterns --days 30 --format both --verbose
```

### Example 3: Test with Sample Data

```bash
# Run test script with synthetic data
python -m moai_flow.scripts.test_analyze_patterns
```

---

## Report Formats

### JSON Report

**File**: `pattern-analysis-{timestamp}.json`

```json
{
  "period": "weekly",
  "date_range": "2025-11-22 to 2025-11-29",
  "generated_at": "2025-11-29T22:50:25.932230",
  "summary": {
    "total_tasks": 140,
    "success_rate": 0.85,
    "avg_duration_ms": 43040.0
  },
  "by_agent": {
    "expert-backend": {
      "tasks": 28,
      "success_rate": 0.5,
      "avg_duration_ms": 52500,
      "median_duration_ms": 52500.0,
      "total_files_created": 28,
      "total_tokens_used": 630000
    }
  },
  "errors": {
    "TypeError": 14,
    "NetworkError": 7
  },
  "patterns_observed": [
    {
      "pattern": "api_implementation",
      "occurrences": 28,
      "avg_duration_ms": 52500,
      "success_rate": 0.5
    }
  ],
  "recommendations": [
    "expert-backend has low success rate (50.0%) - review error handling and test coverage"
  ]
}
```

### Markdown Report

**File**: `pattern-analysis-{timestamp}.md`

```markdown
# Pattern Analysis Report

**Period**: weekly
**Date Range**: 2025-11-22 to 2025-11-29
**Generated**: 2025-11-29T22:50:25.932230

## Summary

- **Total Tasks**: 140
- **Success Rate**: 85.0%
- **Average Duration**: 43.0s

## Agent Performance

| Agent ID | Tasks | Success Rate | Avg Duration | Files Created |
|----------|-------|--------------|--------------|---------------|
| expert-backend | 28 | 50.0% | 52.5s | 28 |
| manager-tdd | 28 | 100.0% | 29.8s | 84 |

## Recommendations

1. expert-backend has low success rate (50.0%) - review error handling and test coverage
2. TypeError errors frequent (14 occurrences) - implement specific handling or prevention
```

---

## Configuration

### config.json Integration

Add to `.moai/config/config.json`:

```json
{
  "patterns": {
    "analysis": {
      "enabled": true,
      "schedule": "weekly",
      "report_location": ".moai/reports/patterns/",
      "format": "both",
      "retention_days": 90
    }
  }
}
```

**Options**:
- `enabled`: Enable/disable pattern analysis
- `schedule`: `daily`, `weekly`, or `monthly`
- `report_location`: Output directory
- `format`: `json`, `markdown`, or `both`
- `retention_days`: Report retention period

---

## API Reference

### PatternAnalyzer

```python
from moai_flow.scripts.analyze_patterns import PatternAnalyzer
from moai_flow.monitoring.metrics_collector import MetricsCollector

collector = MetricsCollector()
analyzer = PatternAnalyzer(collector)

# Analyze agent performance
agent_perf = analyzer.analyze_agent_performance(days=7)
# Returns: Dict[agent_id, performance_data]

# Analyze error patterns
errors = analyzer.analyze_error_patterns(days=7)
# Returns: Dict[error_type, count]

# Analyze task patterns
tasks = analyzer.analyze_task_patterns(days=7)
# Returns: List[pattern_data]

# Generate recommendations
recs = analyzer.generate_recommendations({
    "agent_performance": agent_perf,
    "errors": errors,
    "tasks": tasks
})
# Returns: List[recommendation_string]
```

### ReportGenerator

```python
from moai_flow.scripts.analyze_patterns import ReportGenerator

reporter = ReportGenerator(analyzer)

# Generate weekly report
report = reporter.generate_weekly_report()
# Returns: Dict[report_data]

# Save report
output_file = reporter.save_report(
    report,
    output_path=".moai/reports/patterns/",
    format="both"
)
# Returns: str (file path)
```

---

## CLI Arguments

```
usage: analyze_patterns.py [-h] [--days DAYS] [--format {json,markdown,both}]
                           [--output OUTPUT] [--verbose]

Analyze MoAI patterns

optional arguments:
  -h, --help            show this help message and exit
  --days DAYS           Analysis period in days (default: 7)
  --format {json,markdown,both}
                        Report format (default: both)
  --output OUTPUT       Output directory (default: .moai/reports/patterns/)
  --verbose             Enable verbose logging
```

---

## Development

### Running Tests

```bash
# Run test script with sample data
python -m moai_flow.scripts.test_analyze_patterns
```

### Adding Custom Analysis

1. Extend `PatternAnalyzer` class
2. Add new analysis method
3. Update `generate_recommendations()` logic
4. Update report generation

Example:

```python
class PatternAnalyzer:
    def analyze_token_efficiency(self, days: int = 7) -> Dict[str, float]:
        """Analyze token usage efficiency per agent"""
        # Your implementation
        pass
```

---

## Troubleshooting

### No Data Found

**Issue**: "No metrics data available for analysis"

**Solution**:
1. Ensure MetricsCollector is enabled in config
2. Check `.moai/logs/sessions/` for metric data
3. Run test script to verify functionality

### Permission Errors

**Issue**: "Permission denied writing to .moai/reports/patterns/"

**Solution**:
```bash
# Create directory with proper permissions
mkdir -p .moai/reports/patterns/
chmod 755 .moai/reports/patterns/
```

### Module Not Found

**Issue**: "ModuleNotFoundError: No module named 'moai_flow'"

**Solution**:
```bash
# Run from project root
cd /path/to/moai-adk/
python -m moai_flow.scripts.analyze_patterns
```

---

## Integration

### With SessionEnd Hook

Automatically run analysis at session end:

```python
# In .claude/hooks/session-end.py
from moai_flow.scripts.analyze_patterns import PatternAnalyzer, ReportGenerator
from moai_flow.monitoring.metrics_collector import MetricsCollector

def run_pattern_analysis():
    collector = MetricsCollector()
    analyzer = PatternAnalyzer(collector)
    reporter = ReportGenerator(analyzer)

    report = reporter.generate_weekly_report()
    reporter.save_report(report, format="both")
```

### With Scheduled Tasks

```bash
# crontab entry for weekly analysis
0 9 * * 1 cd /path/to/moai-adk && python -m moai_flow.scripts.analyze_patterns --days 7
```

---

## File Structure

```
moai_flow/scripts/
├── __init__.py                   # Module exports
├── analyze_patterns.py           # Main pattern analysis script (200 LOC)
├── test_analyze_patterns.py      # Test script with sample data
└── README.md                     # This file

.moai/reports/patterns/
├── pattern-analysis-{timestamp}.json    # JSON reports
└── pattern-analysis-{timestamp}.md      # Markdown reports
```

---

## Metrics Collected

### Task Metrics
- `task_id`: Unique task identifier
- `agent_id`: Agent that executed task
- `duration_ms`: Execution duration
- `result`: SUCCESS, FAILURE, PARTIAL, TIMEOUT
- `tokens_used`: Total tokens consumed
- `files_changed`: Number of files modified
- `metadata`: Additional task context

### Agent Metrics
- `agent_id`: Agent identifier
- `tasks_completed`: Total tasks
- `success_rate`: Percentage of successful tasks
- `avg_duration_ms`: Average execution time
- `error_rate`: Percentage of failed tasks

### Pattern Metrics
- `pattern`: Pattern name (e.g., "api_implementation")
- `occurrences`: Number of times pattern used
- `avg_duration_ms`: Average execution time
- `success_rate`: Pattern success rate

---

## Future Enhancements

### Planned (PRD-05 Phase 3)
- 📊 Visual dashboards (Plotly/Dash)
- 🔮 Predictive analytics (trend forecasting)
- 📧 Email report delivery
- 🔔 Slack integration for alerts
- 📈 Real-time metrics streaming

### Under Consideration
- Machine learning anomaly detection
- Cross-project pattern comparison
- Custom metric definitions
- Export to external analytics platforms

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review sample test script (`test_analyze_patterns.py`)
3. Enable `--verbose` mode for detailed logs
4. Submit feedback via `/moai:9-feedback`

---

**Version**: 1.0.0
**Phase**: PRD-05 Phase 2
**Last Updated**: 2025-11-29
**Status**: Production Ready ✅
