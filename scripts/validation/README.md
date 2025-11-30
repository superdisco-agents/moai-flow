# Validation Scripts

Scripts for validation and verification of code, configuration, and dependencies.

## Available Scripts

### validate_config.py
Validate configuration files.

```bash
python scripts/validation/validate_config.py
python scripts/validation/validate_config.py --strict
```

### check_code_quality.py
Check code quality with linters and static analyzers.

```bash
python scripts/validation/check_code_quality.py
python scripts/validation/check_code_quality.py --fix
```

### audit_dependencies.py
Audit dependencies for security vulnerabilities.

```bash
python scripts/validation/audit_dependencies.py
python scripts/validation/audit_dependencies.py --report
```

### verify_structure.py
Verify package structure and organization.

```bash
python scripts/validation/verify_structure.py
```

### check_test_coverage.py
Verify test coverage meets requirements.

```bash
python scripts/validation/check_test_coverage.py
python scripts/validation/check_test_coverage.py --threshold 90
```

## Usage Examples

### Pre-release Validation

```bash
# Validate configuration
python scripts/validation/validate_config.py --strict

# Check code quality
python scripts/validation/check_code_quality.py

# Audit dependencies
python scripts/validation/audit_dependencies.py --report

# Verify structure
python scripts/validation/verify_structure.py

# Check coverage
python scripts/validation/check_test_coverage.py --threshold 90
```

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Validate
  run: |
    python scripts/validation/validate_config.py
    python scripts/validation/check_code_quality.py
    python scripts/validation/check_test_coverage.py
```
