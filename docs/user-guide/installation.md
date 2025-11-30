# Installation Guide

Complete installation instructions for MoAI Flow.

## Requirements

- Python 3.8 or higher
- pip or poetry for package management

## Installation Methods

### Using pip (Recommended)

```bash
pip install moai-flow
```

### Using poetry

```bash
poetry add moai-flow
```

### From Source

```bash
# Clone the repository
git clone https://github.com/your-org/moai-flow
cd moai-flow

# Install dependencies
pip install -e .

# Or with poetry
poetry install
```

## Verify Installation

```python
import moai_flow
print(moai_flow.__version__)
```

## Optional Dependencies

### Development Dependencies

```bash
pip install moai-flow[dev]
```

Includes:
- pytest for testing
- black for formatting
- mypy for type checking
- ruff for linting

### Documentation Dependencies

```bash
pip install moai-flow[docs]
```

Includes:
- sphinx for documentation generation
- sphinx-rtd-theme for documentation theme

### All Dependencies

```bash
pip install moai-flow[all]
```

## Next Steps

- Follow the [Quick Start Guide](quickstart.md)
- Review [Configuration Guide](configuration.md)
- Explore [Examples](../../examples/)
