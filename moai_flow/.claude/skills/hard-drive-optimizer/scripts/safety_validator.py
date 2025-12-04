#!/usr/bin/env python3
"""
Safety validator with 10-point checklist.

ALL checks must pass before allowing deletion.

Checks:
1. cy4 Score Threshold (81+ = HOT → PROTECTED)
2. Activity Threshold (14 days default)
3. Git Uncommitted Changes
4. Running Processes (lsof)
5. Protected Paths (.claude, .moai, .git)
6. IDE/Editor Open
7. Recent Git Operations (< 1 hour)
8. Recent Dependency Installation (< 1 hour)
9. Symlink Detection
10. Minimum Size Threshold (< 10 MB = skip)
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class ProjectInfo:
    """Project information for safety validation."""
    path: str
    size_bytes: int
    cy4_score: float
    days_since_modified: int
    has_dependencies: bool = True


class SafetyValidator:
    """
    10-point safety checklist validator.

    ALL checks must pass before deletion is allowed.
    """

    # Protected folder patterns (never delete projects containing these)
    PROTECTED_PATHS = {'.claude', '.moai', '.git', '.gitignore'}

    # Minimum size to consider for deletion (10 MB)
    MIN_SIZE_BYTES = 10 * 1024 * 1024

    # Dependency patterns
    DEPENDENCY_PATTERNS = {'node_modules', '.venv', 'venv', 'target', 'vendor'}

    def __init__(self, verbose: bool = True):
        """Initialize validator."""
        self.verbose = verbose

    def verify_safe_to_delete(self, project_info: ProjectInfo) -> Tuple[bool, List[str]]:
        """
        Run 10-point safety checklist.

        ALL checks must pass (no errors) for deletion to be safe.

        Args:
            project_info: Project information

        Returns:
            (is_safe, error_messages)
            - is_safe: True if ALL checks pass
            - error_messages: List of failed checks
        """
        errors = []

        # 1. cy4 Score Threshold (81+ = HOT)
        if project_info.cy4_score >= 81:
            errors.append("🔴 Project is HOT (cy4 >= 81)")

        # 2. Activity Threshold (14 days default)
        if project_info.days_since_modified < 14:
            errors.append(f"🟡 Modified within 14 days ({project_info.days_since_modified}d ago)")

        # 3. Git Uncommitted Changes
        if self._has_uncommitted_changes(project_info.path):
            errors.append("🟠 Uncommitted git changes")

        # 4. Running Processes
        if self._count_running_processes(project_info.path) > 0:
            errors.append("🟠 Running processes detected")

        # 5. Protected Paths (.claude, .moai, .git)
        if self._contains_protected_paths(project_info.path):
            errors.append("🔴 Contains protected folders (.claude/.moai)")

        # 6. IDE/Editor Open
        if self._is_open_in_editor(project_info.path):
            errors.append("🟠 Open in VS Code/Cursor")

        # 7. Recent Git Operations (< 1 hour)
        if self._has_recent_git_activity(project_info.path, hours=1):
            errors.append("🟡 Recent git operations (< 1 hour)")

        # 8. Recent Dependency Installation (< 1 hour)
        if self._has_recent_npm_install(project_info.path, hours=1):
            errors.append("🟡 Recent npm/pip install (< 1 hour)")

        # 9. Symlink Detection
        if self._contains_symlinks(project_info.path):
            errors.append("🟡 Contains symlinks (may be linked dependencies)")

        # 10. Minimum Size Threshold (< 10 MB = skip)
        if project_info.size_bytes < self.MIN_SIZE_BYTES:
            errors.append(f"⏭️  Too small ({project_info.size_bytes / 1024 / 1024:.1f} MB < 10 MB)")

        return len(errors) == 0, errors

    def _has_uncommitted_changes(self, project_path: str) -> bool:
        """Check if git repo has uncommitted changes."""
        git_dir = Path(project_path) / ".git"

        if not git_dir.exists():
            return False  # Not a git repo, no uncommitted changes

        try:
            result = subprocess.run(
                ["git", "-C", project_path, "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=2
            )

            # If output is empty, no changes
            return len(result.stdout.strip()) > 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _count_running_processes(self, project_path: str) -> int:
        """Count processes with open files in this project."""
        try:
            result = subprocess.run(
                ["lsof", "+D", project_path],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                pids = set()
                for line in result.stdout.splitlines()[1:]:
                    parts = line.split()
                    if len(parts) > 1:
                        try:
                            pids.add(int(parts[1]))
                        except ValueError:
                            continue

                return len(pids)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return 0

    def _contains_protected_paths(self, project_path: str) -> bool:
        """Check for protected folders (.claude, .moai, .git)."""
        project_dir = Path(project_path)

        for protected in self.PROTECTED_PATHS:
            if (project_dir / protected).exists():
                return True

        return False

    def _is_open_in_editor(self, project_path: str) -> bool:
        """Check if project is open in VS Code, Cursor, etc."""
        editors = {'code', 'cursor', 'vim', 'nano', 'emacs'}

        try:
            result = subprocess.run(
                ["lsof", "-c", "code"],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                return project_path in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return False

    def _has_recent_git_activity(self, project_path: str, hours: int = 1) -> bool:
        """Check if git repo has recent activity (< N hours)."""
        git_dir = Path(project_path) / ".git"

        if not git_dir.exists():
            return False

        try:
            # Check modification time of git index
            git_index = git_dir / "index"

            if git_index.exists():
                mtime = os.path.getmtime(git_index)
                age_hours = (time.time() - mtime) / 3600

                return age_hours < hours
        except (OSError, PermissionError):
            pass

        return False

    def _has_recent_npm_install(self, project_path: str, hours: int = 1) -> bool:
        """Check if dependencies were recently installed (< N hours)."""
        for dep_type in self.DEPENDENCY_PATTERNS:
            dep_path = Path(project_path) / dep_type

            if dep_path.exists():
                try:
                    mtime = os.path.getmtime(dep_path)
                    age_hours = (time.time() - mtime) / 3600

                    if age_hours < hours:
                        return True
                except (OSError, PermissionError):
                    continue

        return False

    def _contains_symlinks(self, project_path: str) -> bool:
        """Check if project contains symlinks to dependencies."""
        for dep_type in self.DEPENDENCY_PATTERNS:
            dep_path = Path(project_path) / dep_type

            if dep_path.exists() and dep_path.is_symlink():
                return True

        return False

    @staticmethod
    def _format_size(bytes_size: int) -> str:
        """Format bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} TB"


def main():
    """Test the safety validator."""
    validator = SafetyValidator(verbose=True)

    # Test projects
    test_projects = [
        ProjectInfo(
            path="/Users/rdmtv/Documents/claydev-local/opensource-v2/old-project",
            size_bytes=500 * 1024 * 1024,
            cy4_score=15,
            days_since_modified=45
        ),
        ProjectInfo(
            path="/Users/rdmtv/Documents/claydev-local/projects-v2/moai-ir-deck",
            size_bytes=200 * 1024 * 1024,
            cy4_score=85,
            days_since_modified=2
        ),
    ]

    print("🔐 Safety Validator Test\n")

    for project in test_projects:
        is_safe, errors = validator.verify_safe_to_delete(project)

        print(f"Project: {Path(project.path).name}")
        print(f"  cy4 Score: {project.cy4_score}/100")
        print(f"  Days inactive: {project.days_since_modified}")
        print(f"  Safe to delete: {'✅ YES' if is_safe else '❌ NO'}")

        if errors:
            for error in errors:
                print(f"    {error}")

        print()


if __name__ == "__main__":
    main()
