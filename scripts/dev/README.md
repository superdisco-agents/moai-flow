# Development Scripts

Utility scripts for development workflows.

## Available Scripts

### setup_dev_environment.py
Set up development environment with all dependencies.

```bash
python scripts/dev/setup_dev_environment.py
```

### run_tests.py
Run test suite with coverage reporting.

```bash
python scripts/dev/run_tests.py
python scripts/dev/run_tests.py --unit
python scripts/dev/run_tests.py --integration
```

### format_code.py
Format code using black and ruff.

```bash
python scripts/dev/format_code.py
python scripts/dev/format_code.py --check
```

### type_check.py
Run type checking with mypy.

```bash
python scripts/dev/type_check.py
```

## Usage Examples

### Full Development Setup

```bash
# Set up environment
python scripts/dev/setup_dev_environment.py

# Run tests
python scripts/dev/run_tests.py

# Format code
python scripts/dev/format_code.py

# Type check
python scripts/dev/type_check.py
```

### Pre-commit Workflow

```bash
# Format and check
python scripts/dev/format_code.py
python scripts/dev/type_check.py
python scripts/dev/run_tests.py --quick
```
