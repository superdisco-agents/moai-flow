# Directory Activity Scoring - Quick Start Guide

## 5-Minute Quick Start

### Python Version

```bash
# Basic usage - score current directory
cd .claude/lib/scoring
python3 scoring.py .

# Score a specific project
python3 scoring.py /path/to/project

# Get JSON output for scripting
python3 scoring.py --format json /path/to/project

# Show detailed breakdown
python3 scoring.py --verbose /path/to/project
```

### Bash Version (Requires Bash 4+)

```bash
# Check bash version
bash --version

# macOS users: install bash 4+
brew install bash

# Score a directory
/usr/local/bin/bash scoring.sh /path/to/project

# JSON output
/usr/local/bin/bash scoring.sh /path/to/project --format json
```

## Understanding Scores

| Score | Classification | Meaning |
|-------|---------------|---------|
| ≥ 20  | **Active** | Keep - actively developed |
| 0-19  | **Borderline** | Review - may be important |
| < 0   | **Archivable** | Consider archiving |

## Common Use Cases

### 1. Find Archivable Projects

```bash
# Find directories that can be archived
for dir in */; do
    score=$(python3 scoring.py "$dir" --format json | jq -r '.total_score')
    if (( $(echo "$score < 0" | bc -l) )); then
        echo "Archivable: $dir (score: $score)"
    fi
done
```

### 2. Generate Workspace Report

```python
from scoring import DirectoryScorer
from pathlib import Path

scorer = DirectoryScorer()
workspace = Path(".")

scores = []
for dir_path in workspace.iterdir():
    if dir_path.is_dir() and not dir_path.name.startswith("."):
        scores.append(scorer.score_directory(str(dir_path)))

# Print markdown report
print(scorer.export_results(scores, "markdown"))
```

### 3. Custom Thresholds for Your Team

```python
from scoring import DirectoryScorer, ScoringConfig

config = ScoringConfig()
config.ACTIVE_THRESHOLD = 25  # Stricter active threshold
config.WEIGHTS["git_activity"] = 3.0  # Emphasize git activity

scorer = DirectoryScorer(config)
score = scorer.score_directory("/path/to/project")
```

## What Gets Scored?

### 🟢 Increases Score
- Recent file modifications (last 7-30 days)
- Git commits, branches, uncommitted changes
- Dependency files (package.json, requirements.txt, etc.)
- Documentation (README, docs/)
- Source code files (.py, .js, .ts, etc.)
- Standard project structure (src/, test/, docs/)
- CI/CD configuration

### 🔴 Decreases Score
- Very old modifications (90+ days)
- No git activity
- Missing documentation
- Empty or minimal file structure

### 🔒 Always Protected
These paths never score as "Archivable":
- `.git`, `.claude`
- `node_modules`, `.venv`
- `dist`, `build`, `.next`

## Quick Examples

### Score Multiple Projects

```bash
python3 scoring.py ~/projects/proj1 ~/projects/proj2 ~/projects/proj3 --format csv > scores.csv
```

### Find Projects by Type

```python
from scoring import DirectoryScorer
from pathlib import Path

scorer = DirectoryScorer()
workspace = Path("~/projects").expanduser()

node_projects = []
for dir_path in workspace.iterdir():
    if dir_path.is_dir():
        score = scorer.score_directory(str(dir_path))
        if score.project_type == "node":
            node_projects.append((dir_path.name, score.total_score))

# Print sorted by score
for name, score in sorted(node_projects, key=lambda x: x[1], reverse=True):
    print(f"{name:30s} {score:>8.2f}")
```

### Automated Cleanup Warning

```bash
#!/bin/bash
# Warn about archivable directories

cd ~/workspace
for dir in */; do
    python3 scoring.py "$dir" > /dev/null 2>&1
    exit_code=$?

    if [ $exit_code -eq 2 ]; then
        echo "⚠️  WARNING: $dir may be archivable"
    fi
done
```

## Integration Examples

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
# Warn if committing to a low-activity project

score=$(python3 /path/to/scoring.py . --format json | jq -r '.total_score')

if (( $(echo "$score < 10" | bc -l) )); then
    echo "⚠️  This project has low activity (score: $score)"
    echo "Consider if this commit is still relevant"
    read -p "Continue commit? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
```

### CI/CD Integration

```yaml
# .github/workflows/check-activity.yml
name: Check Project Activity

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Check activity score
        run: |
          python3 .claude/lib/scoring/scoring.py . --format json > score.json
          score=$(jq -r '.total_score' score.json)

          if (( $(echo "$score < 5" | bc -l) )); then
            echo "::warning::Project activity is very low (score: $score)"
          fi
```

### Claude Skill Integration

```yaml
# .claude/skills/check-workspace-activity.yaml
name: check-workspace-activity
version: 1.0.0
description: Score all directories in workspace and suggest cleanup

prompts:
  check:
    - role: system
      content: |
        Use the directory scoring algorithm to analyze all projects in the workspace.

        For each directory:
        1. Run: python3 .claude/lib/scoring/scoring.py <dir> --format json
        2. Parse the results
        3. Categorize as Active/Borderline/Archivable

        Generate a report with:
        - Summary statistics
        - List of archivable projects
        - Recommendations for cleanup
```

## Troubleshooting

### "Not a directory" error
```bash
# Ensure you're passing a directory path, not a file
python3 scoring.py /path/to/directory  # ✅
python3 scoring.py /path/to/file.txt   # ❌
```

### Git commands timing out
```python
# Increase timeout in scoring.py
result = subprocess.run(
    [...],
    timeout=10  # Increase from 5 to 10 seconds
)
```

### Bash script fails on macOS
```bash
# macOS uses bash 3.x by default, which doesn't support associative arrays
# Install bash 4+
brew install bash

# Use the new bash
/usr/local/bin/bash scoring.sh /path/to/project
```

### Incorrect scores
```python
# Adjust weights in config
config = ScoringConfig()
config.WEIGHTS["git_activity"] = 3.0  # Increase git weight
config.WEIGHTS["documentation"] = 0.5  # Decrease doc weight

scorer = DirectoryScorer(config)
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [examples/example_usage.py](examples/example_usage.py) for more examples
- Review [config/scoring_config.json](config/scoring_config.json) for configuration schema
- Run [tests/test_scoring.py](tests/test_scoring.py) to verify installation

## Support

For issues or questions:
1. Check the [README.md](README.md) documentation
2. Review [example_usage.py](examples/example_usage.py)
3. Run tests to verify: `python3 tests/test_scoring.py`
4. Open an issue in the project repository
