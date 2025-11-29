#!/usr/bin/env python3
"""
MoAI ADK Pre-Installation Check Script
======================================

Comprehensive system check before installing MoAI ADK.

Features:
- Prerequisites validation (Python, Git, Node.js, disk space, network)
- Conflict detection (claude-flow, .dot folders, existing MoAI)
- Auto-fix mode for automated remediation
- CI-friendly JSON output
- AI agent guidance
- Color-coded reports
- Smart exit codes

Usage:
    python pre-install-check.py                    # Interactive mode
    python pre-install-check.py --auto-fix         # Auto-fix conflicts
    python pre-install-check.py --ci               # CI mode (JSON output)
    python pre-install-check.py --agent            # AI guidance mode
    python pre-install-check.py --verbose          # Detailed output

Exit Codes:
    0 - System ready for installation
    1 - General error
    2 - Prerequisites failed
    3 - Conflicts detected (need manual/auto resolution)
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import re


# ============================================================================
# ANSI Color Codes
# ============================================================================

class Colors:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"

    # Bright colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"

    @staticmethod
    def disable():
        """Disable colors (for CI mode)"""
        for attr in dir(Colors):
            if not attr.startswith('_') and attr.isupper() and attr != 'RESET':
                setattr(Colors, attr, '')
        Colors.RESET = ''


# ============================================================================
# Status Enums
# ============================================================================

class CheckStatus(Enum):
    """Status of individual checks"""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIP = "SKIP"
    FIXED = "FIXED"

    def icon(self) -> str:
        """Get icon for status"""
        icons = {
            CheckStatus.PASS: f"{Colors.GREEN}✓{Colors.RESET}",
            CheckStatus.FAIL: f"{Colors.RED}✗{Colors.RESET}",
            CheckStatus.WARNING: f"{Colors.YELLOW}⚠{Colors.RESET}",
            CheckStatus.SKIP: f"{Colors.DIM}○{Colors.RESET}",
            CheckStatus.FIXED: f"{Colors.CYAN}🔧{Colors.RESET}",
        }
        return icons.get(self, "?")


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class CheckResult:
    """Result of a single check"""
    name: str
    status: CheckStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    can_auto_fix: bool = False
    fix_command: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'status': self.status.value,
            'message': self.message,
            'details': self.details,
            'can_auto_fix': self.can_auto_fix,
            'fix_command': self.fix_command
        }


@dataclass
class SystemReport:
    """Complete system check report"""
    prerequisites: List[CheckResult] = field(default_factory=list)
    conflicts: List[CheckResult] = field(default_factory=list)
    disk_space: Optional[CheckResult] = None
    network: Optional[CheckResult] = None
    overall_status: CheckStatus = CheckStatus.PASS
    ready_for_install: bool = False
    timestamp: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'prerequisites': [r.to_dict() for r in self.prerequisites],
            'conflicts': [r.to_dict() for r in self.conflicts],
            'disk_space': self.disk_space.to_dict() if self.disk_space else None,
            'network': self.network.to_dict() if self.network else None,
            'overall_status': self.overall_status.value,
            'ready_for_install': self.ready_for_install,
            'timestamp': self.timestamp
        }


# ============================================================================
# Pre-Installation Checker
# ============================================================================

class PreInstallChecker:
    """Main pre-installation checker class"""

    MIN_PYTHON_VERSION = (3, 11)
    MAX_PYTHON_VERSION = (3, 14)
    MIN_DISK_SPACE_MB = 500
    GITHUB_API_URL = "https://api.github.com"

    def __init__(self, verbose: bool = False, ci_mode: bool = False, agent_mode: bool = False):
        self.verbose = verbose
        self.ci_mode = ci_mode
        self.agent_mode = agent_mode
        self.report = SystemReport()

        if ci_mode:
            Colors.disable()

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled"""
        if self.verbose or level == "ERROR":
            prefix = {
                "INFO": f"{Colors.BLUE}[INFO]{Colors.RESET}",
                "SUCCESS": f"{Colors.GREEN}[SUCCESS]{Colors.RESET}",
                "WARNING": f"{Colors.YELLOW}[WARNING]{Colors.RESET}",
                "ERROR": f"{Colors.RED}[ERROR]{Colors.RESET}",
            }
            print(f"{prefix.get(level, '[INFO]')} {message}")

    def run_command(self, cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
        """Run shell command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except FileNotFoundError:
            return 127, "", f"Command not found: {cmd[0]}"
        except Exception as e:
            return 1, "", str(e)

    def parse_version(self, version_string: str) -> Optional[Tuple[int, ...]]:
        """Parse version string into tuple of integers"""
        match = re.search(r'(\d+)\.(\d+)(?:\.(\d+))?', version_string)
        if match:
            parts = [int(p) for p in match.groups() if p is not None]
            return tuple(parts)
        return None

    # ========================================================================
    # Prerequisite Checks
    # ========================================================================

    def check_python_version(self) -> CheckResult:
        """Check Python version (3.11-3.14)"""
        current_version = sys.version_info[:2]
        version_str = f"{current_version[0]}.{current_version[1]}"

        if self.MIN_PYTHON_VERSION <= current_version <= self.MAX_PYTHON_VERSION:
            return CheckResult(
                name="Python Version",
                status=CheckStatus.PASS,
                message=f"Python {version_str} detected",
                details={
                    'version': version_str,
                    'required': f"{self.MIN_PYTHON_VERSION[0]}.{self.MIN_PYTHON_VERSION[1]}-{self.MAX_PYTHON_VERSION[0]}.{self.MAX_PYTHON_VERSION[1]}"
                }
            )
        else:
            return CheckResult(
                name="Python Version",
                status=CheckStatus.FAIL,
                message=f"Python {version_str} not supported (need 3.11-3.14)",
                details={
                    'version': version_str,
                    'required': f"{self.MIN_PYTHON_VERSION[0]}.{self.MIN_PYTHON_VERSION[1]}-{self.MAX_PYTHON_VERSION[0]}.{self.MAX_PYTHON_VERSION[1]}"
                },
                can_auto_fix=False,
                fix_command="Please install Python 3.11-3.14 from python.org"
            )

    def check_git(self) -> CheckResult:
        """Check Git availability"""
        code, stdout, stderr = self.run_command(['git', '--version'])

        if code == 0:
            version = self.parse_version(stdout)
            return CheckResult(
                name="Git",
                status=CheckStatus.PASS,
                message=f"Git installed: {stdout}",
                details={'version': stdout, 'path': shutil.which('git')}
            )
        else:
            return CheckResult(
                name="Git",
                status=CheckStatus.FAIL,
                message="Git not found",
                details={'error': stderr or 'git command not available'},
                can_auto_fix=False,
                fix_command="Install Git from https://git-scm.com"
            )

    def check_nodejs(self) -> CheckResult:
        """Check Node.js/npx availability"""
        node_code, node_out, node_err = self.run_command(['node', '--version'])
        npx_code, npx_out, npx_err = self.run_command(['npx', '--version'])

        if node_code == 0 and npx_code == 0:
            return CheckResult(
                name="Node.js/npx",
                status=CheckStatus.PASS,
                message=f"Node.js {node_out}, npx {npx_out}",
                details={
                    'node_version': node_out,
                    'npx_version': npx_out,
                    'node_path': shutil.which('node'),
                    'npx_path': shutil.which('npx')
                }
            )
        elif node_code == 0:
            return CheckResult(
                name="Node.js/npx",
                status=CheckStatus.WARNING,
                message="Node.js found but npx missing",
                details={'node_version': node_out, 'error': npx_err},
                can_auto_fix=False,
                fix_command="Install npx: npm install -g npx"
            )
        else:
            return CheckResult(
                name="Node.js/npx",
                status=CheckStatus.FAIL,
                message="Node.js/npx not found",
                details={'error': node_err or 'node command not available'},
                can_auto_fix=False,
                fix_command="Install Node.js from https://nodejs.org"
            )

    def check_disk_space(self) -> CheckResult:
        """Check available disk space"""
        try:
            stat = shutil.disk_usage(os.getcwd())
            free_mb = stat.free / (1024 * 1024)
            total_mb = stat.total / (1024 * 1024)
            used_mb = stat.used / (1024 * 1024)

            if free_mb >= self.MIN_DISK_SPACE_MB:
                return CheckResult(
                    name="Disk Space",
                    status=CheckStatus.PASS,
                    message=f"{free_mb:.0f} MB available (need {self.MIN_DISK_SPACE_MB} MB)",
                    details={
                        'free_mb': round(free_mb, 2),
                        'total_mb': round(total_mb, 2),
                        'used_mb': round(used_mb, 2),
                        'required_mb': self.MIN_DISK_SPACE_MB
                    }
                )
            else:
                return CheckResult(
                    name="Disk Space",
                    status=CheckStatus.FAIL,
                    message=f"Only {free_mb:.0f} MB available (need {self.MIN_DISK_SPACE_MB} MB)",
                    details={
                        'free_mb': round(free_mb, 2),
                        'total_mb': round(total_mb, 2),
                        'required_mb': self.MIN_DISK_SPACE_MB
                    },
                    can_auto_fix=False,
                    fix_command="Free up disk space before installation"
                )
        except Exception as e:
            return CheckResult(
                name="Disk Space",
                status=CheckStatus.WARNING,
                message=f"Could not check disk space: {e}",
                details={'error': str(e)}
            )

    def check_network(self) -> CheckResult:
        """Check network connectivity to GitHub API"""
        try:
            req = urllib.request.Request(
                self.GITHUB_API_URL,
                headers={'User-Agent': 'MoAI-ADK-PreInstallCheck'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return CheckResult(
                        name="Network Connectivity",
                        status=CheckStatus.PASS,
                        message="GitHub API accessible",
                        details={
                            'url': self.GITHUB_API_URL,
                            'status_code': response.status
                        }
                    )
                else:
                    return CheckResult(
                        name="Network Connectivity",
                        status=CheckStatus.WARNING,
                        message=f"GitHub API returned status {response.status}",
                        details={
                            'url': self.GITHUB_API_URL,
                            'status_code': response.status
                        }
                    )
        except urllib.error.URLError as e:
            return CheckResult(
                name="Network Connectivity",
                status=CheckStatus.FAIL,
                message=f"Cannot reach GitHub API: {e.reason}",
                details={'url': self.GITHUB_API_URL, 'error': str(e)},
                can_auto_fix=False,
                fix_command="Check internet connection and firewall settings"
            )
        except Exception as e:
            return CheckResult(
                name="Network Connectivity",
                status=CheckStatus.FAIL,
                message=f"Network check failed: {e}",
                details={'error': str(e)}
            )

    # ========================================================================
    # Conflict Detection
    # ========================================================================

    def check_claude_flow(self) -> CheckResult:
        """Check for claude-flow installation"""
        code, stdout, stderr = self.run_command(['npx', 'claude-flow', '--version'])

        if code == 0:
            return CheckResult(
                name="claude-flow Installation",
                status=CheckStatus.WARNING,
                message=f"claude-flow detected: {stdout}",
                details={'version': stdout, 'conflict': True},
                can_auto_fix=True,
                fix_command="python _config/MOAI-ADK/scripts/uninstall-claude-flow.py"
            )
        else:
            return CheckResult(
                name="claude-flow Installation",
                status=CheckStatus.PASS,
                message="No claude-flow installation detected",
                details={'conflict': False}
            )

    def check_dot_folders(self) -> CheckResult:
        """Check for conflicting .dot folders"""
        home = Path.home()
        conflicting_folders = []

        dot_folders_to_check = [
            '.claude-flow',
            '.flow-nexus',
            '.ruv-swarm',
            '.moai-adk-old'
        ]

        for folder in dot_folders_to_check:
            folder_path = home / folder
            if folder_path.exists():
                # Get folder size
                size = sum(f.stat().st_size for f in folder_path.rglob('*') if f.is_file())
                conflicting_folders.append({
                    'path': str(folder_path),
                    'size_mb': round(size / (1024 * 1024), 2)
                })

        if conflicting_folders:
            total_size = sum(f['size_mb'] for f in conflicting_folders)
            return CheckResult(
                name="Conflicting .dot Folders",
                status=CheckStatus.WARNING,
                message=f"Found {len(conflicting_folders)} conflicting folder(s) ({total_size:.2f} MB)",
                details={
                    'folders': conflicting_folders,
                    'count': len(conflicting_folders),
                    'total_size_mb': total_size
                },
                can_auto_fix=True,
                fix_command="python _config/MOAI-ADK/scripts/clean-dot-folders.py"
            )
        else:
            return CheckResult(
                name="Conflicting .dot Folders",
                status=CheckStatus.PASS,
                message="No conflicting .dot folders found",
                details={'folders': [], 'count': 0}
            )

    def check_moai_installation(self) -> CheckResult:
        """Check if MoAI ADK is already installed"""
        moai_indicators = [
            Path.home() / '.moai-adk',
            Path.cwd() / 'moai-adk.json',
            Path.cwd() / '_config' / 'MOAI-ADK',
        ]

        found = []
        for path in moai_indicators:
            if path.exists():
                found.append(str(path))

        if found:
            return CheckResult(
                name="Existing MoAI Installation",
                status=CheckStatus.WARNING,
                message=f"MoAI ADK may already be installed ({len(found)} indicator(s))",
                details={'paths': found, 'count': len(found)},
                can_auto_fix=False,
                fix_command="Manually review and remove existing installation if needed"
            )
        else:
            return CheckResult(
                name="Existing MoAI Installation",
                status=CheckStatus.PASS,
                message="No existing MoAI installation detected",
                details={'paths': [], 'count': 0}
            )

    # ========================================================================
    # Auto-Fix
    # ========================================================================

    def auto_fix_conflicts(self) -> List[CheckResult]:
        """Auto-fix detected conflicts"""
        fixed_results = []
        scripts_dir = Path(__file__).parent

        self.log("Starting auto-fix process...", "INFO")

        # Fix claude-flow
        claude_flow_check = self.check_claude_flow()
        if claude_flow_check.status == CheckStatus.WARNING and claude_flow_check.can_auto_fix:
            self.log("Uninstalling claude-flow...", "INFO")
            script_path = scripts_dir / "uninstall-claude-flow.py"
            if script_path.exists():
                code, stdout, stderr = self.run_command([sys.executable, str(script_path)])
                if code == 0:
                    fixed_results.append(CheckResult(
                        name="claude-flow Uninstall",
                        status=CheckStatus.FIXED,
                        message="Successfully uninstalled claude-flow",
                        details={'output': stdout}
                    ))
                else:
                    fixed_results.append(CheckResult(
                        name="claude-flow Uninstall",
                        status=CheckStatus.FAIL,
                        message=f"Failed to uninstall claude-flow: {stderr}",
                        details={'error': stderr}
                    ))
            else:
                self.log(f"Uninstall script not found: {script_path}", "WARNING")

        # Fix .dot folders
        dot_folders_check = self.check_dot_folders()
        if dot_folders_check.status == CheckStatus.WARNING and dot_folders_check.can_auto_fix:
            self.log("Cleaning .dot folders...", "INFO")
            script_path = scripts_dir / "clean-dot-folders.py"
            if script_path.exists():
                code, stdout, stderr = self.run_command([sys.executable, str(script_path), '--auto'])
                if code == 0:
                    fixed_results.append(CheckResult(
                        name=".dot Folders Cleanup",
                        status=CheckStatus.FIXED,
                        message="Successfully cleaned .dot folders",
                        details={'output': stdout}
                    ))
                else:
                    fixed_results.append(CheckResult(
                        name=".dot Folders Cleanup",
                        status=CheckStatus.FAIL,
                        message=f"Failed to clean .dot folders: {stderr}",
                        details={'error': stderr}
                    ))
            else:
                self.log(f"Cleanup script not found: {script_path}", "WARNING")

        return fixed_results

    # ========================================================================
    # Main Check Orchestration
    # ========================================================================

    def run_all_checks(self) -> SystemReport:
        """Run all prerequisite and conflict checks"""
        from datetime import datetime

        self.log("Starting pre-installation checks...", "INFO")

        # Prerequisites
        self.report.prerequisites = [
            self.check_python_version(),
            self.check_git(),
            self.check_nodejs(),
        ]

        # Disk and Network
        self.report.disk_space = self.check_disk_space()
        self.report.network = self.check_network()

        # Conflicts
        self.report.conflicts = [
            self.check_claude_flow(),
            self.check_dot_folders(),
            self.check_moai_installation(),
        ]

        # Determine overall status
        has_failures = any(r.status == CheckStatus.FAIL for r in self.report.prerequisites)
        has_failures |= self.report.disk_space.status == CheckStatus.FAIL if self.report.disk_space else False
        has_failures |= self.report.network.status == CheckStatus.FAIL if self.report.network else False

        has_conflicts = any(r.status == CheckStatus.WARNING for r in self.report.conflicts)

        if has_failures:
            self.report.overall_status = CheckStatus.FAIL
            self.report.ready_for_install = False
        elif has_conflicts:
            self.report.overall_status = CheckStatus.WARNING
            self.report.ready_for_install = False
        else:
            self.report.overall_status = CheckStatus.PASS
            self.report.ready_for_install = True

        self.report.timestamp = datetime.now().isoformat()

        return self.report

    # ========================================================================
    # Report Generation
    # ========================================================================

    def print_report(self):
        """Print color-coded report to console"""
        print()
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}MoAI ADK Pre-Installation Check Report{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
        print()

        # Prerequisites
        print(f"{Colors.BOLD}Prerequisites:{Colors.RESET}")
        for result in self.report.prerequisites:
            print(f"  {result.status.icon()} {result.name}: {result.message}")
        print()

        # Disk Space
        if self.report.disk_space:
            print(f"{Colors.BOLD}Disk Space:{Colors.RESET}")
            print(f"  {self.report.disk_space.status.icon()} {self.report.disk_space.message}")
            print()

        # Network
        if self.report.network:
            print(f"{Colors.BOLD}Network Connectivity:{Colors.RESET}")
            print(f"  {self.report.network.status.icon()} {self.report.network.message}")
            print()

        # Conflicts
        print(f"{Colors.BOLD}Conflict Detection:{Colors.RESET}")
        for result in self.report.conflicts:
            print(f"  {result.status.icon()} {result.name}: {result.message}")
            if result.can_auto_fix and result.fix_command:
                print(f"    {Colors.DIM}Fix: {result.fix_command}{Colors.RESET}")
        print()

        # Overall Status
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
        if self.report.overall_status == CheckStatus.PASS:
            status_msg = f"{Colors.BOLD}{Colors.GREEN}✓ READY FOR INSTALLATION{Colors.RESET}"
        elif self.report.overall_status == CheckStatus.WARNING:
            status_msg = f"{Colors.BOLD}{Colors.YELLOW}⚠ CONFLICTS DETECTED - FIX REQUIRED{Colors.RESET}"
        else:
            status_msg = f"{Colors.BOLD}{Colors.RED}✗ PREREQUISITES FAILED{Colors.RESET}"

        print(f"Overall Status: {status_msg}")
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
        print()

        # AI Agent Guidance
        if self.agent_mode:
            self.print_ai_guidance()

    def print_ai_guidance(self):
        """Print AI agent guidance based on check results"""
        print(f"{Colors.BOLD}{Colors.MAGENTA}🤖 AI Agent Guidance:{Colors.RESET}")
        print()

        if self.report.ready_for_install:
            print(f"{Colors.GREEN}Your system is ready for MoAI ADK installation!{Colors.RESET}")
            print()
            print("Next steps:")
            print("  1. Run the MoAI ADK installer")
            print("  2. Follow the setup wizard")
            print("  3. Configure your AI agents")
        else:
            print(f"{Colors.YELLOW}Your system needs attention before installation:{Colors.RESET}")
            print()

            # Prerequisites issues
            failed_prereqs = [r for r in self.report.prerequisites if r.status == CheckStatus.FAIL]
            if failed_prereqs:
                print(f"{Colors.RED}Critical Issues:{Colors.RESET}")
                for result in failed_prereqs:
                    print(f"  • {result.name}: {result.message}")
                    if result.fix_command:
                        print(f"    → {result.fix_command}")
                print()

            # Conflicts
            conflicts = [r for r in self.report.conflicts if r.status == CheckStatus.WARNING]
            if conflicts:
                print(f"{Colors.YELLOW}Conflicts to Resolve:{Colors.RESET}")
                for result in conflicts:
                    print(f"  • {result.name}: {result.message}")
                    if result.can_auto_fix:
                        print(f"    → Run with --auto-fix to resolve automatically")
                    elif result.fix_command:
                        print(f"    → {result.fix_command}")
                print()

            print(f"{Colors.CYAN}Recommended Action:{Colors.RESET}")
            if any(r.can_auto_fix for r in conflicts):
                print(f"  Run: {Colors.BOLD}python pre-install-check.py --auto-fix{Colors.RESET}")
            else:
                print("  Resolve the issues above manually, then re-run this check")

        print()

    def print_json_report(self):
        """Print JSON report for CI mode"""
        print(json.dumps(self.report.to_dict(), indent=2))

    # ========================================================================
    # Exit Code Determination
    # ========================================================================

    def get_exit_code(self) -> int:
        """Determine appropriate exit code"""
        if self.report.overall_status == CheckStatus.PASS:
            return 0
        elif self.report.overall_status == CheckStatus.WARNING:
            return 3  # Conflicts detected
        else:
            return 2  # Prerequisites failed


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MoAI ADK Pre-Installation Check",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pre-install-check.py                    # Interactive check
  python pre-install-check.py --auto-fix         # Auto-fix conflicts
  python pre-install-check.py --ci               # CI mode (JSON output)
  python pre-install-check.py --agent            # AI guidance
  python pre-install-check.py --verbose          # Detailed output

Exit Codes:
  0 - Ready for installation
  1 - General error
  2 - Prerequisites failed
  3 - Conflicts detected
        """
    )

    parser.add_argument(
        '--auto-fix',
        action='store_true',
        help='Automatically fix detected conflicts'
    )

    parser.add_argument(
        '--ci',
        action='store_true',
        help='CI mode: non-interactive with JSON output'
    )

    parser.add_argument(
        '--agent',
        action='store_true',
        help='Enable AI agent guidance'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='MoAI ADK Pre-Install Check v1.0.0'
    )

    args = parser.parse_args()

    try:
        # Create checker
        checker = PreInstallChecker(
            verbose=args.verbose,
            ci_mode=args.ci,
            agent_mode=args.agent
        )

        # Run checks
        report = checker.run_all_checks()

        # Auto-fix if requested
        if args.auto_fix and report.overall_status == CheckStatus.WARNING:
            fixed = checker.auto_fix_conflicts()
            if fixed:
                # Re-run checks after fixes
                checker.log("Re-running checks after auto-fix...", "INFO")
                report = checker.run_all_checks()

        # Print report
        if args.ci:
            checker.print_json_report()
        else:
            checker.print_report()

        # Exit with appropriate code
        exit_code = checker.get_exit_code()
        sys.exit(exit_code)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Check interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.RESET}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
