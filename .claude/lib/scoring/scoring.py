#!/usr/bin/env python3
"""
Directory Activity Scoring Algorithm

This module implements a multi-factor scoring system to classify directories as:
- Active (score ≥ 20): Actively developed, should be retained
- Borderline (0-19): May need review, context-dependent
- Archivable (< 0): Candidates for archival or removal

Scoring Factors:
1. Time-based decay: Recent activity scores higher
2. Git activity: Commit frequency, contributors, branch activity
3. Dependencies: Package manager files indicate active projects
4. Documentation: Well-documented projects are likely active
5. Project type: Different project types have different indicators
"""

import os
import json
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class DirectoryScore:
    """Represents a scored directory with breakdown of factors"""
    path: str
    total_score: float
    classification: str  # "Active", "Borderline", "Archivable"
    factors: Dict[str, float]
    project_type: Optional[str]
    last_modified: float
    warnings: List[str]
    protected: bool


class ScoringConfig:
    """Configuration for scoring thresholds and weights"""

    # Classification thresholds
    ACTIVE_THRESHOLD = 20
    BORDERLINE_THRESHOLD = 0

    # Factor weights
    WEIGHTS = {
        "time_decay": 1.0,
        "git_activity": 2.0,
        "dependencies": 1.5,
        "documentation": 1.0,
        "file_activity": 1.2,
        "project_structure": 0.8
    }

    # Protected paths (never archivable)
    PROTECTED_PATHS = [
        ".git",
        ".claude",
        "node_modules",
        ".venv",
        "venv",
        "__pycache__",
        "dist",
        "build",
        ".next",
        ".nuxt"
    ]

    # Critical file patterns (directories with these are protected)
    CRITICAL_FILES = [
        "package.json",
        "requirements.txt",
        "Cargo.toml",
        "go.mod",
        "pom.xml",
        "Gemfile",
        ".git",
        "Makefile",
        "CMakeLists.txt"
    ]

    # Project type indicators
    PROJECT_INDICATORS = {
        "node": ["package.json", "node_modules", "yarn.lock", "package-lock.json"],
        "python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
        "rust": ["Cargo.toml", "Cargo.lock"],
        "go": ["go.mod", "go.sum"],
        "java": ["pom.xml", "build.gradle", "gradle.properties"],
        "ruby": ["Gemfile", "Gemfile.lock"],
        "php": ["composer.json", "composer.lock"],
        "git": [".git"]
    }


class DirectoryScorer:
    """Main scoring engine for directory activity analysis"""

    def __init__(self, config: Optional[ScoringConfig] = None):
        self.config = config or ScoringConfig()

    def score_directory(self, path: str, base_time: Optional[float] = None) -> DirectoryScore:
        """
        Score a directory based on multiple factors

        Args:
            path: Path to the directory to score
            base_time: Reference time for decay calculations (default: now)

        Returns:
            DirectoryScore object with detailed breakdown
        """
        if not os.path.isdir(path):
            raise ValueError(f"Path is not a directory: {path}")

        base_time = base_time or time.time()
        warnings = []

        # Check if directory is protected
        protected = self._is_protected(path)
        if protected:
            warnings.append("Directory is in protected paths list")

        # Detect project type
        project_type = self._detect_project_type(path)

        # Calculate individual factor scores
        factors = {
            "time_decay": self._score_time_decay(path, base_time),
            "git_activity": self._score_git_activity(path),
            "dependencies": self._score_dependencies(path, project_type),
            "documentation": self._score_documentation(path),
            "file_activity": self._score_file_activity(path),
            "project_structure": self._score_project_structure(path, project_type)
        }

        # Apply weights and calculate total score
        total_score = sum(
            score * self.config.WEIGHTS.get(factor, 1.0)
            for factor, score in factors.items()
        )

        # Override score if protected
        if protected:
            total_score = max(total_score, self.config.ACTIVE_THRESHOLD)

        # Classify based on thresholds
        if total_score >= self.config.ACTIVE_THRESHOLD:
            classification = "Active"
        elif total_score >= self.config.BORDERLINE_THRESHOLD:
            classification = "Borderline"
        else:
            classification = "Archivable"

        # Get last modified time
        last_modified = self._get_last_modified(path)

        return DirectoryScore(
            path=path,
            total_score=round(total_score, 2),
            classification=classification,
            factors={k: round(v, 2) for k, v in factors.items()},
            project_type=project_type,
            last_modified=last_modified,
            warnings=warnings,
            protected=protected
        )

    def _is_protected(self, path: str) -> bool:
        """Check if directory path contains protected components"""
        path_parts = Path(path).parts
        return any(
            protected in path_parts
            for protected in self.config.PROTECTED_PATHS
        )

    def _has_critical_files(self, path: str) -> bool:
        """Check if directory contains critical files"""
        try:
            files = os.listdir(path)
            return any(
                critical in files
                for critical in self.config.CRITICAL_FILES
            )
        except (OSError, PermissionError):
            return False

    def _detect_project_type(self, path: str) -> Optional[str]:
        """Detect project type based on indicator files"""
        try:
            files = set(os.listdir(path))

            for project_type, indicators in self.config.PROJECT_INDICATORS.items():
                if any(indicator in files for indicator in indicators):
                    return project_type

        except (OSError, PermissionError):
            pass

        return None

    def _score_time_decay(self, path: str, base_time: float) -> float:
        """
        Score based on recency of modification

        Scoring:
        - Last 7 days: +10
        - Last 30 days: +5 to +10
        - Last 90 days: +0 to +5
        - Older: -5 to 0
        """
        try:
            last_mod = self._get_last_modified(path)
            days_old = (base_time - last_mod) / (24 * 3600)

            if days_old < 7:
                return 10
            elif days_old < 30:
                return 10 - (days_old - 7) * (5 / 23)  # Linear decay from 10 to 5
            elif days_old < 90:
                return 5 - (days_old - 30) * (5 / 60)  # Linear decay from 5 to 0
            else:
                return max(-5, -(days_old - 90) * (5 / 180))  # Decay to -5

        except (OSError, PermissionError):
            return 0

    def _score_git_activity(self, path: str) -> float:
        """
        Score based on git repository activity

        Checks:
        - Recent commits (last 30 days): +15
        - Branch count: +5 (multiple branches)
        - Uncommitted changes: +10
        - Is git repo: +5
        """
        score = 0

        # Check if git repo exists
        git_dir = os.path.join(path, ".git")
        if not os.path.isdir(git_dir):
            return 0

        score += 5  # Base score for being a git repo

        try:
            # Check for recent commits
            result = subprocess.run(
                ["git", "-C", path, "log", "--since=30 days ago", "--oneline"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                commit_count = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
                if commit_count > 0:
                    score += min(15, commit_count * 1.5)  # Up to +15 for commits

            # Check branch count
            result = subprocess.run(
                ["git", "-C", path, "branch", "-a"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                branch_count = len(result.stdout.strip().split("\n"))
                if branch_count > 1:
                    score += 5

            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "-C", path, "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                score += 10

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass

        return score

    def _score_dependencies(self, path: str, project_type: Optional[str]) -> float:
        """
        Score based on dependency management files

        Indicators:
        - Has dependency file: +10
        - Lock file present: +5
        - Multiple dependency systems: +3
        """
        score = 0

        try:
            files = set(os.listdir(path))

            # Check for dependency files
            dependency_files = [
                "package.json", "requirements.txt", "Cargo.toml", "go.mod",
                "pom.xml", "Gemfile", "composer.json", "Pipfile", "pyproject.toml"
            ]

            lock_files = [
                "package-lock.json", "yarn.lock", "Cargo.lock", "go.sum",
                "Gemfile.lock", "composer.lock", "Pipfile.lock", "poetry.lock"
            ]

            dep_count = sum(1 for f in dependency_files if f in files)
            lock_count = sum(1 for f in lock_files if f in files)

            if dep_count > 0:
                score += 10

            if lock_count > 0:
                score += 5

            if dep_count > 1:
                score += 3

        except (OSError, PermissionError):
            pass

        return score

    def _score_documentation(self, path: str) -> float:
        """
        Score based on documentation presence

        Indicators:
        - README file: +8
        - Additional docs: +2 per file (max +10)
        - docs/ directory: +5
        """
        score = 0

        try:
            files = os.listdir(path)
            files_lower = [f.lower() for f in files]

            # Check for README
            readme_variants = ["readme.md", "readme.txt", "readme.rst", "readme"]
            if any(variant in files_lower for variant in readme_variants):
                score += 8

            # Check for other documentation files
            doc_files = [
                "contributing.md", "changelog.md", "license", "license.md",
                "code_of_conduct.md", "security.md", "api.md"
            ]

            doc_count = sum(1 for doc in doc_files if doc in files_lower)
            score += min(10, doc_count * 2)

            # Check for docs directory
            if "docs" in files_lower:
                docs_path = os.path.join(path, "docs")
                if os.path.isdir(docs_path):
                    score += 5

        except (OSError, PermissionError):
            pass

        return score

    def _score_file_activity(self, path: str) -> float:
        """
        Score based on file count and variety

        Indicators:
        - File count > 10: +5
        - Multiple file types: +3
        - Source code files: +5
        """
        score = 0

        try:
            file_count = 0
            extensions = set()
            has_source = False

            source_extensions = {
                ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java",
                ".c", ".cpp", ".h", ".hpp", ".rb", ".php", ".swift", ".kt"
            }

            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    file_count += 1
                    ext = os.path.splitext(item)[1].lower()
                    if ext:
                        extensions.add(ext)
                    if ext in source_extensions:
                        has_source = True

            if file_count > 10:
                score += 5

            if len(extensions) > 3:
                score += 3

            if has_source:
                score += 5

        except (OSError, PermissionError):
            pass

        return score

    def _score_project_structure(self, path: str, project_type: Optional[str]) -> float:
        """
        Score based on expected project structure

        Indicators:
        - Standard directories present: +2 each (max +10)
        - Test directory: +5
        - CI/CD config: +5
        """
        score = 0

        try:
            items = os.listdir(path)
            items_lower = [item.lower() for item in items]

            # Standard directories
            standard_dirs = ["src", "lib", "test", "tests", "docs", "examples", "scripts"]
            dir_count = sum(
                1 for d in standard_dirs
                if d in items_lower and os.path.isdir(os.path.join(path, d))
            )
            score += min(10, dir_count * 2)

            # Test directory
            if any(t in items_lower for t in ["test", "tests", "__tests__", "spec"]):
                score += 5

            # CI/CD configuration
            ci_files = [".github", ".gitlab-ci.yml", ".travis.yml", "jenkinsfile", ".circleci"]
            if any(ci in items_lower for ci in ci_files):
                score += 5

        except (OSError, PermissionError):
            pass

        return score

    def _get_last_modified(self, path: str) -> float:
        """Get the most recent modification time in directory tree"""
        try:
            latest = os.path.getmtime(path)

            # Sample some files for performance (don't traverse entire tree)
            count = 0
            for root, dirs, files in os.walk(path):
                # Skip hidden and protected directories
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in self.config.PROTECTED_PATHS]

                for file in files[:10]:  # Sample first 10 files per directory
                    try:
                        file_path = os.path.join(root, file)
                        mtime = os.path.getmtime(file_path)
                        latest = max(latest, mtime)
                        count += 1

                        if count > 50:  # Don't check more than 50 files total
                            return latest
                    except (OSError, PermissionError):
                        continue

                if count > 50:
                    break

            return latest

        except (OSError, PermissionError):
            return 0

    def score_batch(self, paths: List[str], base_time: Optional[float] = None) -> List[DirectoryScore]:
        """Score multiple directories in batch"""
        return [self.score_directory(path, base_time) for path in paths]

    def export_results(self, scores: List[DirectoryScore], format: str = "json") -> str:
        """
        Export scoring results in specified format

        Args:
            scores: List of DirectoryScore objects
            format: Output format ("json", "csv", "markdown")

        Returns:
            Formatted string output
        """
        if format == "json":
            return json.dumps([asdict(s) for s in scores], indent=2)

        elif format == "csv":
            lines = ["Path,Score,Classification,ProjectType,Protected"]
            for score in scores:
                lines.append(
                    f"{score.path},{score.total_score},{score.classification},"
                    f"{score.project_type or 'unknown'},{score.protected}"
                )
            return "\n".join(lines)

        elif format == "markdown":
            lines = ["# Directory Activity Scores\n"]
            lines.append("| Path | Score | Classification | Type | Protected |")
            lines.append("|------|-------|----------------|------|-----------|")

            for score in scores:
                lines.append(
                    f"| {score.path} | {score.total_score} | {score.classification} | "
                    f"{score.project_type or 'N/A'} | {'✓' if score.protected else '✗'} |"
                )

            return "\n".join(lines)

        else:
            raise ValueError(f"Unsupported format: {format}")


def main():
    """CLI interface for directory scoring"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Directory Activity Scoring Algorithm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Score a single directory
  python scoring.py /path/to/project

  # Score multiple directories
  python scoring.py /path/to/dir1 /path/to/dir2 /path/to/dir3

  # Export as JSON
  python scoring.py --format json /path/to/project

  # Export as Markdown
  python scoring.py --format markdown /path/to/project > report.md

  # Show detailed breakdown
  python scoring.py --verbose /path/to/project
        """
    )

    parser.add_argument(
        "paths",
        nargs="+",
        help="Directory paths to score"
    )

    parser.add_argument(
        "--format",
        choices=["json", "csv", "markdown", "text"],
        default="text",
        help="Output format (default: text)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed factor breakdown"
    )

    parser.add_argument(
        "--threshold-active",
        type=float,
        default=20,
        help="Score threshold for 'Active' classification (default: 20)"
    )

    parser.add_argument(
        "--threshold-borderline",
        type=float,
        default=0,
        help="Score threshold for 'Borderline' classification (default: 0)"
    )

    args = parser.parse_args()

    # Update config with custom thresholds
    config = ScoringConfig()
    config.ACTIVE_THRESHOLD = args.threshold_active
    config.BORDERLINE_THRESHOLD = args.threshold_borderline

    # Score directories
    scorer = DirectoryScorer(config)
    scores = scorer.score_batch(args.paths)

    # Output results
    if args.format in ["json", "csv", "markdown"]:
        print(scorer.export_results(scores, args.format))
    else:
        # Text format with optional verbosity
        for score in scores:
            print(f"\n{'='*70}")
            print(f"Path: {score.path}")
            print(f"Score: {score.total_score}")
            print(f"Classification: {score.classification}")
            print(f"Project Type: {score.project_type or 'Unknown'}")
            print(f"Protected: {'Yes' if score.protected else 'No'}")
            print(f"Last Modified: {datetime.fromtimestamp(score.last_modified).strftime('%Y-%m-%d %H:%M:%S')}")

            if score.warnings:
                print(f"Warnings: {', '.join(score.warnings)}")

            if args.verbose:
                print("\nFactor Breakdown:")
                for factor, value in score.factors.items():
                    weight = config.WEIGHTS.get(factor, 1.0)
                    weighted = value * weight
                    print(f"  {factor:20s}: {value:6.2f} (weight: {weight:.1f}, weighted: {weighted:.2f})")

            print('='*70)


if __name__ == "__main__":
    main()
