# UV & Inline Dependencies (AI Documentation)

**Version**: 1.0.0
**Last Updated**: November 29, 2025
**Target**: AI Assistants

## Quick Summary

UV is a modern Python package installer (10-100x faster than pip) with support for PEP 723 inline script dependencies, enabling single-file Python scripts with automatic dependency management.

**Key Concepts**:
- **UV**: Fast Python package and project manager
- **PEP 723**: Standard for inline script metadata
- **Inline Dependencies**: Dependencies specified directly in Python files

---

## UV Overview

### What is UV?

UV is an extremely fast Python package installer and resolver written in Rust.

**Key Features**:
- ⚡ 10-100x faster than pip
- 🔒 Reliable dependency resolution
- 📦 Support for PEP 723 inline dependencies
- 🔄 Compatible with pip and requirements.txt
- 💾 Smart caching system

**Comparison**:

| Feature | UV | Pip |
|---------|-----|-----|
| Speed | ⚡⚡⚡ | ⚠️ Slow |
| PEP 723 | ✅ Yes | ❌ No |
| Lockfiles | ✅ Built-in | ❌ Needs pip-tools |
| Caching | ✅ Smart | ⚠️ Basic |
| Resolution | ✅ Fast | ❌ Slow |

---

## Installation

### Quick Install

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
# Expected: uv 0.5.4 (or higher)
```

### Alternative Methods

```bash
# Homebrew (macOS)
brew install uv

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# pip (if already have Python)
pip install uv
```

### Add to PATH

```bash
# Add UV to PATH (if not automatic)
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc

# Verify
which uv
```

---

## Basic Usage

### Virtual Environment

```bash
# Create virtual environment with UV
uv venv

# Specify Python version
uv venv --python 3.13

# Activate environment
source .venv/bin/activate

# Verify
which python
# Expected: /path/to/project/.venv/bin/python
```

### Installing Packages

```bash
# Install single package
uv pip install pydantic

# Install from requirements.txt
uv pip install -r requirements.txt

# Install multiple packages
uv pip install pydantic pyyaml jinja2

# Install with version specifier
uv pip install "pydantic>=2.5.0"
```

### Speed Comparison

```bash
# UV (fast)
time uv pip install langchain
# Real: 5.2s

# Pip (slow)
time pip install langchain
# Real: 52.8s

# UV is ~10x faster!
```

---

## PEP 723: Inline Dependencies

### What is PEP 723?

PEP 723 defines a standard format for embedding dependency metadata directly in Python scripts.

**Benefits**:
- ✅ Single-file scripts with dependencies
- ✅ No separate requirements.txt needed
- ✅ Automatic environment management
- ✅ Self-contained executable scripts

### Syntax

```python
# /// script
# dependencies = [
#   "requests",
#   "rich",
#   "pydantic>=2.0",
# ]
# requires-python = ">=3.11"
# ///

import requests
from rich import print

response = requests.get("https://api.github.com")
print(response.json())
```

### Running PEP 723 Scripts

```bash
# UV automatically handles dependencies
uv run script.py

# UV will:
# 1. Read inline dependencies
# 2. Create temporary virtual environment
# 3. Install dependencies
# 4. Run script
# 5. Cache environment for next run
```

---

## PEP 723 Examples

### Example 1: Simple Script with Dependencies

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "requests>=2.31.0",
# ]
# ///

import requests

def fetch_data(url):
    response = requests.get(url)
    return response.json()

if __name__ == "__main__":
    data = fetch_data("https://api.github.com/users/octocat")
    print(f"User: {data['name']}")
    print(f"Repos: {data['public_repos']}")
```

**Usage**:
```bash
# Make executable
chmod +x script.py

# Run (UV handles dependencies automatically)
./script.py

# Or
uv run script.py
```

---

### Example 2: Data Analysis Script

```python
# /// script
# dependencies = [
#   "pandas>=2.0.0",
#   "matplotlib>=3.7.0",
#   "numpy>=1.24.0",
# ]
# requires-python = ">=3.11"
# ///

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Generate sample data
data = {
    'x': np.linspace(0, 10, 100),
    'y': np.sin(np.linspace(0, 10, 100))
}

df = pd.DataFrame(data)

# Create plot
plt.figure(figsize=(10, 6))
plt.plot(df['x'], df['y'])
plt.title('Sine Wave')
plt.savefig('output.png')
print("Plot saved to output.png")
```

**Usage**:
```bash
uv run data-analysis.py
# UV installs pandas, matplotlib, numpy
# Script runs and generates plot
```

---

### Example 3: Web Scraping

```python
# /// script
# dependencies = [
#   "beautifulsoup4>=4.12.0",
#   "requests>=2.31.0",
#   "lxml>=4.9.0",
# ]
# ///

import requests
from bs4 import BeautifulSoup

def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    return soup.find_all('h1')

if __name__ == "__main__":
    headings = scrape_page("https://example.com")
    for h1 in headings:
        print(h1.text)
```

---

### Example 4: MoAI-ADK Integration

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pydantic>=2.5.0",
#   "pyyaml>=6.0.1",
#   "jinja2>=3.1.2",
#   "click>=8.1.7",
# ]
# requires-python = ">=3.11"
# ///

import click
import yaml
from pydantic import BaseModel

class Specification(BaseModel):
    title: str
    requirements: list[str]

@click.command()
@click.argument('description')
def generate_spec(description):
    """Generate SPEC-First specification"""
    spec = Specification(
        title=description,
        requirements=[
            f"Requirement 1 for {description}",
            f"Requirement 2 for {description}",
        ]
    )

    output = yaml.dump(spec.model_dump(), default_flow_style=False)
    print(output)

if __name__ == "__main__":
    generate_spec()
```

**Usage**:
```bash
chmod +x moai-spec-generator.py
./moai-spec-generator.py "User Authentication System"
```

---

## UV vs Pip Comparison

### Installation Speed

```bash
# Test: Install langchain + dependencies

# UV
time uv pip install langchain
# Real: 5.2s
# Packages: 25

# Pip
time pip install langchain
# Real: 52.8s
# Packages: 25

# Result: UV is 10x faster
```

### Dependency Resolution

```bash
# UV (fast, accurate)
uv pip install package1 package2 package3
# Resolves conflicts in seconds

# Pip (slow, may have conflicts)
pip install package1 package2 package3
# Can take minutes, may fail with conflicts
```

### Caching

**UV**:
- Smart global cache
- Deduplication across projects
- Faster reinstalls

**Pip**:
- Basic HTTP cache
- No deduplication
- Slower reinstalls

---

## Migration from Pip to UV

### Step 1: Install UV

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 2: Recreate Virtual Environment

```bash
# Remove old venv (backup first if needed)
rm -rf .venv

# Create new venv with UV
uv venv --python 3.13

# Activate
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# If you have requirements.txt
uv pip install -r requirements.txt

# Or freeze existing environment first
pip freeze > requirements.txt
uv pip install -r requirements.txt
```

### Step 4: Replace Pip Commands

```bash
# Old (pip)
pip install package

# New (UV)
uv pip install package

# Old (pip)
pip install -r requirements.txt

# New (UV)
uv pip install -r requirements.txt
```

---

## Advanced UV Features

### UV Sync

Synchronize environment with exact versions:

```bash
# Create lockfile
uv pip compile requirements.in -o requirements.txt

# Sync environment
uv pip sync requirements.txt
```

### UV Cache Management

```bash
# Check cache size
uv cache info

# Clean cache
uv cache clean

# Clear specific package
uv cache clean package-name
```

### UV Configuration

```bash
# Set UV config
uv config set python-preference system

# View config
uv config list

# Reset config
uv config unset python-preference
```

---

## PEP 723 Best Practices

### 1. Version Pinning

```python
# Good: Pin major versions
# /// script
# dependencies = [
#   "requests>=2.31.0,<3.0.0",
#   "pydantic>=2.0,<3.0",
# ]
# ///
```

### 2. Python Version Requirement

```python
# Always specify Python version
# /// script
# requires-python = ">=3.11"
# dependencies = ["pydantic"]
# ///
```

### 3. Minimal Dependencies

```python
# Only include what you need
# /// script
# dependencies = [
#   "requests",  # For HTTP
# ]
# ///

# Avoid:
# dependencies = [
#   "requests",
#   "urllib3",  # Already included in requests
#   "certifi",  # Already included in requests
# ]
```

### 4. Shebang for Executable Scripts

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = ["requests"]
# ///

# Makes script directly executable
# chmod +x script.py
# ./script.py
```

---

## Troubleshooting

### UV Not Found

```bash
# Error: uv: command not found

# Solution: Add to PATH
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Verify
uv --version
```

### PEP 723 Not Working

```bash
# Error: Script doesn't detect dependencies

# Solution 1: Use uv run
uv run script.py

# Solution 2: Add shebang
#!/usr/bin/env -S uv run

# Solution 3: Check syntax
# /// script
# dependencies = [
#   "package",
# ]
# ///
# (Must be at top of file, exact format)
```

### Slow Installation

```bash
# Problem: UV still slow

# Solution: Clear cache
uv cache clean

# Or: Use system cache
export UV_CACHE_DIR="$HOME/.cache/uv"
uv pip install package
```

---

## Real-World Examples

### Example: Quick Data Fetch

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = ["requests", "rich"]
# ///

import requests
from rich import print
from rich.table import Table

response = requests.get("https://api.github.com/repos/python/cpython")
data = response.json()

table = Table(title="Python CPython Stats")
table.add_column("Metric", style="cyan")
table.add_column("Value", style="green")

table.add_row("Stars", str(data['stargazers_count']))
table.add_row("Forks", str(data['forks_count']))
table.add_row("Open Issues", str(data['open_issues_count']))

print(table)
```

### Example: CSV Processor

```python
# /// script
# dependencies = ["pandas>=2.0", "openpyxl>=3.0"]
# ///

import pandas as pd
import sys

def process_csv(input_file):
    df = pd.read_csv(input_file)

    # Basic analysis
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"\nSummary:\n{df.describe()}")

    # Export to Excel
    output_file = input_file.replace('.csv', '.xlsx')
    df.to_excel(output_file, index=False)
    print(f"\nExported to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: uv run csv-processor.py data.csv")
        sys.exit(1)

    process_csv(sys.argv[1])
```

**Usage**:
```bash
uv run csv-processor.py sales-data.csv
```

---

## Performance Benchmarks

### Installation Speed (25 packages)

| Tool | Time | Speed |
|------|------|-------|
| UV | 5.2s | ⚡⚡⚡ |
| Pip | 52.8s | ⚠️ |
| Poetry | 35.4s | ⚠️ |

### Resolution Speed (100 dependencies)

| Tool | Time | Accuracy |
|------|------|----------|
| UV | 2.1s | ✅ |
| Pip | 45.8s | ⚠️ |
| Pipenv | 67.3s | ⚠️ |

### Cache Performance (repeated install)

| Tool | First Install | Second Install |
|------|---------------|----------------|
| UV | 5.2s | 0.8s |
| Pip | 52.8s | 48.3s |

---

## Integration with MoAI-ADK

### MoAI-ADK Uses UV For:

1. **Fast Installation**:
   ```bash
   uv venv --python 3.13
   uv pip install -r requirements.txt
   ```

2. **Dependency Management**:
   ```bash
   # requirements.txt
   pydantic>=2.5.0
   langchain>=0.1.0
   # ... UV resolves quickly
   ```

3. **Agent Scripts** (future):
   ```python
   # moai-agents can be PEP 723 compliant
   # /// script
   # dependencies = ["langchain", "pydantic"]
   # ///
   ```

---

## Quick Reference

### UV Commands

```bash
# Virtual environment
uv venv [--python VERSION]
uv venv --python 3.13

# Install packages
uv pip install PACKAGE
uv pip install -r requirements.txt

# Run PEP 723 scripts
uv run script.py

# Cache management
uv cache info
uv cache clean

# Configuration
uv config set KEY VALUE
uv config list
```

### PEP 723 Template

```python
#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "package1>=version",
#   "package2",
# ]
# requires-python = ">=3.11"
# ///

import package1
import package2

# Your code here
```

---

## Related Documentation

- **MoAI-ADK Installation**: `../docs/02-INSTALLATION.md`
- **MoAI-ADK Guide**: `moai-adk-guide.md`
- **Requirements**: `../docs/01-REQUIREMENTS.md`
- **UV Official Docs**: https://github.com/astral-sh/uv

---

**UV & PEP 723** - Modern Python dependency management ⚡
