#!/usr/bin/env python3
"""
cy4-inspired activity scoring system (filesystem-only, no database integration).

5-Factor Scoring Algorithm:
- Factor 1: File Modification Recency (40%)
- Factor 2: Git Activity (25%)
- Factor 3: Running Processes (20%)
- Factor 4: IDE/Editor Open (10%)
- Factor 5: Dependency Freshness (5%)

Score ranges:
- 0-20:   DEAD (90+ days inactive)     → Safe to delete
- 21-40:  DORMANT (30-89 days)         → Safe to delete
- 41-60:  INACTIVE (14-29 days)        → Requires review
- 61-80:  ACTIVE (7-13 days)           → High risk
- 81-100: HOT (0-6 days)               → PROTECTED
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, List


class Cy4Scorer:
    """
    cy4-inspired activity scoring without database integration.

    Uses only filesystem metadata and system inspection.
    """

    def __init__(self, verbose: bool = False):
        """Initialize scorer."""
        self.verbose = verbose
        self._process_cache: Dict[str, List[psutil.Process]] = {}

    def calculate_activity_score(self, project_path: Path) -> int:
        """
        Calculate 0-100 activity score for a project.

        Args:
            project_path: Path to project directory

        Returns:
            Activity score 0-100
        """
        score = 0

        # Factor 1: File Modification Recency (40 points)
        days = self._get_days_since_modification(project_path)
        if days <= 7:
            score += 40
        elif days <= 14:
            score += 30
        elif days <= 30:
            score += 20
        elif days <= 90:
            score += 10
        # else: 0 points (90+ days)

        # Factor 2: Git Activity (25 points)
        git_days = self._get_days_since_last_commit(project_path)
        if git_days is not None:
            if git_days <= 7:
                score += 25
            elif git_days <= 30:
                score += 15
            elif git_days <= 90:
                score += 5

        # Factor 3: Running Processes (20 points)
        if self._count_running_processes(project_path) > 0:
            score += 20

        # Factor 4: IDE/Editor Open (10 points)
        if self._is_open_in_editor(project_path):
            score += 10

        # Factor 5: Dependency Installation Recency (5 points)
        dep_days = self._get_dependency_age(project_path)
        if dep_days is not None and dep_days <= 7:
            score += 5

        return min(score, 100)

    def get_risk_level(self, cy4_score: int) -> str:
        """
        Convert cy4 score to risk level label.

        Args:
            cy4_score: Activity score 0-100

        Returns:
            Risk level label with emoji
        """
        if cy4_score >= 81:
            return "🔴 HOT - PROTECTED"
        elif cy4_score >= 61:
            return "🟠 ACTIVE - HIGH RISK"
        elif cy4_score >= 41:
            return "🟡 INACTIVE - REVIEW"
        elif cy4_score >= 21:
            return "🟢 DORMANT - SAFE"
        else:
            return "🟢 DEAD - SAFE"

    def _get_days_since_modification(self, project_path: Path) -> int:
        """
        Calculate days since any file was modified in project.

        Skips dependency folders (node_modules, .venv, target).

        Args:
            project_path: Path to project

        Returns:
            Days since most recent modification
        """
        now = time.time()
        max_mtime = 0.0
        skip_dirs = {'node_modules', '.venv', 'venv', 'target', 'vendor', '__pycache__'}

        try:
            for root, dirs, files in os.walk(project_path):
                # Remove skip directories from traversal
                dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]

                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        mtime = os.path.getmtime(file_path)
                        max_mtime = max(max_mtime, mtime)
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            pass

        if max_mtime > 0:
            days = int((now - max_mtime) / 86400)
            return days
        else:
            return 999  # Assume very old if no files found

    def _get_days_since_last_commit(self, project_path: Path) -> Optional[int]:
        """
        Check git commit recency.

        Args:
            project_path: Path to project

        Returns:
            Days since last commit, or None if not a git repo
        """
        git_dir = project_path / ".git"
        if not git_dir.exists():
            return None

        try:
            result = subprocess.run(
                ["git", "-C", str(project_path), "log", "-1", "--format=%ct"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                try:
                    commit_time = int(result.stdout.strip())
                    days = int((time.time() - commit_time) / 86400)
                    return days
                except ValueError:
                    return None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return None

    def _count_running_processes(self, project_path: Path) -> int:
        """
        Count processes with open files in this project.

        Uses lsof to find all processes with files in the directory.

        Args:
            project_path: Path to project

        Returns:
            Number of unique processes
        """
        try:
            result = subprocess.run(
                ["lsof", "+D", str(project_path)],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                # Count unique PIDs (skip header line)
                pids = set()
                for line in result.stdout.splitlines()[1:]:
                    parts = line.split()
                    if len(parts) > 1:
                        try:
                            pid = int(parts[1])
                            pids.add(pid)
                        except ValueError:
                            continue

                return len(pids)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return 0

    def _is_open_in_editor(self, project_path: Path) -> bool:
        """
        Check if project is open in an IDE/editor.

        Uses lsof to find processes with the project directory open.

        Args:
            project_path: Path to project

        Returns:
            True if open in editor
        """
        editors = ['code', 'cursor', 'vim']

        for editor in editors:
            try:
                result = subprocess.run(
                    ["lsof", "-c", editor],
                    capture_output=True,
                    text=True,
                    timeout=2
                )

                if result.returncode == 0 and str(project_path) in result.stdout:
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        return False

    def _get_dependency_age(self, project_path: Path) -> Optional[int]:
        """
        Get age of the newest dependency folder.

        Args:
            project_path: Path to project

        Returns:
            Days since newest dependency was modified, or None
        """
        max_mtime = 0.0
        found_deps = False

        for dep_type in ['node_modules', '.venv', 'target', 'vendor']:
            dep_path = project_path / dep_type

            if dep_path.exists():
                try:
                    mtime = os.path.getmtime(dep_path)
                    max_mtime = max(max_mtime, mtime)
                    found_deps = True
                except (OSError, PermissionError):
                    continue

        if found_deps and max_mtime > 0:
            days = int((time.time() - max_mtime) / 86400)
            return days
        else:
            return None

    @staticmethod
    def _format_age(timestamp: float) -> str:
        """Format timestamp as human-readable age."""
        days = (time.time() - timestamp) / 86400

        if days < 1:
            return "today"
        elif days < 7:
            return f"{int(days)}d ago"
        elif days < 30:
            return f"{int(days/7)}w ago"
        else:
            return f"{int(days/30)}m ago"


def main():
    """Test the cy4 scorer."""
    from parallel_scanner import ParallelScanner

    base_dir = Path("/Users/rdmtv/Documents/claydev-local")
    scorer = Cy4Scorer(verbose=True)
    scanner = ParallelScanner(verbose=False)

    # Scan projects
    print("🔍 Scanning projects...")
    projects = list(scanner.scan_base_directory(base_dir))

    # Score projects
    print("\n🔢 Scoring projects...")
    scores: Dict[str, int] = {}

    for project in projects[:10]:  # Test on first 10
        score = scorer.calculate_activity_score(Path(project.path))
        scores[project.path] = score
        risk = scorer.get_risk_level(score)
        print(f"   {score:3} {risk:30} {project.path}")

    # Show statistics
    avg_score = sum(scores.values()) // len(scores) if scores else 0
    print(f"\n📊 Average score: {avg_score}/100")


if __name__ == "__main__":
    main()
