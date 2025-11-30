# GitHub Health Metrics System (PRD-06)

## Overview

Comprehensive repository health tracking system that monitors 5 key metrics and provides overall health scoring with trend analysis.

## File Structure

```
moai_flow/github/
├── health_metrics.py           # Main implementation (~600 LOC)
├── __init__.py                 # Module exports
└── HEALTH_METRICS_README.md    # This file

moai_flow/examples/
└── github_health_example.py    # Usage examples

moai_flow/tests/
└── test_health_metrics.py      # Unit tests
```

## Features

### 1. Five Core Metric Calculators

#### `calculate_issue_velocity()`
- **Purpose**: Measures team productivity on issue management
- **Returns**: Issues closed per week (float)
- **Algorithm**:
  ```
  velocity = total_closed_issues / lookback_weeks
  ```
- **Usage**:
  ```python
  velocity = analyzer.calculate_issue_velocity(lookback_weeks=4)
  # Result: 8.5 issues/week
  ```

#### `calculate_pr_merge_time()`
- **Purpose**: Tracks PR review and merge efficiency
- **Returns**: Average days from PR creation to merge (float)
- **Algorithm**:
  ```
  merge_time = average(pr.merged_at - pr.created_at) in days
  ```
- **Usage**:
  ```python
  merge_time = analyzer.calculate_pr_merge_time(lookback_weeks=4)
  # Result: 2.3 days
  ```

#### `calculate_stale_count()`
- **Purpose**: Identifies neglected issues and PRs
- **Returns**: Total count of stale items (int)
- **Algorithm**:
  ```
  stale_count = count(items with updated_at < (now - stale_days))
  ```
- **Customization**: Configurable stale threshold (default: 60 days)
- **Usage**:
  ```python
  stale_count = analyzer.calculate_stale_count()
  # Result: 15 items
  ```

#### `calculate_contributor_activity()`
- **Purpose**: Measures team engagement and diversity
- **Returns**: Number of unique contributors with commits (int)
- **Algorithm**:
  ```
  activity = count(unique commit authors in period)
  ```
- **Usage**:
  ```python
  activity = analyzer.calculate_contributor_activity(lookback_weeks=4)
  # Result: 7 contributors
  ```

#### `calculate_test_coverage_trend()`
- **Purpose**: Tracks code quality over time
- **Returns**: Percentage change in test coverage (float)
- **Algorithm**: Compares coverage reports across time periods
- **Note**: Returns 0.0 if coverage data unavailable
- **Usage**:
  ```python
  trend = analyzer.calculate_test_coverage_trend(lookback_weeks=4)
  # Result: +1.5%
  ```

### 2. HealthMetrics Dataclass

Complete snapshot of repository health:

```python
@dataclass
class HealthMetrics:
    timestamp: datetime              # When calculated
    issue_velocity: float           # Issues/week
    pr_merge_time: float           # Days to merge
    stale_count: int               # Stale items
    contributor_activity: int      # Active contributors
    test_coverage_trend: float     # Coverage change %
    health_score: int              # 0-100 overall score
    trend: HealthTrend             # improving/stable/degrading

    # Optional detailed breakdowns
    issue_metrics: Dict[str, float]
    pr_metrics: Dict[str, float]
    contributor_metrics: Dict[str, int]
```

**Methods**:
- `to_dict()`: Export to JSON-serializable dictionary for storage

### 3. HealthTrend Analyzer

Compares current metrics with historical data:

```python
class HealthComparison:
    current: HealthMetrics
    previous: HealthMetrics
    change_percentage: float        # Health score change %
    trend: HealthTrend             # Overall direction
    improvements: List[str]        # Metrics that improved
    degradations: List[str]        # Metrics that degraded
```

**Trend Detection**:
- `IMPROVING`: Health score increased > 5%
- `STABLE`: Health score change within ±5%
- `DEGRADING`: Health score decreased > 5%

### 4. Health Score Calculation

Weighted scoring algorithm (0-100):

| Metric | Weight | Target | Score Range |
|--------|--------|--------|-------------|
| Issue Velocity | 25% | 10+ issues/week | 0-25 |
| PR Merge Time | 25% | ≤2 days | 0-25 |
| Stale Count | 20% | 0 items | 0-20 |
| Contributor Activity | 20% | 5+ contributors | 0-20 |
| Test Coverage Trend | 10% | Positive trend | 0-10 |

**Score Interpretation**:
- **80-100**: Excellent health (IMPROVING)
- **60-79**: Good health (STABLE)
- **40-59**: Fair health (STABLE/DEGRADING)
- **0-39**: Poor health (DEGRADING)

## Usage Examples

### Basic Health Metrics

```python
from moai_flow.github.health_metrics import HealthMetricsAnalyzer

# Initialize analyzer
analyzer = HealthMetricsAnalyzer(
    repo_owner="owner",
    repo_name="repo",
    github_token=os.getenv("GITHUB_TOKEN"),
    stale_days=60  # Custom threshold
)

# Calculate metrics for last 4 weeks
metrics = analyzer.calculate_health_metrics(lookback_weeks=4)

print(f"Health Score: {metrics.health_score}/100")
print(f"Trend: {metrics.trend.value}")
print(f"Issue Velocity: {metrics.issue_velocity} issues/week")
print(f"PR Merge Time: {metrics.pr_merge_time} days")
```

### Individual Metric Calculation

```python
# Calculate specific metrics
velocity = analyzer.calculate_issue_velocity(lookback_weeks=4)
merge_time = analyzer.calculate_pr_merge_time(lookback_weeks=4)
stale_count = analyzer.calculate_stale_count()
activity = analyzer.calculate_contributor_activity(lookback_weeks=4)
coverage = analyzer.calculate_test_coverage_trend(lookback_weeks=4)
```

### Trend Analysis

```python
# Compare with historical metrics
current = analyzer.calculate_health_metrics(lookback_weeks=4)
historical = load_historical_metrics()  # Load from storage

comparison = analyzer.analyze_trend(current, historical)

print(f"Trend: {comparison.trend.value}")
print(f"Change: {comparison.change_percentage:+.2f}%")
print(f"Improvements: {comparison.improvements}")
print(f"Degradations: {comparison.degradations}")
```

### Export for Storage

```python
# Export to JSON for storage
metrics = analyzer.calculate_health_metrics(lookback_weeks=4)
metrics_dict = metrics.to_dict()

# Save to file
import json
with open('.moai/reports/repo/health-metrics.json', 'w') as f:
    json.dump(metrics_dict, f, indent=2)
```

## Integration with PRD-06

This health metrics system supports the repository analysis phase of PRD-06:

1. **Automated Monitoring**: Scheduled health checks (daily/weekly)
2. **Trend Detection**: Early warning system for degrading health
3. **Actionable Insights**: Identifies specific areas needing attention
4. **Historical Tracking**: Build health history over time
5. **Report Generation**: Export metrics for dashboards and reports

## Testing

Run tests with:
```bash
pytest moai_flow/tests/test_health_metrics.py -v
```

Test coverage includes:
- ✅ Individual metric calculators
- ✅ HealthMetrics dataclass
- ✅ Health score calculation
- ✅ Trend analysis
- ✅ Integration tests

## Dependencies

- **PyGithub**: GitHub API client (`pip install PyGithub`)
- **Python 3.8+**: Standard library (datetime, dataclasses, statistics)

## Configuration

### Custom Stale Threshold

```python
# 30-day threshold (more aggressive)
analyzer = HealthMetricsAnalyzer(
    repo_owner="owner",
    repo_name="repo",
    github_token=token,
    stale_days=30
)

# 90-day threshold (more lenient)
analyzer = HealthMetricsAnalyzer(
    repo_owner="owner",
    repo_name="repo",
    github_token=token,
    stale_days=90
)
```

### Lookback Period

```python
# 2-week analysis (recent trends)
metrics = analyzer.calculate_health_metrics(lookback_weeks=2)

# 8-week analysis (longer term trends)
metrics = analyzer.calculate_health_metrics(lookback_weeks=8)
```

## Performance Considerations

- **API Rate Limits**: GitHub API has rate limits (5000 req/hour authenticated)
- **Data Volume**: Large repositories may require pagination
- **Caching**: Recommended for frequent queries
- **Async Support**: Consider async implementation for parallel requests

## Future Enhancements

Potential improvements:
1. Async API calls for better performance
2. Caching layer for frequently accessed data
3. Real-time coverage tracking integration
4. Machine learning for anomaly detection
5. Customizable scoring weights
6. Multi-repository health dashboards

## API Reference

See inline documentation in `health_metrics.py` for complete API reference.

## Examples

See `moai_flow/examples/github_health_example.py` for 6 comprehensive examples demonstrating all features.

## License

Part of MoAI-Flow GitHub integration module.

---

**Version**: 1.0.0
**PRD**: PRD-06 GitHub Enhancement
**Last Updated**: 2025-11-29
