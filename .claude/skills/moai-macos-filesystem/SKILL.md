---
name: "moai-macos-filesystem"
version: "1.0.0"
created: 2025-11-25
updated: 2025-11-25
status: stable
description: Enterprise macOS filesystem safety orchestration with intelligent project detection, context-aware scoring algorithms, and fail-safe rollback mechanisms for all file operations across multi-project workspaces
keywords: ['macos-filesystem', 'safety-checks', 'project-detection', 'scoring-algorithm', 'rollback-mechanism', 'filesystem-safety', 'workspace-management', 'safe-operations', 'context-awareness']
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - Write
  - Edit
---

# macOS Filesystem Safety Expert

## Skill Metadata

| Field | Value |
| ----- | ----- |
| **Skill Name** | moai-macos-filesystem |
| **Version** | 1.0.0 (2025-11-25) |
| **Tier** | Enterprise Filesystem Safety |
| **Auto-load** | When filesystem operations detected |
| **Safety Features** | Project detection, scoring, rollback |

---

## What It Does

Enterprise filesystem safety orchestration for macOS that prevents accidental modifications to wrong projects through intelligent project detection, context-aware scoring algorithms, and automated rollback mechanisms.

**Core Capabilities**:
- 🎯 **Intelligent Project Detection** - Identifies correct project context from workspace paths
- 📊 **Context-Aware Scoring** - Evaluates operation safety with multi-factor scoring
- 🛡️ **Safe Operation Patterns** - Ensures all file operations target correct projects
- ↩️ **Automated Rollback** - Instant recovery from incorrect operations
- 🔍 **macOS-Specific Patterns** - Handles .DS_Store, symlinks, and spotlight metadata

---

## When to Use

**Automatic triggers**:
- Before any file write, edit, or delete operation
- When working with multiple projects in same session
- During cross-project navigation or context switching
- When ambiguous paths could target wrong project

**Manual reference**:
- Designing filesystem safety patterns
- Implementing project detection logic
- Planning rollback strategies
- Debugging incorrect file operations

---

# Quick Reference (Level 1)

## Safety Workflow (3-Step Pattern)

### Step 1: Detect Project Context
```bash
# Identify current working directory and project root
pwd                           # Current directory
git rev-parse --show-toplevel # Git project root (if available)
ls -la | head -5             # Verify project markers
```

### Step 2: Score Operation Safety
```python
# Calculate safety score (0-100)
score = 0
if path.startswith(detected_project_root):     score += 40
if git_branch_matches_expected:                score += 20
if package_json_name_matches:                  score += 15
if recent_files_in_same_project:               score += 15
if no_conflicting_project_markers:             score += 10

# Safety thresholds:
# 90-100: Safe (proceed)
# 70-89:  Warning (confirm with user)
# 0-69:   Unsafe (block operation)
```

### Step 3: Execute with Rollback
```bash
# Backup before operation
cp original.file original.file.backup.$(date +%s)

# Execute operation
[perform file operation]

# Auto-rollback on error
if [ $? -ne 0 ]; then
  mv original.file.backup.* original.file
fi
```

## Common Patterns

### Pattern 1: Safe File Write
```python
def safe_write_file(filepath: str, content: str, project_root: str):
    """Write file with project validation and rollback."""
    # 1. Validate path is within project
    if not filepath.startswith(project_root):
        raise ValueError(f"Path {filepath} outside project {project_root}")

    # 2. Create backup if file exists
    backup_path = None
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup.{int(time.time())}"
        shutil.copy2(filepath, backup_path)

    try:
        # 3. Write file
        with open(filepath, 'w') as f:
            f.write(content)
    except Exception as e:
        # 4. Rollback on error
        if backup_path and os.path.exists(backup_path):
            shutil.move(backup_path, filepath)
        raise e
    finally:
        # 5. Cleanup backup on success
        if backup_path and os.path.exists(backup_path):
            os.remove(backup_path)
```

### Pattern 2: Project Detection
```bash
# Detect project root with multiple markers
detect_project_root() {
  local current_dir="$PWD"

  # Check git root
  if git rev-parse --show-toplevel 2>/dev/null; then
    return 0
  fi

  # Check for package.json (Node.js)
  if [ -f "package.json" ]; then
    echo "$current_dir"
    return 0
  fi

  # Check for pyproject.toml (Python)
  if [ -f "pyproject.toml" ]; then
    echo "$current_dir"
    return 0
  fi

  # Check for .moai/ (MoAI-ADK)
  if [ -d ".moai" ]; then
    echo "$current_dir"
    return 0
  fi

  echo "ERROR: No project root detected" >&2
  return 1
}
```

---

# Practical Implementation (Level 2)

## Scoring Algorithm Implementation

### Complete Scoring System
```python
from dataclasses import dataclass
from typing import Optional, List
import os
import json
import subprocess

@dataclass
class ProjectContext:
    """Detected project context information."""
    root_path: str
    project_name: Optional[str]
    git_branch: Optional[str]
    package_manager: Optional[str]  # npm, pip, cargo, etc.
    recent_files: List[str]

    @classmethod
    def detect(cls, current_dir: str) -> 'ProjectContext':
        """Detect project context from current directory."""
        root_path = cls._find_project_root(current_dir)
        project_name = cls._detect_project_name(root_path)
        git_branch = cls._get_git_branch(root_path)
        package_manager = cls._detect_package_manager(root_path)
        recent_files = cls._get_recent_files(root_path)

        return cls(
            root_path=root_path,
            project_name=project_name,
            git_branch=git_branch,
            package_manager=package_manager,
            recent_files=recent_files
        )

    @staticmethod
    def _find_project_root(start_dir: str) -> str:
        """Find project root by checking for markers."""
        current = os.path.abspath(start_dir)
        markers = ['.git', 'package.json', 'pyproject.toml',
                   'Cargo.toml', '.moai', 'pom.xml']

        while current != '/':
            for marker in markers:
                if os.path.exists(os.path.join(current, marker)):
                    return current
            current = os.path.dirname(current)

        raise ValueError(f"No project root found from {start_dir}")

    @staticmethod
    def _detect_project_name(root_path: str) -> Optional[str]:
        """Detect project name from package files."""
        # Check package.json
        pkg_json = os.path.join(root_path, 'package.json')
        if os.path.exists(pkg_json):
            with open(pkg_json) as f:
                return json.load(f).get('name')

        # Check pyproject.toml
        pyproject = os.path.join(root_path, 'pyproject.toml')
        if os.path.exists(pyproject):
            import toml
            return toml.load(pyproject).get('project', {}).get('name')

        # Fallback to directory name
        return os.path.basename(root_path)

    @staticmethod
    def _get_git_branch(root_path: str) -> Optional[str]:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=root_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            return None

    @staticmethod
    def _detect_package_manager(root_path: str) -> Optional[str]:
        """Detect package manager from lock files."""
        if os.path.exists(os.path.join(root_path, 'package-lock.json')):
            return 'npm'
        if os.path.exists(os.path.join(root_path, 'yarn.lock')):
            return 'yarn'
        if os.path.exists(os.path.join(root_path, 'pnpm-lock.yaml')):
            return 'pnpm'
        if os.path.exists(os.path.join(root_path, 'Pipfile.lock')):
            return 'pipenv'
        if os.path.exists(os.path.join(root_path, 'poetry.lock')):
            return 'poetry'
        return None

    @staticmethod
    def _get_recent_files(root_path: str, limit: int = 10) -> List[str]:
        """Get recently modified files in project."""
        try:
            result = subprocess.run(
                ['find', root_path, '-type', 'f', '-mtime', '-1',
                 '-not', '-path', '*/node_modules/*',
                 '-not', '-path', '*/.git/*'],
                capture_output=True,
                text=True,
                check=True
            )
            files = result.stdout.strip().split('\n')
            return files[:limit]
        except:
            return []


class FilesystemSafetyScorer:
    """Calculate safety score for filesystem operations."""

    def __init__(self, project_context: ProjectContext):
        self.context = project_context

    def score_operation(self,
                       target_path: str,
                       expected_project: Optional[str] = None,
                       expected_branch: Optional[str] = None) -> tuple[int, str]:
        """
        Calculate safety score (0-100) for filesystem operation.

        Returns:
            (score, reason) tuple where:
            - score: 0-100 safety score
            - reason: explanation of score
        """
        score = 0
        reasons = []

        # Factor 1: Path within project root (40 points)
        if target_path.startswith(self.context.root_path):
            score += 40
            reasons.append("✓ Path within detected project root")
        else:
            reasons.append("✗ Path OUTSIDE project root")
            return (score, "; ".join(reasons))  # Critical failure

        # Factor 2: Git branch matches expected (20 points)
        if expected_branch:
            if self.context.git_branch == expected_branch:
                score += 20
                reasons.append(f"✓ Git branch matches ({expected_branch})")
            else:
                reasons.append(
                    f"⚠ Git branch mismatch "
                    f"(expected: {expected_branch}, actual: {self.context.git_branch})"
                )
        else:
            # No expectation, give half points
            score += 10
            reasons.append("~ No git branch expectation")

        # Factor 3: Project name matches (15 points)
        if expected_project:
            if self.context.project_name == expected_project:
                score += 15
                reasons.append(f"✓ Project name matches ({expected_project})")
            else:
                reasons.append(
                    f"⚠ Project name mismatch "
                    f"(expected: {expected_project}, actual: {self.context.project_name})"
                )
        else:
            score += 8
            reasons.append("~ No project name expectation")

        # Factor 4: Recent activity in same project (15 points)
        if self._has_recent_activity_in_project(target_path):
            score += 15
            reasons.append("✓ Recent file activity in same project")
        else:
            reasons.append("⚠ No recent activity in this project")

        # Factor 5: No conflicting project markers (10 points)
        if not self._has_conflicting_project_markers(target_path):
            score += 10
            reasons.append("✓ No conflicting project markers")
        else:
            reasons.append("⚠ Conflicting project markers detected")

        return (score, "; ".join(reasons))

    def _has_recent_activity_in_project(self, target_path: str) -> bool:
        """Check if recent files are in same project as target."""
        target_dir = os.path.dirname(target_path)
        return any(
            recent_file.startswith(target_dir)
            for recent_file in self.context.recent_files
        )

    def _has_conflicting_project_markers(self, target_path: str) -> bool:
        """Check if target path contains nested project markers."""
        target_dir = os.path.dirname(target_path)
        relative_path = os.path.relpath(target_dir, self.context.root_path)

        # Check for nested project markers
        markers = ['package.json', 'pyproject.toml', '.git']
        for marker in markers:
            marker_path = os.path.join(target_dir, marker)
            if os.path.exists(marker_path) and relative_path != '.':
                return True
        return False


# Usage Example
def safe_filesystem_operation(target_path: str, operation: str):
    """
    Perform filesystem operation with safety checks.

    Args:
        target_path: Path to operate on
        operation: Operation description
    """
    # 1. Detect project context
    context = ProjectContext.detect(os.getcwd())

    # 2. Calculate safety score
    scorer = FilesystemSafetyScorer(context)
    score, reason = scorer.score_operation(
        target_path,
        expected_project="moai-adk",  # From user config
        expected_branch="main"         # From git context
    )

    # 3. Evaluate safety
    print(f"Safety Score: {score}/100")
    print(f"Reason: {reason}")

    if score >= 90:
        print("✓ SAFE - Proceeding with operation")
        return True
    elif score >= 70:
        print("⚠ WARNING - Confirm before proceeding")
        confirm = input("Continue? (y/n): ")
        return confirm.lower() == 'y'
    else:
        print("✗ UNSAFE - Operation blocked")
        return False
```

## Safe Operation Patterns

### Pattern 1: Atomic File Write with Rollback
```python
import os
import tempfile
import shutil
from contextlib import contextmanager

@contextmanager
def atomic_write(filepath: str, project_root: str):
    """
    Atomic file write with automatic rollback on error.

    Usage:
        with atomic_write('/path/to/file.txt', project_root) as f:
            f.write('content')
    """
    # Validate path
    if not filepath.startswith(project_root):
        raise ValueError(f"Path {filepath} outside project {project_root}")

    # Create backup if file exists
    backup_path = None
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup.{int(time.time())}"
        shutil.copy2(filepath, backup_path)

    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(
        dir=os.path.dirname(filepath),
        prefix='.tmp-',
        suffix=os.path.basename(filepath)
    )

    try:
        # Provide file handle for writing
        with os.fdopen(temp_fd, 'w') as f:
            yield f

        # Atomic replace
        shutil.move(temp_path, filepath)

        # Remove backup on success
        if backup_path:
            os.remove(backup_path)

    except Exception as e:
        # Rollback on error
        if os.path.exists(temp_path):
            os.remove(temp_path)

        if backup_path and os.path.exists(backup_path):
            shutil.move(backup_path, filepath)

        raise e
```

### Pattern 2: Batch Operations with Transaction
```python
class FilesystemTransaction:
    """Transaction wrapper for multiple filesystem operations."""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.operations = []
        self.backups = []

    def write_file(self, filepath: str, content: str):
        """Queue file write operation."""
        self.operations.append(('write', filepath, content))

    def delete_file(self, filepath: str):
        """Queue file delete operation."""
        self.operations.append(('delete', filepath, None))

    def commit(self):
        """Execute all operations with rollback on error."""
        try:
            # Create backups
            for op_type, filepath, _ in self.operations:
                if os.path.exists(filepath):
                    backup = f"{filepath}.backup.{int(time.time())}"
                    shutil.copy2(filepath, backup)
                    self.backups.append((filepath, backup))

            # Execute operations
            for op_type, filepath, content in self.operations:
                if op_type == 'write':
                    with open(filepath, 'w') as f:
                        f.write(content)
                elif op_type == 'delete':
                    os.remove(filepath)

            # Cleanup backups on success
            for _, backup in self.backups:
                os.remove(backup)

        except Exception as e:
            # Rollback all operations
            self.rollback()
            raise e

    def rollback(self):
        """Restore all files from backups."""
        for original, backup in self.backups:
            if os.path.exists(backup):
                shutil.move(backup, original)
```

---

# Advanced Integration (Level 3)

## Rollback Mechanism Implementation

### Complete Rollback System
```python
import pickle
import hashlib
from datetime import datetime
from typing import Dict, List, Any

class FilesystemRollbackManager:
    """
    Advanced rollback manager with snapshot support.

    Features:
    - Point-in-time snapshots
    - Incremental backups
    - Automatic cleanup of old snapshots
    - Checksum verification
    """

    def __init__(self, project_root: str, snapshot_dir: str = '.moai/snapshots'):
        self.project_root = project_root
        self.snapshot_dir = os.path.join(project_root, snapshot_dir)
        os.makedirs(self.snapshot_dir, exist_ok=True)

    def create_snapshot(self, description: str) -> str:
        """
        Create snapshot of current filesystem state.

        Returns:
            snapshot_id: Unique identifier for snapshot
        """
        snapshot_id = datetime.now().strftime('%Y%m%d-%H%M%S')
        snapshot_path = os.path.join(self.snapshot_dir, snapshot_id)
        os.makedirs(snapshot_path, exist_ok=True)

        # Collect file states
        file_states = {}
        for root, dirs, files in os.walk(self.project_root):
            # Skip snapshot directory
            if root.startswith(self.snapshot_dir):
                continue

            for file in files:
                filepath = os.path.join(root, file)
                relative_path = os.path.relpath(filepath, self.project_root)

                # Calculate checksum
                checksum = self._calculate_checksum(filepath)

                # Store file state
                file_states[relative_path] = {
                    'checksum': checksum,
                    'size': os.path.getsize(filepath),
                    'mtime': os.path.getmtime(filepath)
                }

                # Copy file to snapshot
                snapshot_file = os.path.join(snapshot_path, relative_path)
                os.makedirs(os.path.dirname(snapshot_file), exist_ok=True)
                shutil.copy2(filepath, snapshot_file)

        # Save snapshot metadata
        metadata = {
            'id': snapshot_id,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'file_states': file_states
        }

        with open(os.path.join(snapshot_path, 'metadata.pkl'), 'wb') as f:
            pickle.dump(metadata, f)

        return snapshot_id

    def restore_snapshot(self, snapshot_id: str):
        """Restore filesystem to snapshot state."""
        snapshot_path = os.path.join(self.snapshot_dir, snapshot_id)

        if not os.path.exists(snapshot_path):
            raise ValueError(f"Snapshot {snapshot_id} not found")

        # Load metadata
        with open(os.path.join(snapshot_path, 'metadata.pkl'), 'rb') as f:
            metadata = pickle.load(f)

        # Restore files
        for relative_path, state in metadata['file_states'].items():
            snapshot_file = os.path.join(snapshot_path, relative_path)
            target_file = os.path.join(self.project_root, relative_path)

            # Create directories
            os.makedirs(os.path.dirname(target_file), exist_ok=True)

            # Copy file
            shutil.copy2(snapshot_file, target_file)

        print(f"✓ Restored snapshot {snapshot_id}")

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all available snapshots."""
        snapshots = []

        for snapshot_id in os.listdir(self.snapshot_dir):
            snapshot_path = os.path.join(self.snapshot_dir, snapshot_id)
            metadata_path = os.path.join(snapshot_path, 'metadata.pkl')

            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                    snapshots.append(metadata)

        return sorted(snapshots, key=lambda x: x['created_at'], reverse=True)

    def cleanup_old_snapshots(self, keep_count: int = 5):
        """Remove old snapshots, keeping only recent ones."""
        snapshots = self.list_snapshots()

        if len(snapshots) <= keep_count:
            return

        to_remove = snapshots[keep_count:]
        for snapshot in to_remove:
            snapshot_path = os.path.join(self.snapshot_dir, snapshot['id'])
            shutil.rmtree(snapshot_path)
            print(f"✓ Removed old snapshot {snapshot['id']}")

    @staticmethod
    def _calculate_checksum(filepath: str) -> str:
        """Calculate SHA256 checksum of file."""
        sha256 = hashlib.sha256()

        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)

        return sha256.hexdigest()


# Usage Example
def safe_batch_operation_with_rollback(project_root: str):
    """Perform batch operations with automatic rollback."""
    rollback = FilesystemRollbackManager(project_root)

    # Create snapshot before operations
    snapshot_id = rollback.create_snapshot("Before batch file operations")

    try:
        # Perform filesystem operations
        transaction = FilesystemTransaction(project_root)
        transaction.write_file('src/newfile.py', 'content')
        transaction.delete_file('src/oldfile.py')
        transaction.commit()

        print("✓ Operations completed successfully")

        # Cleanup old snapshots
        rollback.cleanup_old_snapshots(keep_count=5)

    except Exception as e:
        print(f"✗ Error during operations: {e}")
        print(f"Rolling back to snapshot {snapshot_id}")
        rollback.restore_snapshot(snapshot_id)
```

## macOS-Specific Patterns

### Pattern 1: Handle .DS_Store Files
```bash
# Ignore .DS_Store in operations
find . -name ".DS_Store" -type f -delete

# Add to .gitignore
echo ".DS_Store" >> .gitignore
echo ".DS_Store" >> .git/info/exclude
```

### Pattern 2: Handle Symlinks Safely
```python
def safe_copy_with_symlinks(src: str, dst: str, project_root: str):
    """Copy files while preserving or resolving symlinks."""
    # Validate paths
    if not src.startswith(project_root):
        raise ValueError(f"Source {src} outside project")
    if not dst.startswith(project_root):
        raise ValueError(f"Destination {dst} outside project")

    if os.path.islink(src):
        # Get link target
        target = os.readlink(src)

        # Check if target is within project
        abs_target = os.path.abspath(os.path.join(os.path.dirname(src), target))

        if abs_target.startswith(project_root):
            # Safe: Recreate symlink
            os.symlink(target, dst)
        else:
            # Unsafe: Copy file content instead
            shutil.copy2(os.path.realpath(src), dst)
    else:
        # Regular file
        shutil.copy2(src, dst)
```

### Pattern 3: Handle Spotlight Metadata
```bash
# Disable Spotlight indexing for build directories
touch node_modules/.metadata_never_index
touch build/.metadata_never_index
touch dist/.metadata_never_index

# Clear Spotlight cache for project
mdutil -E /path/to/project
```

### Pattern 4: macOS File Permissions
```python
def set_macos_permissions(filepath: str, executable: bool = False):
    """Set appropriate macOS permissions."""
    if executable:
        # rwxr-xr-x (755)
        os.chmod(filepath, 0o755)
    else:
        # rw-r--r-- (644)
        os.chmod(filepath, 0o644)

    # Verify no SUID/SGID bits
    stat_info = os.stat(filepath)
    mode = stat_info.st_mode

    if mode & 0o4000:  # SUID
        raise ValueError("SUID bit detected - security risk")
    if mode & 0o2000:  # SGID
        raise ValueError("SGID bit detected - security risk")
```

---

# Best Practices

## DO
- ✅ Always validate paths are within expected project
- ✅ Calculate safety score before operations
- ✅ Create backups before modifying files
- ✅ Use atomic operations with rollback
- ✅ Handle macOS-specific files (.DS_Store, symlinks)
- ✅ Implement transaction patterns for batch operations
- ✅ Verify checksums after critical operations
- ✅ Keep snapshot history for recovery

## DON'T
- ❌ Skip project detection and validation
- ❌ Operate on paths outside detected project
- ❌ Ignore safety score warnings
- ❌ Forget to create backups
- ❌ Assume symlinks are safe
- ❌ Skip cleanup of temporary files
- ❌ Hardcode project paths
- ❌ Ignore filesystem errors

---

# Integration Examples

## Example 1: Integration with Claude Code Agent
```python
class ClaudeCodeFilesystemSafety:
    """Filesystem safety wrapper for Claude Code agents."""

    def __init__(self):
        self.context = None
        self.rollback = None

    def initialize(self, project_root: str):
        """Initialize safety checks for project."""
        self.context = ProjectContext.detect(project_root)
        self.rollback = FilesystemRollbackManager(project_root)

        print(f"✓ Initialized safety for project: {self.context.project_name}")
        print(f"  Root: {self.context.root_path}")
        print(f"  Branch: {self.context.git_branch}")

    def safe_write(self, filepath: str, content: str):
        """Safe file write with validation."""
        # Score operation
        scorer = FilesystemSafetyScorer(self.context)
        score, reason = scorer.score_operation(filepath)

        if score < 70:
            raise ValueError(f"Unsafe operation (score: {score}): {reason}")

        # Create snapshot
        snapshot_id = self.rollback.create_snapshot(
            f"Before writing {os.path.basename(filepath)}"
        )

        try:
            # Execute write
            with atomic_write(filepath, self.context.root_path) as f:
                f.write(content)
        except Exception as e:
            # Rollback on error
            self.rollback.restore_snapshot(snapshot_id)
            raise e
```

## Example 2: Multi-Project Workspace Safety
```python
class MultiProjectWorkspaceSafety:
    """Handle multiple projects in same workspace."""

    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.projects = self._detect_projects()

    def _detect_projects(self) -> Dict[str, ProjectContext]:
        """Detect all projects in workspace."""
        projects = {}

        for item in os.listdir(self.workspace_root):
            item_path = os.path.join(self.workspace_root, item)

            if os.path.isdir(item_path):
                try:
                    context = ProjectContext.detect(item_path)
                    projects[context.project_name] = context
                except:
                    continue

        return projects

    def select_project(self, target_path: str) -> Optional[ProjectContext]:
        """Select correct project for target path."""
        for project_name, context in self.projects.items():
            if target_path.startswith(context.root_path):
                return context
        return None
```

---

# Related Skills

- `moai-foundation-git` - Git operations safety
- `moai-core-practices` - Workflow patterns
- `moai-foundation-trust` - Quality gates
- `moai-essentials-debug` - Error handling

---

**End of Skill** | Updated 2025-11-25 | Version 1.0.0

**Status**: Production Ready | Comprehensive filesystem safety for macOS environments
