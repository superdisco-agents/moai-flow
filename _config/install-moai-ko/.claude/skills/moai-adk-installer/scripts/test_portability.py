#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11,<3.15"
# dependencies = [
#     "click>=8.1.0",
# ]
# ///

"""
MoAI-ADK Portability Testing

Tests portability and isolation:
1. Virtual environment isolation
2. Cross-platform compatibility
3. Korean font availability across systems
4. UV tool installation portability
5. Configuration file portability
6. Dependency resolution

Usage:
    uv run test_portability.py
    uv run test_portability.py --verbose
    uv run test_portability.py --json
"""

import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

import click


class PortabilityTester:
    """MoAI-ADK portability and isolation tester."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: Dict[str, dict] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.platform_info = {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
        }

    def _run_command(
        self, cmd: List[str], timeout: int = 30, cwd: str = None
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
                cwd=cwd,
            )

            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

        except Exception as e:
            return False, "", str(e)

    def test_virtual_environment_isolation(self) -> dict:
        """Test 1: Virtual environment isolation."""
        result = {
            "test": 1,
            "name": "Virtual Environment Isolation",
            "status": "pending",
            "details": {},
        }

        try:
            if self.verbose:
                print("[yellow]Testing virtual environment isolation...[/yellow]")

            # Check if running in virtual environment
            in_venv = sys.prefix != sys.base_prefix
            result["details"]["in_virtual_env"] = in_venv
            result["details"]["sys_prefix"] = sys.prefix
            result["details"]["base_prefix"] = sys.base_prefix

            # Check uv tool isolation
            success, stdout, _ = self._run_command(["uv", "tool", "list"])

            if success:
                result["details"]["uv_tools_isolated"] = True
                result["details"]["installed_tools"] = stdout.split("\n")[:5]  # First 5 tools

                # Check if moai-adk is in uv tools (isolated)
                moai_in_tools = "moai-adk" in stdout
                result["details"]["moai_adk_isolated"] = moai_in_tools

                if moai_in_tools:
                    result["status"] = "passed"

                    if self.verbose:
                        print("✓ moai-adk is properly isolated in uv tools")
                else:
                    result["status"] = "warning"
                    result["details"]["warning"] = "moai-adk not found in uv tools"
                    self.warnings.append(
                        "moai-adk may not be isolated. Install with: uv tool install moai-adk"
                    )
            else:
                result["status"] = "failed"
                result["details"]["error"] = "Could not list uv tools"
                self.errors.append("Failed to verify tool isolation")

        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"Virtual environment isolation test failed: {e}")

        self.results["venv_isolation"] = result
        return result

    def test_cross_platform_compatibility(self) -> dict:
        """Test 2: Cross-platform compatibility."""
        result = {
            "test": 2,
            "name": "Cross-Platform Compatibility",
            "status": "pending",
            "details": self.platform_info.copy(),
        }

        try:
            if self.verbose:
                print("[yellow]Testing cross-platform compatibility...[/yellow]")

            # Check supported platforms
            supported_platforms = ["Darwin", "Linux"]
            is_supported = self.platform_info["system"] in supported_platforms

            result["details"]["supported_platform"] = is_supported
            result["details"]["supported_platforms"] = supported_platforms

            # Check Python version compatibility
            version_parts = self.platform_info["python_version"].split(".")
            major = int(version_parts[0])
            minor = int(version_parts[1])

            python_compatible = (3, 11) <= (major, minor) < (3, 15)
            result["details"]["python_compatible"] = python_compatible

            # Check shell compatibility
            shell = os.environ.get("SHELL", "")
            result["details"]["shell"] = shell
            result["details"]["shell_compatible"] = any(
                s in shell for s in ["bash", "zsh", "fish"]
            )

            # Check path separators (Windows vs Unix)
            result["details"]["path_separator"] = os.sep
            result["details"]["pathsep"] = os.pathsep

            # Overall compatibility
            all_compatible = (
                is_supported and
                python_compatible and
                result["details"]["shell_compatible"]
            )

            if all_compatible:
                result["status"] = "passed"

                if self.verbose:
                    print(f"✓ Platform {self.platform_info['system']} is fully compatible")
            else:
                result["status"] = "warning"
                issues = []
                if not is_supported:
                    issues.append(f"Platform {self.platform_info['system']} not officially supported")
                if not python_compatible:
                    issues.append(f"Python {self.platform_info['python_version']} not compatible")
                if not result["details"]["shell_compatible"]:
                    issues.append(f"Shell {shell} may have compatibility issues")

                result["details"]["compatibility_issues"] = issues
                self.warnings.extend(issues)

        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"Cross-platform compatibility test failed: {e}")

        self.results["cross_platform"] = result
        return result

    def test_korean_font_portability(self) -> dict:
        """Test 3: Korean font availability across systems."""
        result = {
            "test": 3,
            "name": "Korean Font Portability",
            "status": "pending",
            "details": {},
        }

        try:
            if self.verbose:
                print("[yellow]Testing Korean font portability...[/yellow]")

            # Platform-specific font checks
            if self.platform_info["system"] == "Darwin":
                # macOS: Check via Homebrew
                success, stdout, _ = self._run_command(
                    ["brew", "list", "--cask", "font-d2coding"]
                )

                if success:
                    result["details"]["d2coding_installed"] = True
                    result["details"]["installation_method"] = "Homebrew"
                    result["status"] = "passed"

                    if self.verbose:
                        print("✓ D2Coding font installed via Homebrew")
                else:
                    result["details"]["d2coding_installed"] = False
                    result["status"] = "warning"
                    self.warnings.append(
                        "D2Coding font not installed. Install with: "
                        "brew install --cask font-d2coding"
                    )

            elif self.platform_info["system"] == "Linux":
                # Linux: Check via fc-list
                fc_list_path = shutil.which("fc-list")

                if fc_list_path:
                    success, stdout, _ = self._run_command(["fc-list", ":", "family"])

                    if success and "D2Coding" in stdout:
                        result["details"]["d2coding_installed"] = True
                        result["details"]["installation_method"] = "System fonts"
                        result["status"] = "passed"

                        if self.verbose:
                            print("✓ D2Coding font found in system fonts")
                    else:
                        result["details"]["d2coding_installed"] = False
                        result["status"] = "warning"
                        self.warnings.append(
                            "D2Coding font not found. Install manually from: "
                            "https://github.com/naver/d2codingfont"
                        )
                else:
                    result["details"]["d2coding_installed"] = False
                    result["status"] = "skipped"
                    result["details"]["reason"] = "fc-list not available"

            else:
                result["status"] = "skipped"
                result["details"]["reason"] = f"Platform {self.platform_info['system']} not supported"

            # Check UTF-8 support (universal)
            try:
                test_korean = "한글 테스트"
                encoded = test_korean.encode("utf-8")
                decoded = encoded.decode("utf-8")
                result["details"]["utf8_support"] = decoded == test_korean
            except Exception:
                result["details"]["utf8_support"] = False
                self.warnings.append("UTF-8 encoding may not be properly supported")

        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"Korean font portability test failed: {e}")

        self.results["korean_fonts"] = result
        return result

    def test_uv_tool_portability(self) -> dict:
        """Test 4: UV tool installation portability."""
        result = {
            "test": 4,
            "name": "UV Tool Portability",
            "status": "pending",
            "details": {},
        }

        try:
            if self.verbose:
                print("[yellow]Testing UV tool portability...[/yellow]")

            # Check uv installation
            uv_path = shutil.which("uv")
            result["details"]["uv_installed"] = uv_path is not None

            if not uv_path:
                result["status"] = "failed"
                result["details"]["error"] = "uv not found in PATH"
                self.errors.append("uv is not installed or not in PATH")
                self.results["uv_portability"] = result
                return result

            result["details"]["uv_path"] = uv_path

            # Check uv version
            success, version, _ = self._run_command(["uv", "--version"])
            if success:
                result["details"]["uv_version"] = version.replace("uv ", "").strip()

            # Check uv tool directory
            home = Path.home()
            uv_tool_dir = home / ".local" / "share" / "uv" / "tools"

            if uv_tool_dir.exists():
                result["details"]["uv_tool_dir"] = str(uv_tool_dir)
                result["details"]["uv_tool_dir_exists"] = True

                # List installed tools
                tools = list(uv_tool_dir.iterdir()) if uv_tool_dir.is_dir() else []
                result["details"]["installed_tools_count"] = len(tools)
                result["details"]["installed_tools"] = [t.name for t in tools[:5]]

                # Check if moai-adk is portable
                moai_dir = uv_tool_dir / "moai-adk"
                result["details"]["moai_adk_portable"] = moai_dir.exists()

                if moai_dir.exists():
                    result["status"] = "passed"

                    if self.verbose:
                        print("✓ UV tools are portable and moai-adk is installed")
                else:
                    result["status"] = "warning"
                    result["details"]["warning"] = "moai-adk not found in uv tools directory"
                    self.warnings.append(
                        "moai-adk not installed via uv tools. Install with: uv tool install moai-adk"
                    )
            else:
                result["status"] = "warning"
                result["details"]["warning"] = "uv tool directory not found"
                self.warnings.append("uv tool directory not initialized")

        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"UV tool portability test failed: {e}")

        self.results["uv_portability"] = result
        return result

    def test_config_file_portability(self) -> dict:
        """Test 5: Configuration file portability."""
        result = {
            "test": 5,
            "name": "Configuration File Portability",
            "status": "pending",
            "details": {},
        }

        try:
            if self.verbose:
                print("[yellow]Testing configuration file portability...[/yellow]")

            # Check .moai directory
            moai_dir = Path.cwd() / ".moai"
            result["details"]["moai_dir_exists"] = moai_dir.exists()

            if not moai_dir.exists():
                result["status"] = "skipped"
                result["details"]["reason"] = ".moai directory not found"
                self.results["config_portability"] = result
                return result

            # Check configuration file
            config_file = moai_dir / "config" / "moai.json"
            result["details"]["config_file_exists"] = config_file.exists()

            if not config_file.exists():
                result["status"] = "warning"
                result["details"]["warning"] = "Configuration file not found"
                self.warnings.append("Run install_moai.py to create configuration")
                self.results["config_portability"] = result
                return result

            # Read and validate configuration
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            result["details"]["config_valid_json"] = True
            result["details"]["config_keys"] = list(config.keys())

            # Check for platform-specific paths
            config_str = json.dumps(config)
            has_absolute_paths = "/" in config_str or "\\" in config_str

            result["details"]["has_absolute_paths"] = has_absolute_paths

            if has_absolute_paths:
                result["status"] = "warning"
                result["details"]["warning"] = "Configuration contains absolute paths (may not be portable)"
                self.warnings.append(
                    "Configuration contains absolute paths which may cause portability issues"
                )
            else:
                result["status"] = "passed"

                if self.verbose:
                    print("✓ Configuration files are portable (no absolute paths)")

            # Check for platform-specific settings
            result["details"]["korean_support"] = config.get("korean_support", False)

        except json.JSONDecodeError as e:
            result["status"] = "failed"
            result["details"]["error"] = f"Invalid JSON: {e}"
            self.errors.append(f"Configuration file is not valid JSON: {e}")
        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"Configuration file portability test failed: {e}")

        self.results["config_portability"] = result
        return result

    def test_dependency_resolution(self) -> dict:
        """Test 6: Dependency resolution and PEP 723 inline dependencies."""
        result = {
            "test": 6,
            "name": "Dependency Resolution",
            "status": "pending",
            "details": {},
        }

        try:
            if self.verbose:
                print("[yellow]Testing dependency resolution...[/yellow]")

            # Create temporary test script with PEP 723 dependencies
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8",
            ) as f:
                test_script = f"""#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1.0",
# ]
# ///

import click
import sys

@click.command()
def main():
    click.echo("Dependency resolution test passed")
    sys.exit(0)

if __name__ == "__main__":
    main()
"""
                f.write(test_script)
                temp_file = f.name

            try:
                # Make executable
                os.chmod(temp_file, 0o755)

                # Test dependency resolution
                success, stdout, stderr = self._run_command(
                    ["uv", "run", temp_file],
                    timeout=60,
                )

                if success and "test passed" in stdout:
                    result["status"] = "passed"
                    result["details"]["dependency_resolution_works"] = True
                    result["details"]["pep723_supported"] = True

                    if self.verbose:
                        print("✓ PEP 723 inline dependencies work correctly")
                else:
                    result["status"] = "failed"
                    result["details"]["dependency_resolution_works"] = False
                    result["details"]["error"] = stderr or "Test script failed"
                    self.errors.append(f"Dependency resolution failed: {stderr}")

            finally:
                # Cleanup
                Path(temp_file).unlink(missing_ok=True)

            # Check click availability (used in all scripts)
            try:
                import click as _
                result["details"]["click_available"] = True
            except ImportError:
                result["details"]["click_available"] = False
                self.warnings.append("click package not available in current environment")

        except Exception as e:
            result["status"] = "failed"
            result["details"]["error"] = str(e)
            self.errors.append(f"Dependency resolution test failed: {e}")

        self.results["dependency_resolution"] = result
        return result

    def run_all_tests(self) -> dict:
        """Run all portability tests."""
        if self.verbose:
            print("🔍 Testing MoAI-ADK portability...\n")

        self.test_virtual_environment_isolation()
        self.test_cross_platform_compatibility()
        self.test_korean_font_portability()
        self.test_uv_tool_portability()
        self.test_config_file_portability()
        self.test_dependency_resolution()

        # Calculate overall status
        passed_count = len([r for r in self.results.values() if r.get("status") == "passed"])
        total_count = len(self.results)

        percentage = (passed_count / total_count) * 100 if total_count > 0 else 0

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
            "tests_passed": passed_count,
            "tests_total": total_count,
            "percentage": round(percentage, 1),
            "platform_info": self.platform_info,
            "errors": self.errors,
            "warnings": self.warnings,
            "results": self.results,
        }

        return summary


def print_human_readable(summary: dict, verbose: bool = False):
    """Print human-readable portability test summary."""
    print("\n" + "=" * 70)
    print("MoAI-ADK Portability Testing Results")
    print("=" * 70 + "\n")

    # Print platform info
    print("Platform Information:")
    for key, value in summary["platform_info"].items():
        print(f"  {key}: {value}")
    print()

    # Print test results
    for key, result in summary["results"].items():
        status = result.get("status", "unknown")
        status_emoji = {
            "passed": "✓",
            "skipped": "⊙",
            "warning": "⚠",
            "failed": "✗",
        }.get(status, "?")

        test_num = result.get("test", "?")
        name = result.get("name", key)

        print(f"{status_emoji} Test {test_num}: {name} - {status.upper()}")

        if verbose and "details" in result:
            print(f"  Details: {json.dumps(result['details'], indent=4)}")
        print()

    # Print summary
    print("=" * 70)
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Tests Passed: {summary['tests_passed']}/{summary['tests_total']} ({summary['percentage']}%)")
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

    # Print portability assessment
    percentage = summary["percentage"]
    if percentage >= 90:
        print("✅ Excellent portability! Installation is highly portable across systems.")
    elif percentage >= 70:
        print("✓ Good portability. Minor platform-specific adjustments may be needed.")
    elif percentage >= 50:
        print("⚠️  Fair portability. Some features may not work on all platforms.")
    else:
        print("❌ Poor portability. Significant platform-specific issues detected.")


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
    Test MoAI-ADK installation portability.

    Tests:
    1. Virtual environment isolation
    2. Cross-platform compatibility
    3. Korean font availability
    4. UV tool portability
    5. Configuration file portability
    6. Dependency resolution

    Examples:
        uv run test_portability.py
        uv run test_portability.py --verbose
        uv run test_portability.py --json
    """
    if show_help:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        return

    tester = PortabilityTester(verbose=verbose)
    summary = tester.run_all_tests()

    if output_json:
        print(json.dumps(summary, indent=2))
    else:
        print_human_readable(summary, verbose=verbose)

    # Exit with warning code if portability is poor
    if summary["percentage"] < 50:
        sys.exit(1)


if __name__ == "__main__":
    main()
