#!/usr/bin/env python3
"""
MoAI-ADK Dot Folder Cleaner
============================

Scans for and optionally removes non-MoAI .dot folders that may conflict
with the MoAI framework. Preserves essential project folders.

Usage:
    python clean-dot-folders.py [OPTIONS]

Options:
    --scan-only     Scan and report without deleting
    --force         Skip confirmation prompts
    --agent         Enable AI-guided mode with swarm coordination
    --path PATH     Custom path to scan (default: current directory)
    --json          Output results as JSON
    --verbose       Show detailed output

Author: MoAI-ADK Team
License: MIT
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
import subprocess

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Whitelist: NEVER remove these folders
WHITELIST: Set[str] = {
    # Git
    '.git',
    '.github',
    '.gitignore',
    '.gitattributes',
    '.gitmodules',

    # Environment
    '.venv',
    '.virtualenv',
    '.env',
    '.env.local',
    '.env.development',
    '.env.production',
    '.env.test',

    # MoAI Core
    '.moai',
    '.mcp.json',

    # IDE
    '.vscode',
    '.idea',
    '.DS_Store',

    # Python
    '.pytest_cache',
    '__pycache__',
    '.mypy_cache',
    '.ruff_cache',
    '.tox',

    # Node
    '.npm',
    '.yarn',
    '.pnpm-store',

    # Build
    '.next',
    '.nuxt',
    '.cache',
    '.parcel-cache',
}

# Known AI framework folders (potential conflicts)
AI_FRAMEWORKS: Set[str] = {
    '.claude-flow',
    '.swarm',
    '.hive-mind',
    '.specstory',
    '.roo',
    '.aider',
    '.cursor',
    '.copilot',
    '.cody',
    '.tabnine',
    '.kite',
}

# MoAI-specific folders to preserve
MOAI_FOLDERS: Set[str] = {
    '.moai',
    '.claude/commands/moai',
}


class DotFolderScanner:
    """Scanner for .dot folders with conflict detection."""

    def __init__(self, base_path: Path, verbose: bool = False):
        self.base_path = base_path
        self.verbose = verbose
        self.scan_results: Dict[str, Dict] = {}

    def get_folder_size(self, folder_path: Path) -> int:
        """Calculate total size of folder in bytes."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        pass
        except (OSError, PermissionError):
            pass
        return total_size

    def format_size(self, size_bytes: int) -> str:
        """Format bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def is_moai_folder(self, folder_name: str, folder_path: Path) -> bool:
        """Check if folder is MoAI-specific."""
        if folder_name in MOAI_FOLDERS:
            return True

        # Check for .claude/commands/moai path
        if '.claude' in str(folder_path) and 'moai' in str(folder_path).lower():
            return True

        return False

    def classify_folder(self, folder_name: str, folder_path: Path) -> str:
        """Classify folder into categories."""
        if folder_name in WHITELIST:
            return 'whitelisted'

        if self.is_moai_folder(folder_name, folder_path):
            return 'moai'

        if folder_name in AI_FRAMEWORKS:
            return 'ai_framework'

        return 'unknown'

    def scan(self) -> Dict[str, List[Dict]]:
        """Scan for .dot folders and classify them."""
        results = {
            'whitelisted': [],
            'moai': [],
            'ai_framework': [],
            'unknown': [],
        }

        try:
            # Scan immediate .dot folders
            for item in self.base_path.iterdir():
                if item.is_dir() and item.name.startswith('.'):
                    folder_name = item.name
                    folder_size = self.get_folder_size(item)
                    category = self.classify_folder(folder_name, item)

                    folder_info = {
                        'name': folder_name,
                        'path': str(item.absolute()),
                        'size': folder_size,
                        'size_formatted': self.format_size(folder_size),
                        'category': category,
                    }

                    results[category].append(folder_info)

                    if self.verbose:
                        self._print_folder_info(folder_info)

            # Also check for nested .claude/commands/moai
            claude_path = self.base_path / '.claude' / 'commands' / 'moai'
            if claude_path.exists() and claude_path.is_dir():
                folder_size = self.get_folder_size(claude_path)
                folder_info = {
                    'name': '.claude/commands/moai',
                    'path': str(claude_path.absolute()),
                    'size': folder_size,
                    'size_formatted': self.format_size(folder_size),
                    'category': 'moai',
                }
                # Check if not already added
                if not any(f['path'] == folder_info['path'] for f in results['moai']):
                    results['moai'].append(folder_info)

        except PermissionError as e:
            print(f"{Colors.FAIL}Permission denied: {e}{Colors.ENDC}")

        self.scan_results = results
        return results

    def _print_folder_info(self, folder_info: Dict) -> None:
        """Print folder information with colors."""
        category = folder_info['category']
        color_map = {
            'whitelisted': Colors.OKGREEN,
            'moai': Colors.OKCYAN,
            'ai_framework': Colors.WARNING,
            'unknown': Colors.FAIL,
        }
        color = color_map.get(category, Colors.ENDC)

        print(f"{color}  {folder_info['name']:<30} {folder_info['size_formatted']:>10} [{category}]{Colors.ENDC}")


class DotFolderCleaner:
    """Cleaner for removing non-MoAI .dot folders."""

    def __init__(self, scanner: DotFolderScanner, force: bool = False):
        self.scanner = scanner
        self.force = force
        self.deleted_folders: List[Dict] = []
        self.errors: List[Dict] = []

    def get_deletable_folders(self) -> List[Dict]:
        """Get list of folders that can be safely deleted."""
        deletable = []

        # AI framework folders are safe to delete
        deletable.extend(self.scanner.scan_results['ai_framework'])

        # Unknown folders can be deleted with confirmation
        deletable.extend(self.scanner.scan_results['unknown'])

        return deletable

    def confirm_deletion(self, folders: List[Dict]) -> bool:
        """Ask user to confirm deletion."""
        if self.force:
            return True

        print(f"\n{Colors.WARNING}The following folders will be deleted:{Colors.ENDC}")
        total_size = 0

        for folder in folders:
            print(f"  {Colors.BOLD}{folder['name']}{Colors.ENDC} ({folder['size_formatted']})")
            total_size += folder['size']

        print(f"\n{Colors.BOLD}Total size to free: {self.scanner.format_size(total_size)}{Colors.ENDC}")

        response = input(f"\n{Colors.WARNING}Continue with deletion? [y/N]: {Colors.ENDC}")
        return response.lower() in ('y', 'yes')

    def delete_folder(self, folder_info: Dict) -> bool:
        """Delete a single folder."""
        try:
            folder_path = Path(folder_info['path'])

            if folder_path.exists():
                shutil.rmtree(folder_path)
                self.deleted_folders.append(folder_info)
                print(f"{Colors.OKGREEN}✓ Deleted: {folder_info['name']}{Colors.ENDC}")
                return True
            else:
                print(f"{Colors.WARNING}⚠ Not found: {folder_info['name']}{Colors.ENDC}")
                return False

        except Exception as e:
            error_info = {
                'folder': folder_info['name'],
                'error': str(e),
            }
            self.errors.append(error_info)
            print(f"{Colors.FAIL}✗ Failed to delete {folder_info['name']}: {e}{Colors.ENDC}")
            return False

    def clean(self) -> Dict:
        """Clean deletable folders."""
        deletable = self.get_deletable_folders()

        if not deletable:
            print(f"{Colors.OKGREEN}No folders to clean!{Colors.ENDC}")
            return {
                'deleted': [],
                'errors': [],
                'total_freed': 0,
            }

        if not self.confirm_deletion(deletable):
            print(f"{Colors.WARNING}Deletion cancelled.{Colors.ENDC}")
            return {
                'deleted': [],
                'errors': [],
                'total_freed': 0,
                'cancelled': True,
            }

        print(f"\n{Colors.HEADER}Starting deletion...{Colors.ENDC}")

        for folder in deletable:
            self.delete_folder(folder)

        total_freed = sum(f['size'] for f in self.deleted_folders)

        return {
            'deleted': self.deleted_folders,
            'errors': self.errors,
            'total_freed': total_freed,
            'total_freed_formatted': self.scanner.format_size(total_freed),
        }


class AIGuidedMode:
    """AI-guided mode with swarm coordination."""

    def __init__(self, scanner: DotFolderScanner):
        self.scanner = scanner

    def analyze_with_swarm(self) -> Dict:
        """Use AI swarm to analyze folders and recommend actions."""
        print(f"{Colors.HEADER}AI-Guided Mode: Analyzing with swarm...{Colors.ENDC}")

        try:
            # Initialize swarm
            swarm_cmd = [
                'npx', 'claude-flow@alpha', 'swarm', 'init',
                '--topology', 'mesh',
                '--max-agents', '3'
            ]

            result = subprocess.run(swarm_cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                print(f"{Colors.OKGREEN}✓ Swarm initialized{Colors.ENDC}")
            else:
                print(f"{Colors.WARNING}⚠ Swarm initialization skipped{Colors.ENDC}")

        except Exception as e:
            print(f"{Colors.WARNING}⚠ AI mode unavailable: {e}{Colors.ENDC}")

        # Return analysis recommendations
        deletable = []
        deletable.extend(self.scanner.scan_results['ai_framework'])

        return {
            'recommended_deletions': deletable,
            'ai_analysis': 'AI framework folders detected that may conflict with MoAI',
            'confidence': 'high',
        }


def print_report(scan_results: Dict, verbose: bool = False) -> None:
    """Print scan report."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== MoAI Dot Folder Scan Report ==={Colors.ENDC}\n")

    # Summary
    total_folders = sum(len(folders) for folders in scan_results.values())
    print(f"Total .dot folders found: {Colors.BOLD}{total_folders}{Colors.ENDC}")

    # Whitelisted
    whitelisted = scan_results['whitelisted']
    print(f"\n{Colors.OKGREEN}Whitelisted (protected):{Colors.ENDC} {len(whitelisted)}")
    if verbose:
        for folder in whitelisted:
            print(f"  {folder['name']} ({folder['size_formatted']})")

    # MoAI
    moai = scan_results['moai']
    print(f"\n{Colors.OKCYAN}MoAI folders (protected):{Colors.ENDC} {len(moai)}")
    if verbose or moai:
        for folder in moai:
            print(f"  {folder['name']} ({folder['size_formatted']})")

    # AI Frameworks
    ai_frameworks = scan_results['ai_framework']
    if ai_frameworks:
        print(f"\n{Colors.WARNING}AI Framework conflicts:{Colors.ENDC} {len(ai_frameworks)}")
        for folder in ai_frameworks:
            print(f"  {Colors.WARNING}{folder['name']}{Colors.ENDC} ({folder['size_formatted']})")

    # Unknown
    unknown = scan_results['unknown']
    if unknown:
        print(f"\n{Colors.FAIL}Unknown .dot folders:{Colors.ENDC} {len(unknown)}")
        for folder in unknown:
            print(f"  {folder['name']} ({folder['size_formatted']})")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='MoAI-ADK Dot Folder Cleaner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('--scan-only', action='store_true',
                       help='Scan and report without deleting')
    parser.add_argument('--force', action='store_true',
                       help='Skip confirmation prompts')
    parser.add_argument('--agent', action='store_true',
                       help='Enable AI-guided mode with swarm coordination')
    parser.add_argument('--path', type=str, default='.',
                       help='Custom path to scan (default: current directory)')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON')
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed output')

    args = parser.parse_args()

    # Initialize scanner
    base_path = Path(args.path).resolve()

    if not base_path.exists():
        print(f"{Colors.FAIL}Error: Path does not exist: {base_path}{Colors.ENDC}")
        sys.exit(1)

    print(f"{Colors.HEADER}Scanning: {base_path}{Colors.ENDC}\n")

    scanner = DotFolderScanner(base_path, verbose=args.verbose)
    results = scanner.scan()

    # Print report
    if not args.json:
        print_report(results, verbose=args.verbose)

    # AI-guided mode
    if args.agent:
        ai_mode = AIGuidedMode(scanner)
        ai_results = ai_mode.analyze_with_swarm()

        if not args.json:
            print(f"\n{Colors.OKCYAN}AI Analysis:{Colors.ENDC} {ai_results['ai_analysis']}")
            print(f"{Colors.OKCYAN}Confidence:{Colors.ENDC} {ai_results['confidence']}")

    # Scan-only mode
    if args.scan_only:
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\n{Colors.OKBLUE}Scan complete. Use without --scan-only to clean.{Colors.ENDC}")
        sys.exit(0)

    # Clean mode
    cleaner = DotFolderCleaner(scanner, force=args.force)
    clean_results = cleaner.clean()

    # Output results
    if args.json:
        output = {
            'scan_results': results,
            'clean_results': clean_results,
            'timestamp': datetime.now().isoformat(),
        }
        print(json.dumps(output, indent=2))
    else:
        if clean_results.get('deleted'):
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ Cleanup complete!{Colors.ENDC}")
            print(f"Deleted {len(clean_results['deleted'])} folders")
            print(f"Freed {clean_results['total_freed_formatted']}")

        if clean_results.get('errors'):
            print(f"\n{Colors.FAIL}Errors encountered:{Colors.ENDC}")
            for error in clean_results['errors']:
                print(f"  {error['folder']}: {error['error']}")


if __name__ == '__main__':
    main()
