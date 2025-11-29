#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11,<3.15"
# dependencies = [
#     "click>=8.1.0",
# ]
# ///

"""
MoAI-ADK System Requirements Checker

Validates system requirements for MoAI-ADK installation:
- Python 3.11-3.14
- uv package manager
- git version control
- npx (Node.js)
- Disk space (2GB minimum)
- Terminal (Ghostty recommended)

Usage:
    uv run check_system.py
    uv run check_system.py --verbose
    uv run check_system.py --json
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click


class SystemChecker:
    """System requirements validation for MoAI-ADK."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: Dict[str, dict] = {}
        self.warnings: List[str] = []
        self.errors: List[str] = []

    def _run_command(
        self, cmd: List[str], capture_output: bool = True
    ) -> Tuple[bool, str]:
        """Execute command and return success status and output."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=10,
            )
            return result.returncode == 0, result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return False, str(e)

    def check_python_version(self) -> dict:
        """Check Python version is between 3.11 and 3.14."""
        version_info = sys.version_info
        version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"

        is_valid = (3, 11) <= (version_info.major, version_info.minor) < (3, 15)

        result = {
            "name": "Python Version",
            "required": "3.11-3.14",
            "found": version_str,
            "valid": is_valid,
            "details": {
                "major": version_info.major,
                "minor": version_info.minor,
                "micro": version_info.micro,
                "full_version": sys.version,
            },
        }

        if not is_valid:
            self.errors.append(
                f"Python {version_str} is not supported. "
                "Please install Python 3.11, 3.12, 3.13, or 3.14"
            )
        elif self.verbose:
            print(f"✓ Python {version_str} detected")

        self.results["python"] = result
        return result

    def check_uv_installed(self) -> dict:
        """Check if uv package manager is installed."""
        uv_path = shutil.which("uv")
        is_installed = uv_path is not None
        version = ""

        if is_installed:
            success, output = self._run_command(["uv", "--version"])
            if success:
                # Extract version from "uv 0.x.x" format
                version = output.replace("uv ", "").strip()

        result = {
            "name": "UV Package Manager",
            "required": "latest",
            "found": version if is_installed else "Not installed",
            "valid": is_installed,
            "details": {
                "path": uv_path,
                "version": version,
                "install_command": "curl -LsSf https://astral.sh/uv/install.sh | sh",
            },
        }

        if not is_installed:
            self.warnings.append(
                "uv is not installed. It will be installed automatically during setup."
            )
        elif self.verbose:
            print(f"✓ uv {version} detected at {uv_path}")

        self.results["uv"] = result
        return result

    def check_git_installed(self) -> dict:
        """Check if git is installed."""
        git_path = shutil.which("git")
        is_installed = git_path is not None
        version = ""

        if is_installed:
            success, output = self._run_command(["git", "--version"])
            if success:
                # Extract version from "git version 2.x.x" format
                version = output.replace("git version ", "").strip()

        result = {
            "name": "Git",
            "required": "any",
            "found": version if is_installed else "Not installed",
            "valid": is_installed,
            "details": {
                "path": git_path,
                "version": version,
                "install_command": "brew install git" if platform.system() == "Darwin" else "apt-get install git",
            },
        }

        if not is_installed:
            self.errors.append(
                "git is required but not installed. "
                "Install with: brew install git (macOS) or apt-get install git (Linux)"
            )
        elif self.verbose:
            print(f"✓ git {version} detected at {git_path}")

        self.results["git"] = result
        return result

    def check_npx_installed(self) -> dict:
        """Check if npx (Node.js) is installed."""
        npx_path = shutil.which("npx")
        is_installed = npx_path is not None
        node_version = ""
        npm_version = ""

        if is_installed:
            success, output = self._run_command(["node", "--version"])
            if success:
                node_version = output.strip()

            success, output = self._run_command(["npm", "--version"])
            if success:
                npm_version = output.strip()

        result = {
            "name": "NPX (Node.js)",
            "required": "any",
            "found": f"Node {node_version}, npm {npm_version}" if is_installed else "Not installed",
            "valid": is_installed,
            "details": {
                "npx_path": npx_path,
                "node_version": node_version,
                "npm_version": npm_version,
                "install_command": "brew install node" if platform.system() == "Darwin" else "apt-get install nodejs npm",
            },
        }

        if not is_installed:
            self.errors.append(
                "npx is required for MoAI-ADK commands. "
                "Install Node.js with: brew install node (macOS) or apt-get install nodejs npm (Linux)"
            )
        elif self.verbose:
            print(f"✓ npx detected with Node {node_version}")

        self.results["npx"] = result
        return result

    def check_disk_space(self, min_gb: float = 2.0) -> dict:
        """Check available disk space (minimum 2GB recommended)."""
        try:
            stat = os.statvfs(Path.home())
            available_bytes = stat.f_bavail * stat.f_frsize
            available_gb = available_bytes / (1024**3)
            is_sufficient = available_gb >= min_gb

            result = {
                "name": "Disk Space",
                "required": f"{min_gb}GB",
                "found": f"{available_gb:.2f}GB",
                "valid": is_sufficient,
                "details": {
                    "available_bytes": available_bytes,
                    "available_gb": round(available_gb, 2),
                    "minimum_gb": min_gb,
                },
            }

            if not is_sufficient:
                self.warnings.append(
                    f"Low disk space: {available_gb:.2f}GB available. "
                    f"Recommended minimum: {min_gb}GB"
                )
            elif self.verbose:
                print(f"✓ {available_gb:.2f}GB disk space available")

        except Exception as e:
            result = {
                "name": "Disk Space",
                "required": f"{min_gb}GB",
                "found": "Unable to check",
                "valid": False,
                "details": {"error": str(e)},
            }
            self.warnings.append(f"Could not check disk space: {e}")

        self.results["disk_space"] = result
        return result

    def check_terminal(self) -> dict:
        """Check terminal emulator (Ghostty recommended for Korean support)."""
        term = os.environ.get("TERM_PROGRAM", "")
        term_version = os.environ.get("TERM_PROGRAM_VERSION", "")
        is_ghostty = "ghostty" in term.lower()

        # Check if Ghostty is installed
        ghostty_path = shutil.which("ghostty")
        ghostty_installed = ghostty_path is not None

        result = {
            "name": "Terminal",
            "required": "Ghostty (recommended)",
            "found": term if term else "Unknown",
            "valid": True,  # Any terminal works, but Ghostty is recommended
            "details": {
                "current_terminal": term,
                "version": term_version,
                "is_ghostty": is_ghostty,
                "ghostty_installed": ghostty_installed,
                "ghostty_path": ghostty_path,
                "install_command": "brew install ghostty" if platform.system() == "Darwin" else "See https://ghostty.org",
            },
        }

        if not is_ghostty and not ghostty_installed:
            self.warnings.append(
                "Ghostty terminal is recommended for optimal Korean font rendering. "
                "Install with: brew install ghostty (macOS)"
            )
        elif is_ghostty and self.verbose:
            print(f"✓ Ghostty terminal detected ({term_version})")
        elif ghostty_installed and self.verbose:
            print(f"✓ Ghostty installed at {ghostty_path} (not currently active)")

        self.results["terminal"] = result
        return result

    def check_platform(self) -> dict:
        """Check operating system platform."""
        system = platform.system()
        release = platform.release()
        machine = platform.machine()

        supported_platforms = ["Darwin", "Linux"]
        is_supported = system in supported_platforms

        result = {
            "name": "Operating System",
            "required": "macOS or Linux",
            "found": f"{system} {release} ({machine})",
            "valid": is_supported,
            "details": {
                "system": system,
                "release": release,
                "machine": machine,
                "platform": platform.platform(),
            },
        }

        if not is_supported:
            self.warnings.append(
                f"Platform {system} may not be fully supported. "
                "MoAI-ADK is optimized for macOS and Linux."
            )
        elif self.verbose:
            print(f"✓ {system} {release} detected")

        self.results["platform"] = result
        return result

    def run_all_checks(self) -> dict:
        """Run all system checks and return results."""
        if self.verbose:
            print("🔍 Checking system requirements for MoAI-ADK...\n")

        self.check_platform()
        self.check_python_version()
        self.check_uv_installed()
        self.check_git_installed()
        self.check_npx_installed()
        self.check_disk_space()
        self.check_terminal()

        # Calculate overall status
        all_valid = all(r.get("valid", False) for r in self.results.values())
        critical_errors = len(self.errors) == 0

        summary = {
            "overall_status": "READY" if (all_valid and critical_errors) else "NEEDS_ATTENTION",
            "checks_passed": sum(1 for r in self.results.values() if r.get("valid", False)),
            "checks_total": len(self.results),
            "errors": self.errors,
            "warnings": self.warnings,
            "results": self.results,
        }

        return summary


def print_human_readable(summary: dict, verbose: bool = False):
    """Print human-readable summary of system checks."""
    print("\n" + "=" * 70)
    print("MoAI-ADK System Requirements Check")
    print("=" * 70 + "\n")

    # Print results
    for key, result in summary["results"].items():
        status = "✓" if result["valid"] else "✗"
        color = "green" if result["valid"] else "red"

        print(f"{status} {result['name']}")
        print(f"  Required: {result['required']}")
        print(f"  Found: {result['found']}")

        if verbose and "details" in result:
            print(f"  Details: {json.dumps(result['details'], indent=4)}")
        print()

    # Print summary
    print("=" * 70)
    print(f"Status: {summary['overall_status']}")
    print(f"Checks Passed: {summary['checks_passed']}/{summary['checks_total']}")
    print("=" * 70 + "\n")

    # Print errors
    if summary["errors"]:
        print("❌ ERRORS:")
        for error in summary["errors"]:
            print(f"  • {error}")
        print()

    # Print warnings
    if summary["warnings"]:
        print("⚠️  WARNINGS:")
        for warning in summary["warnings"]:
            print(f"  • {warning}")
        print()

    # Print next steps
    if summary["overall_status"] == "READY":
        print("✅ System is ready for MoAI-ADK installation!")
        print("\nNext steps:")
        print("  1. Run: uv run install_moai.py")
        print("  2. (Optional) Run: uv run configure_korean.py")
        print("  3. Validate: uv run validate_install.py")
    else:
        print("⚠️  Please resolve errors before installing MoAI-ADK")


@click.command()
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output with detailed information",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results in JSON format",
)
@click.option(
    "--help",
    "-h",
    "show_help",
    is_flag=True,
    help="Show this help message and exit",
)
def main(verbose: bool, output_json: bool, show_help: bool):
    """
    Check system requirements for MoAI-ADK installation.

    Validates:
    - Python 3.11-3.14
    - uv package manager
    - git version control
    - npx (Node.js)
    - Disk space (2GB minimum)
    - Terminal (Ghostty recommended)

    Examples:
        uv run check_system.py
        uv run check_system.py --verbose
        uv run check_system.py --json
    """
    if show_help:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        return

    checker = SystemChecker(verbose=verbose)
    summary = checker.run_all_checks()

    if output_json:
        print(json.dumps(summary, indent=2))
    else:
        print_human_readable(summary, verbose=verbose)

    # Exit with error code if system is not ready
    if summary["overall_status"] != "READY" and len(summary["errors"]) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
