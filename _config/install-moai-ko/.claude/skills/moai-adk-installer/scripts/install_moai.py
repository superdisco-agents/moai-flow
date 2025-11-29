#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11,<3.15"
# dependencies = [
#     "click>=8.1.0",
#     "rich>=13.0.0",
# ]
# ///

"""
MoAI-ADK Installation Script

Installs and configures MoAI-ADK with the following steps:
1. Install uv package manager (if missing)
2. Install moai-adk via uv tool
3. Initialize project structure
4. Configure .moai/ directory
5. Verify installation

Usage:
    uv run install_moai.py
    uv run install_moai.py --verbose
    uv run install_moai.py --json
    uv run install_moai.py --korean
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.table import Table

console = Console()


class MoAIInstaller:
    """MoAI-ADK installation and configuration manager."""

    def __init__(self, verbose: bool = False, korean: bool = False):
        self.verbose = verbose
        self.korean = korean
        self.results: Dict[str, dict] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.home = Path.home()

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
                if result.stderr:
                    console.print(f"[red]Error: {result.stderr}[/red]")

            return success, result.stdout.strip(), result.stderr.strip()

        except subprocess.TimeoutExpired:
            error = f"Command timed out after {timeout}s"
            if self.verbose:
                console.print(f"[red]{error}[/red]")
            return False, "", error
        except FileNotFoundError as e:
            error = f"Command not found: {e}"
            if self.verbose:
                console.print(f"[red]{error}[/red]")
            return False, "", error
        except Exception as e:
            error = str(e)
            if self.verbose:
                console.print(f"[red]Unexpected error: {error}[/red]")
            return False, "", error

    def check_uv_installed(self) -> bool:
        """Check if uv is already installed."""
        success, stdout, _ = self._run_command(["which", "uv"])
        return success and stdout

    def install_uv(self) -> dict:
        """Install uv package manager if not already installed."""
        result = {
            "step": "install_uv",
            "name": "Install UV Package Manager",
            "status": "pending",
            "details": {},
        }

        try:
            # Check if already installed
            if self.check_uv_installed():
                success, version, _ = self._run_command(["uv", "--version"])
                result["status"] = "skipped"
                result["details"]["reason"] = "uv already installed"
                result["details"]["version"] = version.replace("uv ", "").strip()

                if self.verbose:
                    console.print("[green]✓ uv already installed[/green]")

                self.results["uv_install"] = result
                return result

            # Install uv
            if self.verbose:
                console.print("[yellow]Installing uv package manager...[/yellow]")

            install_cmd = "curl -LsSf https://astral.sh/uv/install.sh | sh"
            success, stdout, stderr = self._run_command(
                [install_cmd],
                shell=True,
                timeout=180,
            )

            if success:
                # Verify installation
                time.sleep(2)  # Wait for PATH update

                # Check with explicit path
                uv_path = self.home / ".cargo" / "bin" / "uv"
                if uv_path.exists():
                    success, version, _ = self._run_command([str(uv_path), "--version"])
                    result["status"] = "success"
                    result["details"]["version"] = version.replace("uv ", "").strip()
                    result["details"]["path"] = str(uv_path)

                    if self.verbose:
                        console.print("[green]✓ uv installed successfully[/green]")
                else:
                    result["status"] = "error"
                    result["details"]["error"] = "uv binary not found after installation"
                    self.errors.append("Failed to install uv: binary not found")
            else:
                result["status"] = "error"
                result["details"]["error"] = stderr or "Installation failed"
                self.errors.append(f"Failed to install uv: {stderr}")

        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
            self.errors.append(f"Exception during uv installation: {e}")

        self.results["uv_install"] = result
        return result

    def install_moai_adk(self) -> dict:
        """Install moai-adk using uv tool."""
        result = {
            "step": "install_moai_adk",
            "name": "Install MoAI-ADK",
            "status": "pending",
            "details": {},
        }

        try:
            if self.verbose:
                console.print("[yellow]Installing MoAI-ADK...[/yellow]")

            # Install moai-adk
            success, stdout, stderr = self._run_command(
                ["uv", "tool", "install", "moai-adk"],
                timeout=300,
            )

            if success or "already installed" in stderr.lower():
                # Verify installation
                success_verify, version_output, _ = self._run_command(
                    ["uv", "tool", "run", "moai-adk", "--version"]
                )

                if success_verify:
                    result["status"] = "success"
                    result["details"]["version"] = version_output.strip()
                    result["details"]["stdout"] = stdout

                    if self.verbose:
                        console.print(f"[green]✓ MoAI-ADK installed: {version_output}[/green]")
                else:
                    # Try without uv tool run
                    success_verify, version_output, _ = self._run_command(
                        ["moai-adk", "--version"]
                    )

                    if success_verify:
                        result["status"] = "success"
                        result["details"]["version"] = version_output.strip()
                        result["details"]["stdout"] = stdout
                    else:
                        result["status"] = "warning"
                        result["details"]["message"] = "Installed but version check failed"
                        result["details"]["stderr"] = stderr
                        self.warnings.append("MoAI-ADK installed but version verification failed")
            else:
                result["status"] = "error"
                result["details"]["error"] = stderr or "Installation failed"
                result["details"]["stdout"] = stdout
                self.errors.append(f"Failed to install MoAI-ADK: {stderr}")

        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
            self.errors.append(f"Exception during MoAI-ADK installation: {e}")

        self.results["moai_install"] = result
        return result

    def initialize_project_structure(self) -> dict:
        """Initialize MoAI-ADK project structure."""
        result = {
            "step": "init_project",
            "name": "Initialize Project Structure",
            "status": "pending",
            "details": {"directories_created": []},
        }

        try:
            if self.verbose:
                console.print("[yellow]Initializing project structure...[/yellow]")

            # Create .moai directory structure
            moai_dir = Path.cwd() / ".moai"
            directories = [
                moai_dir,
                moai_dir / "agents",
                moai_dir / "commands",
                moai_dir / "config",
                moai_dir / "logs",
                moai_dir / "cache",
            ]

            created = []
            for directory in directories:
                if not directory.exists():
                    directory.mkdir(parents=True, exist_ok=True)
                    created.append(str(directory))
                    if self.verbose:
                        console.print(f"[dim]Created: {directory}[/dim]")

            result["status"] = "success"
            result["details"]["directories_created"] = created
            result["details"]["moai_dir"] = str(moai_dir)

            if self.verbose:
                console.print(f"[green]✓ Created {len(created)} directories[/green]")

        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
            self.errors.append(f"Failed to initialize project structure: {e}")

        self.results["project_init"] = result
        return result

    def configure_moai_directory(self) -> dict:
        """Configure .moai directory with default settings."""
        result = {
            "step": "configure_moai",
            "name": "Configure .moai Directory",
            "status": "pending",
            "details": {"files_created": []},
        }

        try:
            if self.verbose:
                console.print("[yellow]Configuring .moai directory...[/yellow]")

            moai_dir = Path.cwd() / ".moai"
            config_dir = moai_dir / "config"

            # Create default config file
            config_file = config_dir / "moai.json"
            default_config = {
                "version": "1.0.0",
                "korean_support": self.korean,
                "agents": {
                    "max_concurrent": 5,
                    "timeout": 300,
                },
                "logging": {
                    "level": "INFO",
                    "directory": "logs",
                },
            }

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)

            files_created = [str(config_file)]

            # Create README
            readme_file = moai_dir / "README.md"
            readme_content = """# MoAI-ADK Configuration

This directory contains MoAI-ADK configuration and runtime files.

## Directory Structure

- `agents/` - Agent definitions and configurations
- `commands/` - Custom command definitions
- `config/` - Configuration files
- `logs/` - Application logs
- `cache/` - Temporary cache files

## Configuration

Edit `config/moai.json` to customize MoAI-ADK behavior.

## Korean Support

{}
""".format(
                "Korean font support is enabled. Use Ghostty terminal for best results."
                if self.korean
                else "To enable Korean support, run: uv run configure_korean.py"
            )

            with open(readme_file, "w", encoding="utf-8") as f:
                f.write(readme_content)

            files_created.append(str(readme_file))

            # Create .gitignore
            gitignore_file = moai_dir / ".gitignore"
            gitignore_content = """logs/
cache/
*.pyc
__pycache__/
.DS_Store
"""

            with open(gitignore_file, "w", encoding="utf-8") as f:
                f.write(gitignore_content)

            files_created.append(str(gitignore_file))

            result["status"] = "success"
            result["details"]["files_created"] = files_created
            result["details"]["config"] = default_config

            if self.verbose:
                console.print(f"[green]✓ Created {len(files_created)} configuration files[/green]")

        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
            self.errors.append(f"Failed to configure .moai directory: {e}")

        self.results["moai_config"] = result
        return result

    def verify_installation(self) -> dict:
        """Verify MoAI-ADK installation."""
        result = {
            "step": "verify",
            "name": "Verify Installation",
            "status": "pending",
            "details": {},
        }

        try:
            if self.verbose:
                console.print("[yellow]Verifying installation...[/yellow]")

            # Check moai-adk command
            success, version, stderr = self._run_command(
                ["moai-adk", "--version"]
            )

            if success:
                result["status"] = "success"
                result["details"]["version"] = version.strip()
                result["details"]["moai_adk_available"] = True

                if self.verbose:
                    console.print(f"[green]✓ MoAI-ADK is available: {version}[/green]")
            else:
                # Try with uv tool run
                success, version, stderr = self._run_command(
                    ["uv", "tool", "run", "moai-adk", "--version"]
                )

                if success:
                    result["status"] = "success"
                    result["details"]["version"] = version.strip()
                    result["details"]["moai_adk_available"] = True
                    result["details"]["note"] = "Available via 'uv tool run moai-adk'"

                    self.warnings.append(
                        "moai-adk must be run via 'uv tool run moai-adk'. "
                        "Add ~/.cargo/bin to PATH for direct access."
                    )
                else:
                    result["status"] = "error"
                    result["details"]["error"] = stderr or "Command not available"
                    result["details"]["moai_adk_available"] = False
                    self.errors.append("MoAI-ADK command is not available")

        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
            self.errors.append(f"Verification failed: {e}")

        self.results["verification"] = result
        return result

    def run_installation(self) -> dict:
        """Run complete installation process."""
        if not self.verbose:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Installing MoAI-ADK...", total=5)

                progress.update(task, description="[cyan]Installing uv...")
                self.install_uv()
                progress.advance(task)

                progress.update(task, description="[cyan]Installing MoAI-ADK...")
                self.install_moai_adk()
                progress.advance(task)

                progress.update(task, description="[cyan]Initializing project...")
                self.initialize_project_structure()
                progress.advance(task)

                progress.update(task, description="[cyan]Configuring .moai...")
                self.configure_moai_directory()
                progress.advance(task)

                progress.update(task, description="[cyan]Verifying installation...")
                self.verify_installation()
                progress.advance(task)
        else:
            self.install_uv()
            self.install_moai_adk()
            self.initialize_project_structure()
            self.configure_moai_directory()
            self.verify_installation()

        # Generate summary
        all_success = all(
            r.get("status") in ["success", "skipped"]
            for r in self.results.values()
        )

        summary = {
            "overall_status": "SUCCESS" if all_success and not self.errors else "FAILED",
            "steps_completed": len([r for r in self.results.values() if r.get("status") == "success"]),
            "steps_total": len(self.results),
            "errors": self.errors,
            "warnings": self.warnings,
            "results": self.results,
        }

        return summary


def print_human_readable(summary: dict, verbose: bool = False):
    """Print human-readable installation summary."""
    console.print("\n" + "=" * 70)
    console.print("[bold]MoAI-ADK Installation Summary[/bold]")
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
            "pending": "○",
        }.get(status, "?")

        details = ""
        if "version" in result.get("details", {}):
            details = f"Version: {result['details']['version']}"
        elif "directories_created" in result.get("details", {}):
            count = len(result["details"]["directories_created"])
            details = f"{count} directories"
        elif "files_created" in result.get("details", {}):
            count = len(result["details"]["files_created"])
            details = f"{count} files"

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
            """[green]✅ MoAI-ADK installed successfully![/green]

Next steps:
  1. Add to PATH (if needed):
     export PATH="$HOME/.cargo/bin:$PATH"

  2. Configure Korean support (optional):
     uv run configure_korean.py

  3. Validate installation:
     uv run validate_install.py

  4. Start using MoAI-ADK:
     moai-adk --help
     npx moai-adk /moai:0""",
            title="[bold green]Installation Complete[/bold green]",
            border_style="green",
        ))
    else:
        console.print(Panel(
            "[red]Installation encountered errors. Please resolve them and try again.[/red]",
            title="[bold red]Installation Failed[/bold red]",
            border_style="red",
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
    "--korean",
    "-k",
    is_flag=True,
    help="Enable Korean language support configuration",
)
@click.option(
    "--help",
    "-h",
    "show_help",
    is_flag=True,
    help="Show this help message and exit",
)
def main(verbose: bool, output_json: bool, korean: bool, show_help: bool):
    """
    Install and configure MoAI-ADK.

    This script will:
    1. Install uv package manager (if missing)
    2. Install moai-adk via uv tool
    3. Initialize project structure
    4. Configure .moai/ directory
    5. Verify installation

    Examples:
        uv run install_moai.py
        uv run install_moai.py --verbose
        uv run install_moai.py --korean
        uv run install_moai.py --json
    """
    if show_help:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        return

    installer = MoAIInstaller(verbose=verbose, korean=korean)
    summary = installer.run_installation()

    if output_json:
        print(json.dumps(summary, indent=2))
    else:
        print_human_readable(summary, verbose=verbose)

    # Exit with error code if installation failed
    if summary["overall_status"] != "SUCCESS":
        sys.exit(1)


if __name__ == "__main__":
    main()
