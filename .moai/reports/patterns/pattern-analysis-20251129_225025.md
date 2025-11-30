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
| expert-frontend | 28 | 75.0% | 36.8s | 56 |
| manager-tdd | 28 | 100.0% | 29.8s | 84 |
| expert-database | 28 | 100.0% | 42.4s | 112 |
| expert-devops | 28 | 100.0% | 53.8s | 140 |

## Error Patterns

- **TypeError**: 14 occurrences
- **NetworkError**: 7 occurrences

## Task Patterns

| Pattern | Occurrences | Avg Duration | Success Rate |
|---------|-------------|--------------|--------------|
| api_implementation | 28 | 52.5s | 50.0% |
| database_migration | 28 | 36.8s | 75.0% |
| test_creation | 28 | 29.8s | 100.0% |
| frontend_component | 28 | 42.4s | 100.0% |
| deployment_script | 28 | 53.8s | 100.0% |

## Recommendations

1. expert-backend has low success rate (50.0%) - review error handling and test coverage
2. expert-frontend has low success rate (75.0%) - review error handling and test coverage
3. TypeError errors frequent (14 occurrences) - implement specific handling or prevention
4. NetworkError errors frequent (7 occurrences) - implement specific handling or prevention
5. api_implementation pattern has low success rate (50.0%) - review implementation
6. database_migration pattern has low success rate (75.0%) - review implementation
