# Code Style & Best Practices

> Claude-Flow's development standards and quality guidelines

## Overview

Claude-Flow defines specific code style rules for maintaining code quality and consistency.

---

## Claude-Flow Standards

### 1. Modular Design

```
📏 Files under 500 lines
```

- Break large files into smaller modules
- Single responsibility per file
- Clear module boundaries

### 2. Environment Safety

```
🔐 Never hardcode secrets
```

- Use environment variables
- Never commit credentials
- Validate at system boundaries

### 3. Test-First Development

```
🧪 Write tests before implementation
```

- TDD (Test-Driven Development)
- Tests guide design
- Coverage before shipping

### 4. Clean Architecture

```
🏗️ Separate concerns
```

- Clear layer boundaries
- Dependency injection
- Interface segregation

### 5. Documentation

```
📚 Keep documentation updated
```

- Document as you code
- Update on changes
- Clear API documentation

---

## MoAI Comparison

MoAI has these principles embedded in its constitution and agents:

### Constitution (config.json)

```json
{
  "constitution": {
    "enforce_tdd": true,
    "test_coverage_target": 90
  }
}
```

### TRUST 5 Principles (from manager-quality)

1. **T**estability - Comprehensive test coverage
2. **R**eadability - Clear, maintainable code
3. **U**sability - Developer-friendly interfaces
4. **S**curity - Secure by design
5. **T**raceability - Audit trails and logging

### Code Style via Agents

- `manager-quality`: Enforces quality gates
- `expert-security`: Security reviews
- `manager-tdd`: TDD implementation

---

## Comparison Table

| Principle | Claude-Flow | MoAI |
|-----------|-------------|------|
| File Size | 500 lines max | No explicit limit |
| TDD | Recommended | **Enforced** (constitution) |
| Coverage | Not specified | **90% target** |
| Security | Environment safety | TRUST 5 + expert-security |
| Architecture | Clean architecture | Domain-driven agents |
| Documentation | Keep updated | Auto-generated via /moai:3-sync |

---

## MoAI Advantages

1. **Enforced TDD**: Constitution-level enforcement
2. **Measurable Coverage**: 90% target in config
3. **Specialized Agents**: expert-security, manager-quality
4. **TRUST 5 Framework**: Comprehensive quality principles
5. **Automated Docs**: /moai:3-sync for documentation

---

## Potential Enhancement

Add explicit file size limit to MoAI:

```json
{
  "code_style": {
    "max_file_lines": 500,
    "max_function_lines": 50,
    "enforce_single_responsibility": true
  }
}
```

---

## Best Practices Summary

| Category | Rule |
|----------|------|
| Size | Keep files < 500 lines |
| Secrets | Never hardcode, use env vars |
| Testing | Write tests first (TDD) |
| Coverage | Target 90%+ |
| Security | Validate at boundaries |
| Docs | Update with code changes |
