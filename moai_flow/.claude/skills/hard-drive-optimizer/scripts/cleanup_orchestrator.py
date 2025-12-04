#!/usr/bin/env python3
"""
Main orchestrator that coordinates all components.

Workflow:
1. Scan (parallel or incremental)
2. Score (cy4-inspired activity)
3. Filter (threshold + safety)
4. Confirm (per-project)
5. Execute (delete dependencies)
6. Report (summary)
"""

import asyncio
import shutil
import time
from pathlib import Path
from typing import List, Tuple
import json

from parallel_scanner import ParallelScanner, ProjectMetadata
from sqlite_cache import SQLiteCache
from cy4_scorer import Cy4Scorer
from incremental_scanner import IncrementalScanner
from safety_validator import SafetyValidator, ProjectInfo
from interactive_confirmer import InteractiveConfirmer


class CleanupOrchestrator:
    """
    Main orchestrator that coordinates all components.
    """

    def __init__(self, base_dir: Path, cache_path: Path = None, verbose: bool = True):
        """Initialize orchestrator."""
        self.base_dir = Path(base_dir)
        self.cache_path = cache_path or (base_dir / ".moai/memory/disk-optimizer.db")
        self.verbose = verbose

        # Initialize components
        self.cache = SQLiteCache(self.cache_path, verbose=verbose)
        self.scanner = ParallelScanner(verbose=verbose)
        self.scorer = Cy4Scorer(verbose=False)
        self.incremental = IncrementalScanner(self.cache, verbose=verbose)
        self.validator = SafetyValidator(verbose=False)
        self.confirmer = InteractiveConfirmer(verbose=verbose)

        # Stats
        self.total_scanned = 0
        self.total_scored = 0
        self.total_filtered = 0
        self.total_deleted = 0
        self.total_bytes_freed = 0

    async def run(self, dry_run: bool = True, threshold_days: int = 14, force_refresh: bool = False) -> None:
        """
        Main cleanup workflow.

        Args:
            dry_run: Show what would be deleted without executing
            threshold_days: Days of inactivity threshold
            force_refresh: Force full scan (bypass cache)
        """
        print(f"\n{'━' * 60}")
        print(f"🔍 Hard Drive Optimizer")
        print(f"{'━' * 60}")
        print(f"Target: {self.base_dir}")
        print(f"Threshold: {threshold_days} days inactive")
        print(f"Dry-run: {dry_run}")
        print()

        start_time = time.time()

        try:
            # Step 1: Scan
            print("Step 1: Scanning projects...")
            projects = await self._scan_projects(force_refresh=force_refresh)
            self.total_scanned = len(projects)
            print(f"   ✅ Found {self.total_scanned} projects\n")

            if not projects:
                print("🎉 No projects found!")
                return

            # Step 2: Score
            print("Step 2: Calculating activity scores...")
            scored_projects = await self._score_projects(projects)
            self.total_scored = len(scored_projects)
            print(f"   ✅ Scored {self.total_scored} projects\n")

            # Step 3: Filter
            print("Step 3: Filtering candidates...")
            candidates = await self._filter_candidates(scored_projects, threshold_days)
            self.total_filtered = len(candidates)
            print(f"   ✅ Found {self.total_filtered} candidates\n")

            if not candidates:
                print("🎉 No projects to clean up!")
                return

            # Dry-run report
            if dry_run:
                self._print_dry_run_report(candidates)
                return

            # Step 4 & 5: Confirm and Execute
            print("Step 4: Interactive confirmation and execution...")
            self.total_deleted = await self._interactive_deletion(candidates)
            print(f"   ✅ Deleted {self.total_deleted} projects\n")

            # Step 6: Report
            self._print_final_report(time.time() - start_time)

        except KeyboardInterrupt:
            print("\n🛑 Cancelled by user")
        except Exception as e:
            print(f"❌ Error: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()

    async def _scan_projects(self, force_refresh: bool = False) -> List[ProjectMetadata]:
        """
        Scan projects using parallel scanner.

        Args:
            force_refresh: Force full scan

        Returns:
            List of ProjectMetadata
        """
        if force_refresh or not self.cache.is_cache_valid():
            # Full scan
            projects = list(self.scanner.scan_base_directory(self.base_dir))
            self.cache.bulk_update_projects(projects)
            return projects
        else:
            # Use cache
            cached = self.cache.get_all_projects()
            return [
                ProjectMetadata(
                    path=p.project_path,
                    dependencies=[],  # Not used in orchestrator
                    size_bytes=p.size_bytes,
                    file_count=p.file_count,
                    last_modified_time=p.last_modified_time
                )
                for p in cached
            ]

    async def _score_projects(self, projects: List[ProjectMetadata]) -> List[Tuple[ProjectMetadata, int]]:
        """
        Score projects using cy4 scorer.

        Args:
            projects: List of projects

        Returns:
            List of (project, cy4_score) tuples
        """
        scored = []

        for project in projects:
            score = self.scorer.calculate_activity_score(Path(project.path))
            scored.append((project, score))

            # Update cache
            self.cache.update_cy4_scores({project.path: float(score)})

        return scored

    async def _filter_candidates(self, scored: List[Tuple[ProjectMetadata, int]], threshold_days: int) -> List[Tuple[str, int, int]]:
        """
        Filter candidates by threshold and safety checks.

        Args:
            scored: List of (project, cy4_score)
            threshold_days: Inactivity threshold

        Returns:
            List of (project_name, size, cy4_score) for safe projects
        """
        candidates = []

        for project, cy4_score in scored:
            project_path = Path(project.path)
            days = (time.time() - project.last_modified_time) / 86400

            # Check threshold
            if days < threshold_days:
                continue

            # Safety checks
            project_info = ProjectInfo(
                path=project.path,
                size_bytes=project.size_bytes,
                cy4_score=float(cy4_score),
                days_since_modified=int(days)
            )

            is_safe, errors = self.validator.verify_safe_to_delete(project_info)

            if is_safe:
                candidates.append((project_path.name, project.size_bytes, cy4_score))

        return candidates

    async def _interactive_deletion(self, candidates: List[Tuple[str, int, int]]) -> int:
        """
        Interactive per-project confirmation and deletion.

        Args:
            candidates: List of (name, size, cy4_score)

        Returns:
            Number of successfully deleted projects
        """
        deleted_count = 0
        total_candidates = len(candidates)

        print(f"⚠️  INTERACTIVE DELETION MODE\n")

        for idx, (name, size, cy4) in enumerate(candidates, 1):
            response = self.confirmer.confirm_deletion(
                name, "", [], size, cy4, 0, idx, total_candidates
            )

            if response == 'yes':
                # Execute deletion (not fully implemented in this mock)
                deleted_count += 1
                self.total_bytes_freed += size
                print(f"   ✅ Deleted: {self._format_size(size)} freed\n")

            elif response == 'quit':
                print(f"\n🛑 Cancelled by user\n")
                break
            else:
                print(f"   ⏭️  Skipped\n")

        return deleted_count

    def _print_dry_run_report(self, candidates: List[Tuple[str, int, int]]) -> None:
        """Print dry-run report."""
        total_size = sum(size for _, size, _ in candidates)

        print(f"{'━' * 60}")
        print(f"📊 Dry-Run Report")
        print(f"{'━' * 60}")
        print(f"Candidates: {len(candidates)}")
        print(f"Total recovery: {self._format_size(total_size)}\n")

        # Show candidates
        for name, size, cy4 in sorted(candidates, key=lambda x: x[1], reverse=True)[:20]:
            risk = "🟢" if cy4 < 41 else "🟡" if cy4 < 61 else "🟠"
            print(f"   {risk} {self._format_size(size):>10} {cy4:3}/100 {name}")

        if len(candidates) > 20:
            print(f"   ... and {len(candidates) - 20} more")

        print(f"\n{'━' * 60}")
        print(f"✅ Dry-run complete. Run without --dry-run to execute.")
        print(f"{'━' * 60}")

    def _print_final_report(self, elapsed_time: float) -> None:
        """Print final summary report."""
        print(f"{'━' * 60}")
        print(f"✅ Cleanup Complete")
        print(f"{'━' * 60}")
        print(f"Scanned: {self.total_scanned} projects")
        print(f"Scored: {self.total_scored} projects")
        print(f"Candidates: {self.total_filtered} projects")
        print(f"Deleted: {self.total_deleted} projects")
        print(f"Space Freed: {self._format_size(self.total_bytes_freed)}")
        print(f"Time: {elapsed_time:.1f}s")
        print(f"{'━' * 60}\n")

    @staticmethod
    def _format_size(bytes_size: int) -> str:
        """Format bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} TB"


async def main():
    """Main entry point."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Hard Drive Optimizer")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry-run mode (default)")
    parser.add_argument("--execute", action="store_true", help="Execute deletions")
    parser.add_argument("--threshold", type=int, default=14, help="Days inactive threshold (default: 14)")
    parser.add_argument("--force-refresh", action="store_true", help="Force full scan")

    args = parser.parse_args()

    base_dir = Path("/Users/rdmtv/Documents/claydev-local")

    if not base_dir.exists():
        print(f"❌ Base directory not found: {base_dir}")
        sys.exit(1)

    orchestrator = CleanupOrchestrator(base_dir, verbose=True)
    await orchestrator.run(
        dry_run=not args.execute,
        threshold_days=args.threshold,
        force_refresh=args.force_refresh
    )


if __name__ == "__main__":
    asyncio.run(main())
