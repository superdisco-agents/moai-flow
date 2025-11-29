# Directory Activity Scoring Algorithm

A multi-factor scoring system for classifying directories based on activity levels, designed to help identify active projects, borderline cases, and archivable directories.

## Overview

This module provides both Python and Bash implementations of a sophisticated directory scoring algorithm that considers multiple factors to determine if a directory represents an active, borderline, or archivable project.

### Classification Thresholds

- **Active** (score ≥ 20): Actively developed projects that should be retained
- **Borderline** (0-19): Projects that may need review, context-dependent
- **Archivable** (< 0): Strong candidates for archival or removal

## Features

- **Multi-factor analysis**: Considers time, git activity, dependencies, documentation, file activity, and project structure
- **Project type detection**: Automatically detects Node.js, Python, Rust, Go, Java, Ruby, PHP, and Git projects
- **Safety checks**: Protected paths and critical files prevent accidental archival
- **Flexible output**: JSON, CSV, Markdown, and text formats
- **Batch processing**: Score multiple directories efficiently
- **CLI interface**: Easy integration with shell scripts and automation

## Installation

### Python Version

```bash
# Make the Python script executable
chmod +x .claude/lib/scoring/scoring.py

# Optional: Install in PATH
ln -s "$(pwd)/.claude/lib/scoring/scoring.py" /usr/local/bin/score-directory
```

### Bash Version

```bash
# Make the Bash script executable
chmod +x .claude/lib/scoring/scoring.sh

# Optional: Install in PATH
ln -s "$(pwd)/.claude/lib/scoring/scoring.sh" /usr/local/bin/score-directory-sh
```

## Usage

### Python CLI

```bash
# Score a single directory
python scoring.py /path/to/project

# Score multiple directories
python scoring.py /path/to/dir1 /path/to/dir2 /path/to/dir3

# Export as JSON
python scoring.py --format json /path/to/project

# Export as CSV
python scoring.py --format csv /path/to/project > scores.csv

# Export as Markdown
python scoring.py --format markdown /path/to/project > report.md

# Show detailed factor breakdown
python scoring.py --verbose /path/to/project

# Custom thresholds
python scoring.py --threshold-active 25 --threshold-borderline 5 /path/to/project
```

### Bash CLI

```bash
# Score a directory (text output)
./scoring.sh /path/to/project

# JSON output
./scoring.sh /path/to/project --format json

# Verbose mode
./scoring.sh /path/to/project --verbose

# Check exit code for classification
./scoring.sh /path/to/project
if [ $? -eq 0 ]; then
    echo "Directory is Active"
elif [ $? -eq 1 ]; then
    echo "Directory is Borderline"
elif [ $? -eq 2 ]; then
    echo "Directory is Archivable"
fi
```

### Python API

```python
from scoring import DirectoryScorer, ScoringConfig

# Create scorer with default configuration
scorer = DirectoryScorer()

# Score a directory
score = scorer.score_directory("/path/to/project")

print(f"Path: {score.path}")
print(f"Total Score: {score.total_score}")
print(f"Classification: {score.classification}")
print(f"Project Type: {score.project_type}")
print(f"Protected: {score.protected}")

# Access factor breakdown
for factor, value in score.factors.items():
    print(f"{factor}: {value}")

# Batch scoring
paths = ["/path/to/proj1", "/path/to/proj2", "/path/to/proj3"]
scores = scorer.score_batch(paths)

# Export results
json_output = scorer.export_results(scores, "json")
csv_output = scorer.export_results(scores, "csv")
md_output = scorer.export_results(scores, "markdown")
```

### Custom Configuration

```python
from scoring import DirectoryScorer, ScoringConfig

# Create custom configuration
config = ScoringConfig()

# Adjust thresholds
config.ACTIVE_THRESHOLD = 25
config.BORDERLINE_THRESHOLD = 5

# Adjust factor weights
config.WEIGHTS["git_activity"] = 3.0  # Emphasize git activity
config.WEIGHTS["documentation"] = 0.5  # De-emphasize documentation

# Add protected paths
config.PROTECTED_PATHS.append("my_special_dir")

# Add critical files
config.CRITICAL_FILES.append("my_important_file.conf")

# Create scorer with custom config
scorer = DirectoryScorer(config)
```

## Scoring Factors

### 1. Time Decay (Weight: 1.0)

Scores based on recency of file modifications:

- **Last 7 days**: +10 points
- **7-30 days**: +5 to +10 points (linear decay)
- **30-90 days**: 0 to +5 points (linear decay)
- **90+ days**: 0 to -5 points (decay to -5)

### 2. Git Activity (Weight: 2.0)

Evaluates git repository activity:

- **Is git repo**: +5 points
- **Recent commits (30 days)**: Up to +15 points (1.5 per commit)
- **Multiple branches**: +5 points
- **Uncommitted changes**: +10 points

### 3. Dependencies (Weight: 1.5)

Checks for dependency management:

- **Has dependency file**: +10 points (package.json, requirements.txt, etc.)
- **Has lock file**: +5 points (package-lock.json, Cargo.lock, etc.)
- **Multiple dependency systems**: +3 points

### 4. Documentation (Weight: 1.0)

Assesses documentation quality:

- **README file**: +8 points
- **Additional docs**: +2 points each (max +10)
- **docs/ directory**: +5 points

### 5. File Activity (Weight: 1.2)

Analyzes file presence and variety:

- **More than 10 files**: +5 points
- **Source code files present**: +5 points
- **Multiple file types (>3)**: +3 points

### 6. Project Structure (Weight: 0.8)

Evaluates project organization:

- **Standard directories**: +2 points each (src, lib, test, docs, etc., max +10)
- **Test directory**: +5 points
- **CI/CD configuration**: +5 points

## Protected Paths

The following paths are automatically protected from archival:

- `.git`, `.claude`
- `node_modules`, `.venv`, `venv`, `__pycache__`
- `dist`, `build`, `.next`, `.nuxt`

Directories in protected paths always receive a minimum score of 20 (Active).

## Critical Files

Directories containing these files are considered important:

- `package.json`, `requirements.txt`, `Cargo.toml`, `go.mod`
- `pom.xml`, `Gemfile`, `.git`, `Makefile`, `CMakeLists.txt`

## Project Type Detection

The algorithm automatically detects project types:

| Type | Indicators |
|------|-----------|
| Node.js | package.json, node_modules, yarn.lock |
| Python | requirements.txt, setup.py, pyproject.toml |
| Rust | Cargo.toml, Cargo.lock |
| Go | go.mod, go.sum |
| Java | pom.xml, build.gradle |
| Ruby | Gemfile, Gemfile.lock |
| PHP | composer.json, composer.lock |
| Git | .git directory |

## Output Formats

### JSON

```json
{
  "path": "/path/to/project",
  "total_score": 45.5,
  "classification": "Active",
  "project_type": "node",
  "protected": false,
  "last_modified": 1699564800.0,
  "factors": {
    "time_decay": 10.0,
    "git_activity": 25.0,
    "dependencies": 15.0,
    "documentation": 13.0,
    "file_activity": 13.0,
    "project_structure": 15.0
  },
  "warnings": []
}
```

### CSV

```csv
Path,Score,Classification,ProjectType,Protected
/path/to/project,45.5,Active,node,false
```

### Markdown

```markdown
# Directory Activity Scores

| Path | Score | Classification | Type | Protected |
|------|-------|----------------|------|-----------|
| /path/to/project | 45.5 | Active | node | ✗ |
```

### Text

```
======================================================================
Path: /path/to/project
Score: 45.5
Classification: Active
Project Type: node
Protected: false
Last Modified: 2024-11-09 12:00:00

Factor Breakdown:
  time_decay          :  10.00 (weight: 1.0, weighted: 10.00)
  git_activity        :  25.00 (weight: 2.0, weighted: 50.00)
  dependencies        :  15.00 (weight: 1.5, weighted: 22.50)
  documentation       :  13.00 (weight: 1.0, weighted: 13.00)
  file_activity       :  13.00 (weight: 1.2, weighted: 15.60)
  project_structure   :  15.00 (weight: 0.8, weighted: 12.00)
======================================================================
```

## Testing

Run the comprehensive test suite:

```bash
# Run Python tests
python tests/test_scoring.py

# Run specific test
python -c "from tests.test_scoring import TestDirectoryScorer; TestDirectoryScorer.test_git_activity_scoring()"
```

### Test Coverage

- Individual factor scoring functions
- Classification threshold logic
- Protected paths and safety checks
- Project type detection
- Batch processing
- Export formats
- Error handling
- Complete workflow integration

## Integration Examples

### Find Archivable Directories

```bash
#!/bin/bash
# Find all archivable directories in a workspace

for dir in */; do
    ./scoring.sh "$dir" > /dev/null 2>&1
    if [ $? -eq 2 ]; then
        echo "Archivable: $dir"
    fi
done
```

### Generate Report for All Projects

```python
from pathlib import Path
from scoring import DirectoryScorer

scorer = DirectoryScorer()
workspace = Path("/path/to/workspace")

# Score all subdirectories
dirs = [str(d) for d in workspace.iterdir() if d.is_dir()]
scores = scorer.score_batch(dirs)

# Generate markdown report
report = scorer.export_results(scores, "markdown")

with open("workspace_scores.md", "w") as f:
    f.write(report)
```

### Automated Cleanup Script

```python
from scoring import DirectoryScorer
import shutil
from pathlib import Path

scorer = DirectoryScorer()
workspace = Path("/path/to/workspace")

archivable = []
for dir_path in workspace.iterdir():
    if not dir_path.is_dir():
        continue

    score = scorer.score_directory(str(dir_path))

    if score.classification == "Archivable" and not score.protected:
        archivable.append(dir_path)

# Review and confirm before archiving
print(f"Found {len(archivable)} archivable directories:")
for path in archivable:
    print(f"  - {path}")

if input("Archive these directories? (yes/no): ").lower() == "yes":
    archive_dir = workspace / ".archived"
    archive_dir.mkdir(exist_ok=True)

    for path in archivable:
        dest = archive_dir / path.name
        shutil.move(str(path), str(dest))
        print(f"Archived: {path.name}")
```

## Performance Considerations

- **Large directories**: The algorithm samples files for performance (max 50 files checked for timestamps)
- **Git operations**: Git commands have 5-second timeouts to prevent hanging
- **Batch processing**: More efficient than individual scoring for multiple directories
- **Protected paths**: Automatically skipped during file traversal

## Best Practices

1. **Review borderline cases**: Don't auto-archive borderline directories without review
2. **Custom thresholds**: Adjust thresholds based on your workflow
3. **Factor weights**: Tune weights to match your priorities (e.g., emphasize git activity)
4. **Protected paths**: Add project-specific paths to the protected list
5. **Regular audits**: Run scoring periodically to identify archival candidates

## Troubleshooting

### Git Commands Timing Out

Increase timeout in `scoring.py`:

```python
result = subprocess.run(
    [...],
    timeout=10  # Increase from 5 to 10 seconds
)
```

### Permission Errors

Ensure the script has read permissions for target directories:

```bash
chmod -R +r /path/to/workspace
```

### Incorrect Classifications

Adjust factor weights or thresholds to match your needs:

```python
config = ScoringConfig()
config.WEIGHTS["git_activity"] = 3.0  # Emphasize git more
config.ACTIVE_THRESHOLD = 15  # Lower threshold for active classification
```

## Contributing

To extend the scoring algorithm:

1. **Add new factors**: Implement new scoring methods in `DirectoryScorer`
2. **Update weights**: Add new factors to `ScoringConfig.WEIGHTS`
3. **Add tests**: Create test cases in `tests/test_scoring.py`
4. **Update documentation**: Document new features in this README

## License

This module is part of the MoAI-ADK project and follows the same license.

## See Also

- [MoAI-ADK Documentation](../../docs/)
- [Project Configuration](../../config/)
- [CLI Skills](../)
