#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11,<3.15"
# dependencies = [
#     "click>=8.1.0",
#     "rich>=13.0.0",
# ]
# ///

"""
MoAI-ADK Korean Language Configuration

Configures Korean language support for MoAI-ADK:
1. Install D2Coding font via Homebrew
2. Configure Ghostty terminal
3. Set up Korean locale
4. Test Korean rendering

Usage:
    uv run configure_korean.py
    uv run configure_korean.py --verbose
    uv run configure_korean.py --auto
    uv run configure_korean.py --json
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
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


class KoreanConfigurator:
    """Korean language support configuration for MoAI-ADK."""

    def __init__(self, verbose: bool = False, auto: bool = False):
        self.verbose = verbose
        self.auto = auto
        self.results: Dict[str, dict] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.home = Path.home()
        self.is_macos = platform.system() == "Darwin"

    def _run_command(
        self,
        cmd: List[str],
        capture_output: bool = True,
        timeout: int = 300,
        shell: bool = False,
    ) -> Tuple[bool, str, str]:
        """Execute command and return success status, stdout, and stderr."""
        try:
            if self.verbose:
                console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")

            result = subprocess.run(
                cmd if not shell else " ".join(cmd),
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                shell=shell,
            )

            success = result.returncode == 0

            if self.verbose and not success:
                console.print(f"[red]Command failed with code {result.returncode}[/red]")

            return success, result.stdout.strip(), result.stderr.strip()

        except Exception as e:
            if self.verbose:
                console.print(f"[red]Command error: {e}[/red]")
            return False, "", str(e)

    def check_homebrew_installed(self) -> bool:
        """Check if Homebrew is installed (macOS only)."""
        if not self.is_macos:
            return False

        success, _, _ = self._run_command(["which", "brew"])
        return success

    def install_d2coding_font(self) -> dict:
        """Install D2Coding font for Korean support."""
        result = {
            "step": "install_font",
            "name": "Install D2Coding Font",
            "status": "pending",
            "details": {},
        }

        try:
            if not self.is_macos:
                result["status"] = "skipped"
                result["details"]["reason"] = "Non-macOS platform - manual font installation required"
                self.warnings.append(
                    "On Linux, install D2Coding font manually: "
                    "https://github.com/naver/d2codingfont"
                )
                self.results["font_install"] = result
                return result

            if self.verbose:
                console.print("[yellow]Checking D2Coding font...[/yellow]")

            # Check if Homebrew is installed
            if not self.check_homebrew_installed():
                result["status"] = "error"
                result["details"]["error"] = "Homebrew not installed"
                self.errors.append(
                    "Homebrew is required. Install from https://brew.sh"
                )
                self.results["font_install"] = result
                return result

            # Check if font is already installed
            success, stdout, _ = self._run_command(
                ["brew", "list", "--cask", "font-d2coding"]
            )

            if success:
                result["status"] = "skipped"
                result["details"]["reason"] = "D2Coding font already installed"

                if self.verbose:
                    console.print("[green]✓ D2Coding font already installed[/green]")

                self.results["font_install"] = result
                return result

            # Tap font cask repository
            if self.verbose:
                console.print("[yellow]Tapping homebrew-cask-fonts...[/yellow]")

            success, _, stderr = self._run_command(
                ["brew", "tap", "homebrew/cask-fonts"]
            )

            if not success and "already tapped" not in stderr:
                result["status"] = "warning"
                result["details"]["tap_warning"] = stderr
                self.warnings.append(f"Font tap warning: {stderr}")

            # Install D2Coding font
            if self.verbose:
                console.print("[yellow]Installing D2Coding font...[/yellow]")

            success, stdout, stderr = self._run_command(
                ["brew", "install", "--cask", "font-d2coding"],
                timeout=180,
            )

            if success:
                result["status"] = "success"
                result["details"]["installed"] = True
                result["details"]["font_name"] = "D2Coding"

                if self.verbose:
                    console.print("[green]✓ D2Coding font installed successfully[/green]")
            else:
                result["status"] = "error"
                result["details"]["error"] = stderr or "Installation failed"
                self.errors.append(f"Failed to install D2Coding font: {stderr}")

        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
            self.errors.append(f"Exception during font installation: {e}")

        self.results["font_install"] = result
        return result

    def configure_ghostty(self) -> dict:
        """Configure Ghostty terminal for Korean support."""
        result = {
            "step": "configure_ghostty",
            "name": "Configure Ghostty Terminal",
            "status": "pending",
            "details": {},
        }

        try:
            if self.verbose:
                console.print("[yellow]Configuring Ghostty terminal...[/yellow]")

            # Check if Ghostty is installed
            ghostty_path = shutil.which("ghostty")
            if not ghostty_path:
                result["status"] = "skipped"
                result["details"]["reason"] = "Ghostty not installed"
                self.warnings.append(
                    "Ghostty not installed. Install with: brew install ghostty (macOS)"
                )
                self.results["ghostty_config"] = result
                return result

            # Create Ghostty config directory
            config_dir = self.home / ".config" / "ghostty"
            config_dir.mkdir(parents=True, exist_ok=True)

            config_file = config_dir / "config"

            # Read existing config or create new
            existing_config = ""
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    existing_config = f.read()

            # Korean-specific configuration
            korean_config = """
# Korean Language Support Configuration
# Added by MoAI-ADK installer

# Font configuration for Korean
font-family = D2Coding
font-size = 13

# Fallback fonts for CJK characters
font-family-bold = D2Coding
font-family-italic = D2Coding
font-family-bold-italic = D2Coding

# Terminal encoding
locale = en_US.UTF-8

# Enable ligatures and proper spacing
font-feature = +liga
font-feature = +calt

# Cursor configuration
cursor-style = block
cursor-style-blink = true

# Color scheme (optional - adjust as needed)
background = 1e1e1e
foreground = d4d4d4

# Korean-specific optimizations
keybind = super+shift+k=reload_config
"""

            # Check if Korean config already exists
            if "D2Coding" in existing_config and "Korean Language Support" in existing_config:
                result["status"] = "skipped"
                result["details"]["reason"] = "Ghostty already configured for Korean"

                if self.verbose:
                    console.print("[green]✓ Ghostty already configured[/green]")
            else:
                # Backup existing config
                if existing_config:
                    backup_file = config_dir / "config.backup"
                    with open(backup_file, "w", encoding="utf-8") as f:
                        f.write(existing_config)
                    result["details"]["backup"] = str(backup_file)

                # Append Korean configuration
                with open(config_file, "a", encoding="utf-8") as f:
                    f.write(korean_config)

                result["status"] = "success"
                result["details"]["config_file"] = str(config_file)
                result["details"]["changes"] = "Added Korean font and encoding settings"

                if self.verbose:
                    console.print(f"[green]✓ Ghostty configured: {config_file}[/green]")

        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
            self.errors.append(f"Failed to configure Ghostty: {e}")

        self.results["ghostty_config"] = result
        return result

    def setup_korean_locale(self) -> dict:
        """Set up Korean locale support."""
        result = {
            "step": "setup_locale",
            "name": "Set Up Korean Locale",
            "status": "pending",
            "details": {},
        }

        try:
            if self.verbose:
                console.print("[yellow]Setting up Korean locale...[/yellow]")

            # Check current locale
            success, current_locale, _ = self._run_command(["locale"])

            result["details"]["current_locale"] = current_locale

            # Check if UTF-8 locale is available
            success, locales, _ = self._run_command(["locale", "-a"])

            utf8_locales = [
                loc for loc in locales.split("\n")
                if "UTF-8" in loc or "utf8" in loc
            ]

            if utf8_locales:
                result["status"] = "success"
                result["details"]["utf8_available"] = True
                result["details"]["available_locales"] = utf8_locales[:5]  # First 5

                # Check if Korean locale is available
                korean_locales = [
                    loc for loc in utf8_locales
                    if "ko_KR" in loc or "korean" in loc.lower()
                ]

                if korean_locales:
                    result["details"]["korean_locale_available"] = True
                    result["details"]["korean_locales"] = korean_locales
                else:
                    result["details"]["korean_locale_available"] = False
                    self.warnings.append(
                        "Korean locale not found. UTF-8 locale is sufficient for Korean text."
                    )

                if self.verbose:
                    console.print("[green]✓ UTF-8 locale available[/green]")
            else:
                result["status"] = "warning"
                result["details"]["utf8_available"] = False
                self.warnings.append(
                    "No UTF-8 locale found. Korean characters may not display correctly."
                )

        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
            self.errors.append(f"Failed to check locale: {e}")

        self.results["locale_setup"] = result
        return result

    def test_korean_rendering(self) -> dict:
        """Test Korean character rendering."""
        result = {
            "step": "test_rendering",
            "name": "Test Korean Rendering",
            "status": "pending",
            "details": {},
        }

        try:
            if self.verbose:
                console.print("[yellow]Testing Korean rendering...[/yellow]")

            # Test strings
            test_strings = {
                "hangul": "안녕하세요",  # Hello
                "mixed": "MoAI-ADK 한글 지원",  # MoAI-ADK Korean Support
                "numbers": "테스트 123",  # Test 123
            }

            # Test each string
            all_displayed = True
            for key, text in test_strings.items():
                try:
                    # Try to encode/decode to verify UTF-8 support
                    encoded = text.encode("utf-8")
                    decoded = encoded.decode("utf-8")

                    if decoded == text:
                        result["details"][f"{key}_test"] = "passed"
                    else:
                        result["details"][f"{key}_test"] = "failed"
                        all_displayed = False
                except Exception as e:
                    result["details"][f"{key}_test"] = f"error: {e}"
                    all_displayed = False

            if all_displayed:
                result["status"] = "success"
                result["details"]["all_tests_passed"] = True

                # Display test output
                if self.verbose:
                    console.print("\n[cyan]Korean Rendering Test:[/cyan]")
                    for key, text in test_strings.items():
                        console.print(f"  {key}: {text}")
                    console.print("[green]✓ All Korean characters rendered correctly[/green]\n")
            else:
                result["status"] = "warning"
                result["details"]["all_tests_passed"] = False
                self.warnings.append(
                    "Some Korean characters may not render correctly. "
                    "Ensure D2Coding font is installed and terminal supports UTF-8."
                )

            result["details"]["test_strings"] = test_strings

        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
            self.errors.append(f"Korean rendering test failed: {e}")

        self.results["rendering_test"] = result
        return result

    def update_moai_config(self) -> dict:
        """Update MoAI-ADK configuration for Korean support."""
        result = {
            "step": "update_config",
            "name": "Update MoAI Config",
            "status": "pending",
            "details": {},
        }

        try:
            if self.verbose:
                console.print("[yellow]Updating MoAI-ADK config...[/yellow]")

            moai_config = Path.cwd() / ".moai" / "config" / "moai.json"

            if not moai_config.exists():
                result["status"] = "skipped"
                result["details"]["reason"] = ".moai/config/moai.json not found"
                self.warnings.append(
                    "MoAI config not found. Run install_moai.py first."
                )
                self.results["config_update"] = result
                return result

            # Read existing config
            with open(moai_config, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Update Korean support flag
            config["korean_support"] = True
            config["font"] = {
                "family": "D2Coding",
                "size": 13,
            }
            config["locale"] = "en_US.UTF-8"

            # Write updated config
            with open(moai_config, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            result["status"] = "success"
            result["details"]["config_file"] = str(moai_config)
            result["details"]["korean_support_enabled"] = True

            if self.verbose:
                console.print("[green]✓ MoAI config updated for Korean support[/green]")

        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
            self.errors.append(f"Failed to update MoAI config: {e}")

        self.results["config_update"] = result
        return result

    def run_configuration(self) -> dict:
        """Run complete Korean configuration process."""
        if not self.verbose:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Configuring Korean support...", total=5)

                progress.update(task, description="[cyan]Installing D2Coding font...")
                self.install_d2coding_font()
                progress.advance(task)

                progress.update(task, description="[cyan]Configuring Ghostty...")
                self.configure_ghostty()
                progress.advance(task)

                progress.update(task, description="[cyan]Setting up locale...")
                self.setup_korean_locale()
                progress.advance(task)

                progress.update(task, description="[cyan]Testing rendering...")
                self.test_korean_rendering()
                progress.advance(task)

                progress.update(task, description="[cyan]Updating config...")
                self.update_moai_config()
                progress.advance(task)
        else:
            self.install_d2coding_font()
            self.configure_ghostty()
            self.setup_korean_locale()
            self.test_korean_rendering()
            self.update_moai_config()

        # Generate summary
        all_success = all(
            r.get("status") in ["success", "skipped"]
            for r in self.results.values()
        )

        summary = {
            "overall_status": "SUCCESS" if all_success and not self.errors else "PARTIAL",
            "steps_completed": len([r for r in self.results.values() if r.get("status") == "success"]),
            "steps_total": len(self.results),
            "errors": self.errors,
            "warnings": self.warnings,
            "results": self.results,
        }

        return summary


def print_human_readable(summary: dict, verbose: bool = False):
    """Print human-readable configuration summary."""
    console.print("\n" + "=" * 70)
    console.print("[bold]Korean Language Configuration Summary[/bold]")
    console.print("=" * 70 + "\n")

    # Create results table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Step", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")

    for key, result in summary["results"].items():
        status = result.get("status", "unknown")
        status_emoji = {
            "success": "✓",
            "skipped": "⊙",
            "warning": "⚠",
            "error": "✗",
        }.get(status, "?")

        details = result.get("details", {}).get("reason", "")

        table.add_row(
            result.get("name", key),
            f"{status_emoji} {status.upper()}",
            details,
        )

    console.print(table)

    # Print summary
    console.print("\n" + "=" * 70)
    console.print(f"Overall Status: [bold]{summary['overall_status']}[/bold]")
    console.print(f"Steps Completed: {summary['steps_completed']}/{summary['steps_total']}")
    console.print("=" * 70 + "\n")

    # Print errors
    if summary["errors"]:
        console.print(Panel(
            "\n".join(f"• {error}" for error in summary["errors"]),
            title="[bold red]Errors[/bold red]",
            border_style="red",
        ))

    # Print warnings
    if summary["warnings"]:
        console.print(Panel(
            "\n".join(f"• {warning}" for warning in summary["warnings"]),
            title="[bold yellow]Warnings[/bold yellow]",
            border_style="yellow",
        ))

    # Print next steps
    if summary["overall_status"] == "SUCCESS":
        console.print(Panel(
            """[green]✅ Korean support configured successfully![/green]

Next steps:
  1. Restart Ghostty terminal for changes to take effect

  2. Test Korean rendering:
     uv run test_korean_fonts.py

  3. Validate full installation:
     uv run validate_install.py

  4. Start using MoAI-ADK with Korean:
     moai-adk --help
     # Should display: 안녕하세요 (Hello)""",
            title="[bold green]Configuration Complete[/bold green]",
            border_style="green",
        ))


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
    "--auto",
    "-a",
    is_flag=True,
    help="Automatic mode - skip confirmations",
)
@click.option(
    "--help",
    "-h",
    "show_help",
    is_flag=True,
    help="Show this help message and exit",
)
def main(verbose: bool, output_json: bool, auto: bool, show_help: bool):
    """
    Configure Korean language support for MoAI-ADK.

    This script will:
    1. Install D2Coding font via Homebrew
    2. Configure Ghostty terminal
    3. Set up Korean locale
    4. Test Korean rendering
    5. Update MoAI-ADK configuration

    Examples:
        uv run configure_korean.py
        uv run configure_korean.py --verbose
        uv run configure_korean.py --auto
        uv run configure_korean.py --json
    """
    if show_help:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        return

    configurator = KoreanConfigurator(verbose=verbose, auto=auto)
    summary = configurator.run_configuration()

    if output_json:
        print(json.dumps(summary, indent=2))
    else:
        print_human_readable(summary, verbose=verbose)


if __name__ == "__main__":
    main()
