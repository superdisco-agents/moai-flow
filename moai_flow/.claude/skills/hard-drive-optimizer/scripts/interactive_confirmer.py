#!/usr/bin/env python3
"""
Interactive per-project confirmation flow.

Shows project details and asks user for Y/N/S/Q/I confirmation.
"""

from pathlib import Path
from typing import Optional


class InteractiveConfirmer:
    """
    Per-project interactive confirmation system.
    """

    def __init__(self, verbose: bool = True):
        """Initialize confirmer."""
        self.verbose = verbose

    def confirm_deletion(self, project_name: str, project_path: str,
                        dependencies: list, size_bytes: int, cy4_score: int,
                        days_since_modified: int, current: int, total: int) -> str:
        """
        Show project details and ask for confirmation.

        Args:
            project_name: Project name
            project_path: Full path to project
            dependencies: List of dependency types
            size_bytes: Total size in bytes
            cy4_score: Activity score 0-100
            days_since_modified: Days since modification
            current: Current project number
            total: Total projects to review

        Returns:
            'yes': Delete this project
            'no'/'skip': Skip this project
            'quit': Stop entire process
            'info': Show more info (then re-ask)
        """
        risk_label = self._get_risk_label(cy4_score)
        size_str = self._format_size(size_bytes)

        print(f"\n{'━' * 60}")
        print(f"Project {current}/{total}: {project_name}")
        print(f"{'━' * 60}")
        print(f"📁 {project_path}")
        print(f"📦 Dependencies: {', '.join(dependencies)}")
        print(f"💾 Size: {size_str}")
        print(f"🔢 cy4 Score: {cy4_score}/100 ({risk_label})")
        print(f"📅 Days inactive: {days_since_modified}")
        print()

        while True:
            response = input("❓ Delete dependencies? [Y/N/S/Q/I]: ").strip().lower()

            if response in ['y', 'yes']:
                return 'yes'
            elif response in ['n', 'no']:
                return 'skip'
            elif response in ['s', 'skip']:
                return 'skip'
            elif response in ['q', 'quit']:
                return 'quit'
            elif response in ['i', 'info']:
                self._show_detailed_info(project_path)
                continue
            else:
                print("   Invalid input. Use: Y (yes), N (no), S (skip), Q (quit), I (info)")

    def confirm_batch(self, count: int, total_size: int) -> bool:
        """
        Batch confirmation for LOW-risk projects.

        Args:
            count: Number of projects to delete
            total_size: Total size to recover

        Returns:
            True if user confirms batch deletion
        """
        size_str = self._format_size(total_size)

        print(f"\n{'━' * 60}")
        print(f"Batch Confirmation - LOW Risk Projects")
        print(f"{'━' * 60}")
        print(f"Projects: {count}")
        print(f"Total recovery: {size_str}")
        print()

        response = input("❓ Delete all? [Y/N]: ").strip().lower()
        return response in ['y', 'yes']

    def show_dry_run_report(self, candidates: list) -> None:
        """
        Show dry-run report before deletion.

        Args:
            candidates: List of (name, size, cy4_score) tuples
        """
        if not candidates:
            print("🎉 No projects to clean up!")
            return

        print(f"\n{'━' * 60}")
        print(f"📊 Dry-Run Report")
        print(f"{'━' * 60}")
        print(f"Candidates: {len(candidates)}")
        print()

        total_size = 0
        for name, size, cy4 in candidates:
            self._print_project_row(name, size, cy4)
            total_size += size

        print()
        print(f"{'━' * 60}")
        print(f"Total recovery: {self._format_size(total_size)}")
        print(f"{'━' * 60}")

    @staticmethod
    def _get_risk_label(cy4_score: int) -> str:
        """Convert cy4 score to risk label."""
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

    @staticmethod
    def _format_size(bytes_size: int) -> str:
        """Format bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} TB"

    @staticmethod
    def _print_project_row(name: str, size_bytes: int, cy4_score: int) -> None:
        """Print project row in report."""
        risk = "🟢" if cy4_score < 41 else "🟡" if cy4_score < 61 else "🟠"
        size_str = InteractiveConfirmer._format_size(size_bytes)
        print(f"   {risk} {size_str:>10} {cy4_score:3}/100 {name}")

    @staticmethod
    def _show_detailed_info(project_path: str) -> None:
        """Show detailed information about project."""
        print(f"\n📋 Detailed Information:")
        print(f"   Full path: {project_path}")
        print(f"   Available commands:")
        print(f"     Y/yes  - Delete dependencies")
        print(f"     N/no   - Skip this project")
        print(f"     S/skip - Skip this project")
        print(f"     Q/quit - Stop entire process")
        print(f"     I/info - Show this info again")
        print()


def main():
    """Test the interactive confirmer."""
    confirmer = InteractiveConfirmer(verbose=True)

    # Test dry-run report
    candidates = [
        ("old-project-1", 500 * 1024 * 1024, 15),
        ("old-project-2", 300 * 1024 * 1024, 18),
        ("legacy-app", 1024 * 1024 * 1024, 8),
    ]

    confirmer.show_dry_run_report(candidates)

    print("\n(In interactive mode, this would continue with per-project confirmation)")


if __name__ == "__main__":
    main()
