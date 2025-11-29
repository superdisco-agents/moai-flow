#!/usr/bin/env python3
"""
Claude-Flow Comprehensive Uninstaller
Safely removes all claude-flow directories and packages
Supports dry-run, backup, and AI-guided modes
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Try importing optional dependencies
try:
    from packaging import version as pkg_version
except ImportError:
    print("📦 Installing packaging...")
    subprocess.run([sys.executable, "-m", "pip", "install", "packaging", "-q"], check=True)
    from packaging import version as pkg_version


class Colors:
    """Terminal color codes"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ClaudeFlowUninstaller:
    """Main uninstaller class"""

    # Directories to remove
    DIRECTORIES = [
        '.claude-flow',
        '.swarm',
        '.hive-mind',
        '.specstory',
        'node_modules/.cache/claude-flow'
    ]

    # NPM packages to uninstall
    NPM_PACKAGES = [
        'claude-flow',
        '@claude-flow/core',
        '@claude-flow/cli'
    ]

    def __init__(self, dry_run: bool = False, backup: bool = False, verbose: bool = False):
        """
        Initialize uninstaller

        Args:
            dry_run: If True, only show what would be done
            backup: If True, backup directories before deletion
            verbose: If True, show detailed output
        """
        self.dry_run = dry_run
        self.backup = backup
        self.verbose = verbose
        self.base_dir = Path.cwd()
        self.removed_items: List[Dict] = []
        self.errors: List[Dict] = []
        self.total_size = 0

    def print_header(self):
        """Print formatted header"""
        mode = "DRY RUN" if self.dry_run else "UNINSTALL"
        backup_indicator = " + BACKUP" if self.backup else ""

        print(f"\n{Colors.BOLD}{Colors.RED}🗑️  Claude-Flow Uninstaller [{mode}{backup_indicator}]{Colors.END}")
        print("━" * 60)
        print()

    def get_directory_size(self, path: Path) -> int:
        """
        Calculate total size of directory

        Args:
            path: Directory path

        Returns:
            Size in bytes
        """
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except (OSError, PermissionError) as e:
            if self.verbose:
                print(f"   {Colors.YELLOW}⚠ Could not calculate size: {e}{Colors.END}")
        return total_size

    def format_size(self, size_bytes: int) -> str:
        """
        Format bytes to human-readable size

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def scan_directories(self) -> List[Dict]:
        """
        Scan for claude-flow directories

        Returns:
            List of dictionaries with directory info
        """
        print(f"{Colors.BOLD}📂 Scanning for claude-flow directories...{Colors.END}")
        print()

        found_dirs = []

        for dir_name in self.DIRECTORIES:
            dir_path = self.base_dir / dir_name

            if dir_path.exists():
                size = self.get_directory_size(dir_path)
                self.total_size += size

                dir_info = {
                    'name': dir_name,
                    'path': str(dir_path),
                    'size': size,
                    'size_formatted': self.format_size(size),
                    'type': 'directory'
                }
                found_dirs.append(dir_info)

                status = f"{Colors.GREEN}✓ Found{Colors.END}"
                print(f"  {status} {Colors.CYAN}{dir_name:<35}{Colors.END} ({dir_info['size_formatted']})")

        if not found_dirs:
            print(f"  {Colors.YELLOW}⚠ No claude-flow directories found{Colors.END}")

        print()
        return found_dirs

    def check_npm_packages(self) -> List[Dict]:
        """
        Check for globally installed npm packages

        Returns:
            List of dictionaries with package info
        """
        print(f"{Colors.BOLD}📦 Checking npm packages...{Colors.END}")
        print()

        found_packages = []

        try:
            # Get global npm packages
            result = subprocess.run(
                ['npm', 'list', '-g', '--json', '--depth=0'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                dependencies = data.get('dependencies', {})

                for package_name in self.NPM_PACKAGES:
                    if package_name in dependencies:
                        version = dependencies[package_name].get('version', 'unknown')
                        package_info = {
                            'name': package_name,
                            'version': version,
                            'type': 'npm-global'
                        }
                        found_packages.append(package_info)

                        status = f"{Colors.GREEN}✓ Found{Colors.END}"
                        print(f"  {status} {Colors.CYAN}{package_name:<35}{Colors.END} (v{version})")

        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError) as e:
            if self.verbose:
                print(f"  {Colors.YELLOW}⚠ Could not check npm packages: {e}{Colors.END}")

        if not found_packages:
            print(f"  {Colors.YELLOW}⚠ No claude-flow npm packages found{Colors.END}")

        print()
        return found_packages

    def backup_directory(self, dir_path: Path) -> Optional[str]:
        """
        Create backup of directory

        Args:
            dir_path: Path to directory to backup

        Returns:
            Backup archive path or None if failed
        """
        if not self.backup or self.dry_run:
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.base_dir / '_backups' / 'claude-flow-uninstall'
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_name = f"{dir_path.name}_{timestamp}"
        backup_path = backup_dir / backup_name

        try:
            print(f"  {Colors.BLUE}📦 Creating backup: {backup_name}{Colors.END}")
            shutil.copytree(dir_path, backup_path)
            return str(backup_path)
        except Exception as e:
            error_msg = f"Failed to backup {dir_path.name}: {e}"
            self.errors.append({
                'operation': 'backup',
                'target': str(dir_path),
                'error': str(e)
            })
            print(f"  {Colors.RED}✗ Backup failed: {e}{Colors.END}")
            return None

    def remove_directory(self, dir_info: Dict) -> bool:
        """
        Remove directory

        Args:
            dir_info: Directory information dictionary

        Returns:
            True if successful, False otherwise
        """
        dir_path = Path(dir_info['path'])

        print(f"  {Colors.YELLOW}🗑️  Removing: {dir_info['name']}{Colors.END}")

        # Backup if requested
        if self.backup:
            backup_path = self.backup_directory(dir_path)
            if backup_path:
                dir_info['backup_path'] = backup_path

        # Remove directory
        if not self.dry_run:
            try:
                shutil.rmtree(dir_path)
                print(f"     {Colors.GREEN}✓ Removed successfully{Colors.END}")
                dir_info['removed'] = True
                self.removed_items.append(dir_info)
                return True
            except Exception as e:
                error_msg = f"Failed to remove {dir_info['name']}: {e}"
                self.errors.append({
                    'operation': 'remove',
                    'target': dir_info['path'],
                    'error': str(e)
                })
                print(f"     {Colors.RED}✗ Removal failed: {e}{Colors.END}")
                dir_info['removed'] = False
                return False
        else:
            print(f"     {Colors.BLUE}ℹ Would remove (dry-run){Colors.END}")
            dir_info['removed'] = None  # Not applicable in dry-run
            return True

    def uninstall_npm_package(self, package_info: Dict) -> bool:
        """
        Uninstall npm package

        Args:
            package_info: Package information dictionary

        Returns:
            True if successful, False otherwise
        """
        package_name = package_info['name']

        print(f"  {Colors.YELLOW}🗑️  Uninstalling: {package_name}{Colors.END}")

        if not self.dry_run:
            try:
                result = subprocess.run(
                    ['npm', 'uninstall', '-g', package_name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    print(f"     {Colors.GREEN}✓ Uninstalled successfully{Colors.END}")
                    package_info['removed'] = True
                    self.removed_items.append(package_info)
                    return True
                else:
                    error_msg = result.stderr or "Unknown error"
                    self.errors.append({
                        'operation': 'npm-uninstall',
                        'target': package_name,
                        'error': error_msg
                    })
                    print(f"     {Colors.RED}✗ Uninstall failed: {error_msg}{Colors.END}")
                    package_info['removed'] = False
                    return False

            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                self.errors.append({
                    'operation': 'npm-uninstall',
                    'target': package_name,
                    'error': str(e)
                })
                print(f"     {Colors.RED}✗ Uninstall failed: {e}{Colors.END}")
                package_info['removed'] = False
                return False
        else:
            print(f"     {Colors.BLUE}ℹ Would uninstall (dry-run){Colors.END}")
            package_info['removed'] = None
            return True

    def clean_npm_cache(self) -> bool:
        """
        Clean npm cache

        Returns:
            True if successful, False otherwise
        """
        print(f"  {Colors.YELLOW}🧹 Cleaning npm cache...{Colors.END}")

        if not self.dry_run:
            try:
                result = subprocess.run(
                    ['npm', 'cache', 'clean', '--force'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    print(f"     {Colors.GREEN}✓ Cache cleaned{Colors.END}")
                    return True
                else:
                    print(f"     {Colors.YELLOW}⚠ Cache clean returned non-zero{Colors.END}")
                    return False

            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                print(f"     {Colors.RED}✗ Cache clean failed: {e}{Colors.END}")
                return False
        else:
            print(f"     {Colors.BLUE}ℹ Would clean cache (dry-run){Colors.END}")
            return True

    def verify_removal(self) -> Tuple[int, int]:
        """
        Verify that items were actually removed

        Returns:
            Tuple of (successfully_removed, still_exists)
        """
        if self.dry_run:
            return (0, 0)

        print(f"\n{Colors.BOLD}🔍 Verifying removal...{Colors.END}")
        print()

        removed_count = 0
        still_exists = 0

        for item in self.removed_items:
            if item['type'] == 'directory':
                path = Path(item['path'])
                if not path.exists():
                    removed_count += 1
                    print(f"  {Colors.GREEN}✓{Colors.END} {item['name']} - removed")
                else:
                    still_exists += 1
                    print(f"  {Colors.RED}✗{Colors.END} {item['name']} - still exists")

        print()
        return (removed_count, still_exists)

    def show_summary(self, dirs: List[Dict], packages: List[Dict]):
        """
        Show summary of what will be or was done

        Args:
            dirs: List of directories
            packages: List of packages
        """
        print(f"{Colors.BOLD}📊 Summary{Colors.END}")
        print("━" * 60)
        print()

        # Directories
        if dirs:
            print(f"{Colors.BOLD}Directories:{Colors.END}")
            for dir_info in dirs:
                status = "Would remove" if self.dry_run else (
                    "✓ Removed" if dir_info.get('removed') else "✗ Failed"
                )
                print(f"  {status:<15} {dir_info['name']:<35} ({dir_info['size_formatted']})")
                if dir_info.get('backup_path'):
                    print(f"                  ↳ Backed up to: {dir_info['backup_path']}")
            print()

        # Packages
        if packages:
            print(f"{Colors.BOLD}NPM Packages:{Colors.END}")
            for pkg_info in packages:
                status = "Would remove" if self.dry_run else (
                    "✓ Uninstalled" if pkg_info.get('removed') else "✗ Failed"
                )
                print(f"  {status:<15} {pkg_info['name']:<35} (v{pkg_info['version']})")
            print()

        # Total size
        print(f"{Colors.BOLD}Total space to be freed:{Colors.END} {Colors.CYAN}{self.format_size(self.total_size)}{Colors.END}")
        print()

        # Errors
        if self.errors:
            print(f"{Colors.BOLD}{Colors.RED}Errors encountered:{Colors.END}")
            for error in self.errors:
                print(f"  ✗ {error['operation']}: {error['target']}")
                print(f"    {error['error']}")
            print()

    def generate_report(self, dirs: List[Dict], packages: List[Dict]) -> Dict:
        """
        Generate JSON report

        Args:
            dirs: List of directories
            packages: List of packages

        Returns:
            Report dictionary
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'mode': 'dry-run' if self.dry_run else 'uninstall',
            'backup_enabled': self.backup,
            'base_directory': str(self.base_dir),
            'directories': dirs,
            'packages': packages,
            'total_size_bytes': self.total_size,
            'total_size_formatted': self.format_size(self.total_size),
            'errors': self.errors,
            'summary': {
                'directories_found': len(dirs),
                'packages_found': len(packages),
                'items_removed': len(self.removed_items),
                'errors_count': len(self.errors)
            }
        }

    def save_report(self, report: Dict, report_path: Path):
        """
        Save JSON report to file

        Args:
            report: Report dictionary
            report_path: Path to save report
        """
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"{Colors.GREEN}✓ Report saved to: {report_path}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to save report: {e}{Colors.END}")

    def run(self) -> int:
        """
        Run the uninstaller

        Returns:
            Exit code: 0 (success), 1 (error), 4 (cleanup failed)
        """
        self.print_header()

        # Scan
        dirs = self.scan_directories()
        packages = self.check_npm_packages()

        # Check if anything to do
        if not dirs and not packages:
            print(f"{Colors.GREEN}✓ No claude-flow installation found{Colors.END}")
            print()
            return 0

        # Show summary
        self.show_summary(dirs, packages)

        # Confirm unless dry-run
        if not self.dry_run:
            print(f"{Colors.BOLD}{Colors.RED}⚠️  WARNING: This will permanently remove claude-flow{Colors.END}")
            if self.backup:
                print(f"{Colors.BLUE}ℹ  Backups will be saved to _backups/claude-flow-uninstall/{Colors.END}")
            print()

            response = input(f"{Colors.BOLD}Proceed with uninstall? (yes/no): {Colors.END}")
            print()

            if response.lower() not in ['yes', 'y']:
                print(f"{Colors.YELLOW}✗ Uninstall cancelled{Colors.END}")
                print()
                return 0

        # Remove directories
        print(f"{Colors.BOLD}🗑️  Removing directories...{Colors.END}")
        print()
        for dir_info in dirs:
            self.remove_directory(dir_info)
        print()

        # Uninstall packages
        if packages:
            print(f"{Colors.BOLD}🗑️  Uninstalling npm packages...{Colors.END}")
            print()
            for pkg_info in packages:
                self.uninstall_npm_package(pkg_info)
            print()

            # Clean npm cache
            self.clean_npm_cache()
            print()

        # Verify
        if not self.dry_run and (dirs or packages):
            removed, still_exists = self.verify_removal()

            if still_exists > 0:
                print(f"{Colors.RED}⚠️  Some items could not be removed{Colors.END}")
                print()
                return 4

        # Generate report
        report = self.generate_report(dirs, packages)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.base_dir / '_config' / 'MOAI-ADK' / 'reports' / f'claude-flow-uninstall_{timestamp}.json'
        self.save_report(report, report_path)
        print()

        # Final status
        if self.dry_run:
            print(f"{Colors.BLUE}ℹ  Dry-run completed - no changes made{Colors.END}")
            print()
            return 0
        elif self.errors:
            print(f"{Colors.YELLOW}⚠️  Uninstall completed with errors{Colors.END}")
            print()
            return 1
        else:
            print(f"{Colors.GREEN}✅ Claude-Flow uninstalled successfully!{Colors.END}")
            print()
            return 0


async def agent_mode(uninstaller: ClaudeFlowUninstaller):
    """
    Claude Agent SDK mode for AI-guided uninstallation

    Args:
        uninstaller: ClaudeFlowUninstaller instance
    """
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions
    except ImportError:
        print(f"{Colors.YELLOW}⚠️  Claude Agent SDK not installed{Colors.END}")
        print("Install with: pip install claude-agent-sdk")
        print()
        print("Falling back to standalone mode...")
        return uninstaller.run()

    print()
    print(f"{Colors.BOLD}🤖 Claude Agent SDK Mode{Colors.END}")
    print("━" * 60)
    print()

    # Scan first
    dirs = uninstaller.scan_directories()
    packages = uninstaller.check_npm_packages()

    # Prepare context for Claude
    context = {
        'directories': [d['name'] for d in dirs],
        'packages': [p['name'] for p in packages],
        'total_size': uninstaller.format_size(uninstaller.total_size),
        'dry_run': uninstaller.dry_run,
        'backup': uninstaller.backup
    }

    prompt = f"""I'm planning to uninstall claude-flow. Here's what was found:

Directories to remove:
{chr(10).join('- ' + d for d in context['directories']) if context['directories'] else '- None found'}

NPM packages to uninstall:
{chr(10).join('- ' + p for p in context['packages']) if context['packages'] else '- None found'}

Total space to free: {context['total_size']}
Mode: {'Dry-run (preview only)' if context['dry_run'] else 'Full uninstall'}
Backup enabled: {'Yes' if context['backup'] else 'No'}

Please analyze this and provide:
1. Assessment of what will be removed
2. Any potential issues or warnings
3. Recommendations for proceeding safely
4. Whether this looks like a complete uninstallation

Be specific and actionable."""

    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant for claude-flow uninstallation.",
        permission_mode='default'
    )

    print("🤖 Analyzing with Claude...\n")

    async for message in query(prompt=prompt, options=options):
        if hasattr(message, 'content'):
            for block in message.content:
                if hasattr(block, 'text'):
                    print(block.text)

    print()
    print("━" * 60)
    print()

    # Ask user if they want to proceed
    if not uninstaller.dry_run:
        response = input(f"{Colors.BOLD}Proceed with uninstall based on AI analysis? (yes/no): {Colors.END}")
        print()

        if response.lower() not in ['yes', 'y']:
            print(f"{Colors.YELLOW}✗ Uninstall cancelled{Colors.END}")
            print()
            return 0

    return uninstaller.run()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Comprehensive claude-flow uninstaller",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        # Preview what would be removed
  %(prog)s --dry-run              # Same as above (explicit)
  %(prog)s --yes                  # Uninstall without confirmation
  %(prog)s --backup               # Backup before removing
  %(prog)s --agent                # AI-guided uninstallation
  %(prog)s --backup --yes         # Backup and uninstall

Exit codes:
  0 - Success or nothing to do
  1 - Error during uninstall
  4 - Cleanup verification failed
        """
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be removed (no changes)"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backups before removing directories"
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt"
    )
    parser.add_argument(
        "--agent",
        action="store_true",
        help="Use Claude Agent SDK for AI-guided uninstallation"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()

    # Default to dry-run if no action specified
    if not args.yes and not args.agent:
        args.dry_run = True

    # Create uninstaller
    uninstaller = ClaudeFlowUninstaller(
        dry_run=args.dry_run,
        backup=args.backup,
        verbose=args.verbose
    )

    # Choose mode
    if args.agent:
        import anyio
        return anyio.run(agent_mode, uninstaller)
    else:
        return uninstaller.run()


if __name__ == "__main__":
    sys.exit(main())
