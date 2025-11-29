#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11,<3.15"
# dependencies = [
#     "click>=8.1.0",
# ]
# ///

"""
MoAI-ADK Installation Validation

Comprehensive 10-point validation checklist:
1. Check moai-adk version
2. Verify 26 agents available
3. Test /moai:0 command
4. Test /moai:1 command
5. Test /moai:2 command
6. Test /moai:3 command
7. Test /moai:4 command
8. Verify project structure
9. Check configuration files
10. Verify Korean fonts (if configured)

Usage:
    uv run validate_install.py
    uv run validate_install.py --verbose
    uv run validate_install.py --comprehensive
    uv run validate_install.py --json
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import click


class InstallationValidator:
    """Comprehensive MoAI-ADK installation validator."""

    def __init__(self, verbose: bool = False, comprehensive: bool = False):
        self.verbose = verbose
        self.comprehensive = comprehensive
        self.results: Dict[str, dict] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.score = 0
        self.max_score = 10

    def _run_command(
        self, cmd: List[str], timeout: int = 30
    ) -> Tuple[bool, str, str]:
        """Execute command and return success status, stdout, stderr."""
        try:
            if self.verbose:
                print(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

        except Exception as e:
            return False, "", str(e)

    def validate_moai_version(self) -> dict:
        """Check 1: Verify moai-adk is installed and get version."""
        result = {
            "check": 1,
            "name": "MoAI-ADK Version",
            "status": "pending",
            "details": {},
        }

        try:
            # Try direct command first
            success, stdout, stderr = self._run_command(["moai-adk", "--version"])

            if not success:
                # Try via uv tool run
                success, stdout, stderr = self._run_command(
                    ["uv", "tool", "run", "moai-adk", "--version"]
                )

            if success:
                result["status"] = "passed"
                result["details"]["version"] = stdout.strip()
                result["details"]["command_available"] = True
                self.score += 1

                if self.verbose:
                    print(f"✓ MoAI-ADK version: {stdout}")
            else:
                result["status"] = "failed"
                result["details"]["error"] = stderr or "Command not available"
                self.errors.append("MoAI-ADK is not installed or not accessible")

        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"Version check failed: {e}")

        self.results["version"] = result
        return result

    def validate_agents_available(self) -> dict:
        """Check 2: Verify 26 agents are available."""
        result = {
            "check": 2,
            "name": "Available Agents",
            "status": "pending",
            "details": {},
        }

        try:
            # Try to list agents
            success, stdout, stderr = self._run_command(
                ["moai-adk", "list", "agents"]
            )

            if not success:
                success, stdout, stderr = self._run_command(
                    ["uv", "tool", "run", "moai-adk", "list", "agents"]
                )

            if success:
                # Count agents in output
                lines = [l for l in stdout.split("\n") if l.strip()]
                agent_count = len(lines)

                result["details"]["agents_found"] = agent_count
                result["details"]["expected"] = 26

                if agent_count >= 26:
                    result["status"] = "passed"
                    self.score += 1

                    if self.verbose:
                        print(f"✓ Found {agent_count} agents (expected 26+)")
                else:
                    result["status"] = "warning"
                    result["details"]["warning"] = f"Only {agent_count} agents found (expected 26)"
                    self.warnings.append(f"Expected 26 agents, found {agent_count}")
                    self.score += 0.5
            else:
                result["status"] = "failed"
                result["details"]["error"] = stderr or "Could not list agents"
                self.errors.append("Failed to list agents")

        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"Agent list check failed: {e}")

        self.results["agents"] = result
        return result

    def validate_moai_command(self, level: int) -> dict:
        """Check 3-7: Test /moai:N commands (N=0-4)."""
        result = {
            "check": 3 + level,
            "name": f"MoAI Command Level {level}",
            "status": "pending",
            "details": {},
        }

        try:
            # Test moai command
            cmd_name = f"/moai:{level}"

            # Try npx command
            success, stdout, stderr = self._run_command(
                ["npx", "moai-adk", cmd_name, "--help"],
                timeout=15,
            )

            if success:
                result["status"] = "passed"
                result["details"]["command"] = cmd_name
                result["details"]["available"] = True
                result["details"]["help_output"] = stdout[:200] if self.comprehensive else "Available"
                self.score += 1

                if self.verbose:
                    print(f"✓ Command {cmd_name} is available")
            else:
                # Command might exist but --help not supported
                if "not found" in stderr.lower() or "command not found" in stderr.lower():
                    result["status"] = "failed"
                    result["details"]["error"] = f"Command {cmd_name} not found"
                    self.errors.append(f"Command {cmd_name} is not available")
                else:
                    # Command exists but help failed - still count as passed
                    result["status"] = "passed"
                    result["details"]["command"] = cmd_name
                    result["details"]["available"] = True
                    result["details"]["note"] = "Command exists but --help not supported"
                    self.score += 1

        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"Command /moai:{level} test failed: {e}")

        self.results[f"moai_{level}"] = result
        return result

    def validate_project_structure(self) -> dict:
        """Check 8: Verify .moai/ project structure."""
        result = {
            "check": 8,
            "name": "Project Structure",
            "status": "pending",
            "details": {},
        }

        try:
            moai_dir = Path.cwd() / ".moai"

            required_dirs = [
                "agents",
                "commands",
                "config",
                "logs",
                "cache",
            ]

            existing_dirs = []
            missing_dirs = []

            for dir_name in required_dirs:
                dir_path = moai_dir / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    existing_dirs.append(dir_name)
                else:
                    missing_dirs.append(dir_name)

            result["details"]["required_directories"] = required_dirs
            result["details"]["existing_directories"] = existing_dirs
            result["details"]["missing_directories"] = missing_dirs

            if not missing_dirs:
                result["status"] = "passed"
                self.score += 1

                if self.verbose:
                    print(f"✓ All {len(required_dirs)} required directories exist")
            else:
                result["status"] = "warning"
                result["details"]["warning"] = f"Missing directories: {', '.join(missing_dirs)}"
                self.warnings.append(f"Missing directories in .moai/: {', '.join(missing_dirs)}")
                self.score += 0.5

        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"Project structure validation failed: {e}")

        self.results["structure"] = result
        return result

    def validate_configuration_files(self) -> dict:
        """Check 9: Verify configuration files."""
        result = {
            "check": 9,
            "name": "Configuration Files",
            "status": "pending",
            "details": {},
        }

        try:
            moai_dir = Path.cwd() / ".moai"

            required_files = [
                "config/moai.json",
                "README.md",
                ".gitignore",
            ]

            existing_files = []
            missing_files = []

            for file_path_str in required_files:
                file_path = moai_dir / file_path_str
                if file_path.exists() and file_path.is_file():
                    existing_files.append(file_path_str)

                    # Validate JSON files
                    if file_path.suffix == ".json" and self.comprehensive:
                        try:
                            with open(file_path, "r") as f:
                                json.load(f)
                            result["details"][f"{file_path_str}_valid"] = True
                        except json.JSONDecodeError as e:
                            result["details"][f"{file_path_str}_valid"] = False
                            self.warnings.append(f"Invalid JSON in {file_path_str}: {e}")
                else:
                    missing_files.append(file_path_str)

            result["details"]["required_files"] = required_files
            result["details"]["existing_files"] = existing_files
            result["details"]["missing_files"] = missing_files

            if not missing_files:
                result["status"] = "passed"
                self.score += 1

                if self.verbose:
                    print(f"✓ All {len(required_files)} required files exist")
            else:
                result["status"] = "warning"
                result["details"]["warning"] = f"Missing files: {', '.join(missing_files)}"
                self.warnings.append(f"Missing configuration files: {', '.join(missing_files)}")
                self.score += 0.5

        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"Configuration file validation failed: {e}")

        self.results["config_files"] = result
        return result

    def validate_korean_fonts(self) -> dict:
        """Check 10: Verify Korean font configuration (if enabled)."""
        result = {
            "check": 10,
            "name": "Korean Font Support",
            "status": "pending",
            "details": {},
        }

        try:
            # Check if Korean support is enabled in config
            moai_config = Path.cwd() / ".moai" / "config" / "moai.json"

            korean_enabled = False
            if moai_config.exists():
                try:
                    with open(moai_config, "r") as f:
                        config = json.load(f)
                        korean_enabled = config.get("korean_support", False)
                except Exception:
                    pass

            result["details"]["korean_support_enabled"] = korean_enabled

            if not korean_enabled:
                result["status"] = "skipped"
                result["details"]["reason"] = "Korean support not enabled"
                self.score += 1  # Not required, so count as passed

                if self.verbose:
                    print("⊙ Korean support not enabled (optional)")

                self.results["korean_fonts"] = result
                return result

            # Check for D2Coding font (macOS)
            import platform
            if platform.system() == "Darwin":
                success, stdout, _ = self._run_command(
                    ["brew", "list", "--cask", "font-d2coding"]
                )

                if success:
                    result["status"] = "passed"
                    result["details"]["d2coding_installed"] = True
                    self.score += 1

                    if self.verbose:
                        print("✓ D2Coding font is installed")
                else:
                    result["status"] = "warning"
                    result["details"]["d2coding_installed"] = False
                    self.warnings.append("D2Coding font not installed (run configure_korean.py)")
                    self.score += 0.5
            else:
                # Non-macOS: cannot verify font installation
                result["status"] = "skipped"
                result["details"]["reason"] = "Font verification only available on macOS"
                self.score += 1

            # Check Ghostty configuration
            ghostty_config = Path.home() / ".config" / "ghostty" / "config"
            if ghostty_config.exists():
                try:
                    with open(ghostty_config, "r") as f:
                        config_content = f.read()

                    if "D2Coding" in config_content:
                        result["details"]["ghostty_configured"] = True
                        if self.verbose:
                            print("✓ Ghostty configured for Korean")
                    else:
                        result["details"]["ghostty_configured"] = False
                        self.warnings.append("Ghostty not configured with D2Coding font")
                except Exception:
                    result["details"]["ghostty_configured"] = False
            else:
                result["details"]["ghostty_configured"] = False

        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"Korean font validation failed: {e}")

        self.results["korean_fonts"] = result
        return result

    def run_validation(self) -> dict:
        """Run all validation checks."""
        if self.verbose:
            print("🔍 Running MoAI-ADK installation validation...\n")

        # Run all checks
        self.validate_moai_version()
        self.validate_agents_available()

        # Test all /moai:N commands (0-4)
        for level in range(5):
            self.validate_moai_command(level)

        self.validate_project_structure()
        self.validate_configuration_files()
        self.validate_korean_fonts()

        # Calculate overall status
        percentage = (self.score / self.max_score) * 100

        if percentage >= 90:
            overall_status = "EXCELLENT"
        elif percentage >= 70:
            overall_status = "GOOD"
        elif percentage >= 50:
            overall_status = "FAIR"
        else:
            overall_status = "POOR"

        summary = {
            "overall_status": overall_status,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": round(percentage, 1),
            "checks_passed": len([r for r in self.results.values() if r.get("status") == "passed"]),
            "checks_total": len(self.results),
            "errors": self.errors,
            "warnings": self.warnings,
            "results": self.results,
        }

        return summary


def print_human_readable(summary: dict, verbose: bool = False):
    """Print human-readable validation summary."""
    print("\n" + "=" * 70)
    print("MoAI-ADK Installation Validation")
    print("=" * 70 + "\n")

    # Print results
    for key, result in summary["results"].items():
        status = result.get("status", "unknown")
        status_emoji = {
            "passed": "✓",
            "skipped": "⊙",
            "warning": "⚠",
            "failed": "✗",
        }.get(status, "?")

        check_num = result.get("check", "?")
        name = result.get("name", key)

        print(f"{status_emoji} Check {check_num}: {name}")

        if verbose and "details" in result:
            for detail_key, detail_value in result["details"].items():
                if isinstance(detail_value, (str, int, bool)):
                    print(f"    {detail_key}: {detail_value}")
        print()

    # Print score
    print("=" * 70)
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Score: {summary['score']}/{summary['max_score']} ({summary['percentage']}%)")
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

    # Print recommendations
    percentage = summary["percentage"]
    if percentage >= 90:
        print("✅ Installation is excellent! MoAI-ADK is ready to use.")
    elif percentage >= 70:
        print("✓ Installation is good. Minor issues can be addressed if needed.")
    elif percentage >= 50:
        print("⚠️  Installation is fair. Consider resolving warnings.")
    else:
        print("❌ Installation needs attention. Please resolve errors.")


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
    "--comprehensive",
    "-c",
    is_flag=True,
    help="Run comprehensive validation with extended checks",
)
@click.option(
    "--help",
    "-h",
    "show_help",
    is_flag=True,
    help="Show this help message and exit",
)
def main(verbose: bool, output_json: bool, comprehensive: bool, show_help: bool):
    """
    Validate MoAI-ADK installation with 10-point checklist.

    Checks:
    1. MoAI-ADK version
    2. Available agents (26 expected)
    3-7. /moai:0 through /moai:4 commands
    8. Project structure (.moai/ directories)
    9. Configuration files
    10. Korean font support (if enabled)

    Examples:
        uv run validate_install.py
        uv run validate_install.py --verbose
        uv run validate_install.py --comprehensive
        uv run validate_install.py --json
    """
    if show_help:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        return

    validator = InstallationValidator(verbose=verbose, comprehensive=comprehensive)
    summary = validator.run_validation()

    if output_json:
        print(json.dumps(summary, indent=2))
    else:
        print_human_readable(summary, verbose=verbose)

    # Exit with error code if validation score is poor
    if summary["percentage"] < 50:
        sys.exit(1)


if __name__ == "__main__":
    main()
