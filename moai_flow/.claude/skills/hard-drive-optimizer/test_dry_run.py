#!/usr/bin/env python3
"""Test script for Hard Drive Optimizer dry-run."""

import asyncio
import sys
import time
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from cleanup_orchestrator import CleanupOrchestrator


async def main():
    """Run dry-run test on actual directory."""
    print('\n' + '=' * 70)
    print('🚀 Hard Drive Optimizer - Dry-Run Test')
    print('=' * 70)

    base_dir = Path('/Users/rdmtv/Documents/claydev-local')
    cache_path = base_dir / '.moai/memory/disk-optimizer.db'

    start_time = time.time()

    try:
        orchestrator = CleanupOrchestrator(base_dir, cache_path=cache_path, verbose=True)
        await orchestrator.run(dry_run=True, threshold_days=14, force_refresh=True)

        elapsed = time.time() - start_time

        print('\n' + '=' * 70)
        print(f'⏱️  Performance Results')
        print('=' * 70)
        print(f'Total time: {elapsed:.1f} seconds')
        print(f'Projects scanned: {orchestrator.total_scanned}')
        print(f'Projects scored: {orchestrator.total_scored}')
        print(f'Candidates found: {orchestrator.total_filtered}')

        # Performance assessment
        if elapsed < 300:  # 5 minutes
            print(f'\n✅ PERFORMANCE TARGET MET: {elapsed:.1f}s < 300s')
        else:
            print(f'\n⚠️  PERFORMANCE TARGET MIGHT EXCEED: {elapsed:.1f}s')

        return True

    except Exception as e:
        print(f'\n❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
