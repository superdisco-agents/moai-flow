#!/usr/bin/env python3
"""
MoAI-ADK UV CLI Installer
Version: 1.0.0

A comprehensive, interactive CLI installer for MoAI-ADK with Korean language support.

Features:
- Click-based command groups
- Interactive prompts with rich output
- Korean language auto-detection
- Progress indicators
- Comprehensive validation

Usage:
    uv run installer.py install
    uv run installer.py install --korean
    uv run installer.py verify
    uv run installer.py status
    uv run installer.py uninstall
    uv run installer.py setup-korean

Dependencies (PEP 723):
# /// script
# dependencies = [
#   "click>=8.1.0",
#   "rich>=13.0.0",
# ]
# ///
"""

import os
import sys
import json
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

try:
    import click
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.prompt import Confirm, Prompt
    from rich.syntax import Syntax
    from rich.markdown import Markdown
except ImportError:
    print("Error: Required dependencies not found")
    print("Install with: uv pip install click rich")
    sys.exit(1)

# ============================================================================
# Configuration & Constants
# ============================================================================

VERSION = "1.0.0"
PYTHON_MIN_VERSION = (3, 11)
MOAI_PACKAGE = "moai-adk"
MOAI_CONFIG_DIR = Path.home() / ".moai"
LOG_FILE = MOAI_CONFIG_DIR / "logs" / "installer.log"

console = Console()

# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class SystemInfo:
    """System information dataclass"""
    os_type: str
    os_version: str
    architecture: str
    python_version: str
    python_executable: str
    disk_space_mb: int
    has_uv: bool
    uv_version: Optional[str]
    locale: str
    is_korean: bool

@dataclass
class InstallationConfig:
    """Installation configuration"""
    install_korean_fonts: bool = False
    skip_python_check: bool = False
    skip_uv_install: bool = False
    force_reinstall: bool = False
    verbose: bool = False

@dataclass
class InstallationStatus:
    """Installation status tracking"""
    config_dir_created: bool = False
    uv_installed: bool = False
    moai_installed: bool = False
    korean_configured: bool = False
    activation_script_created: bool = False

# ============================================================================
# Utility Functions
# ============================================================================

def setup_logging():
    """Initialize logging directory and file"""
    MOAI_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def log_message(level: str, message: str):
    """Write log message to file"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"

    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

def get_system_info() -> SystemInfo:
    """Gather comprehensive system information"""

    # OS detection
    os_type = platform.system()
    os_version = platform.version()
    architecture = platform.machine()

    # Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    python_executable = sys.executable

    # Disk space
    stat = shutil.disk_usage(Path.home())
    disk_space_mb = stat.free // (1024 * 1024)

    # UV detection
    has_uv = shutil.which("uv") is not None
    uv_version = None
    if has_uv:
        try:
            result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
            uv_version = result.stdout.strip().split()[1]
        except:
            pass

    # Locale detection
    locale = os.environ.get("LANG", "en_US.UTF-8")
    is_korean = locale.startswith("ko_") or "KR" in locale

    return SystemInfo(
        os_type=os_type,
        os_version=os_version,
        architecture=architecture,
        python_version=python_version,
        python_executable=python_executable,
        disk_space_mb=disk_space_mb,
        has_uv=has_uv,
        uv_version=uv_version,
        locale=locale,
        is_korean=is_korean
    )

def check_python_version() -> bool:
    """Validate Python version meets minimum requirements"""
    current = (sys.version_info.major, sys.version_info.minor)
    if current < PYTHON_MIN_VERSION:
        console.print(f"[red]Error:[/red] Python {PYTHON_MIN_VERSION[0]}.{PYTHON_MIN_VERSION[1]}+ required")
        console.print(f"Current version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return False
    return True

def run_command(cmd: List[str], description: str, capture_output: bool = True) -> bool:
    """Execute shell command with error handling"""
    try:
        log_message("DEBUG", f"Running: {' '.join(cmd)}")

        if capture_output:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if result.stdout:
                log_message("DEBUG", f"Output: {result.stdout}")
        else:
            subprocess.run(cmd, check=True)

        console.print(f"[green]✓[/green] {description}")
        log_message("SUCCESS", description)
        return True

    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗[/red] {description}")
        console.print(f"[red]Error:[/red] {e}")
        log_message("ERROR", f"{description}: {e}")
        return False
    except FileNotFoundError:
        console.print(f"[red]✗[/red] Command not found: {cmd[0]}")
        log_message("ERROR", f"Command not found: {cmd[0]}")
        return False

# ============================================================================
# Installation Functions
# ============================================================================

def install_uv(config: InstallationConfig) -> bool:
    """Install UV package manager"""

    if config.skip_uv_install:
        console.print("[yellow]Skipping UV installation[/yellow]")
        return True

    system = get_system_info()

    if system.has_uv and not config.force_reinstall:
        console.print(f"[green]✓[/green] UV already installed (version: {system.uv_version})")
        return True

    console.print("[cyan]Installing UV package manager...[/cyan]")

    try:
        # Download and run UV installer
        curl_cmd = [
            "curl", "-LsSf", "https://astral.sh/uv/install.sh"
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            console.print("[red]Failed to download UV installer[/red]")
            return False

        # Run installer script
        bash_cmd = ["sh"]
        process = subprocess.Popen(
            bash_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(input=result.stdout)

        if process.returncode == 0:
            console.print("[green]✓[/green] UV installed successfully")

            # Add to PATH instructions
            shell_config = Path.home() / ".zshrc" if Path(Path.home() / ".zshrc").exists() else Path.home() / ".bashrc"
            console.print(f"\n[yellow]Note:[/yellow] Add UV to PATH:")
            console.print(f"[cyan]export PATH=\"$HOME/.cargo/bin:$PATH\"[/cyan]")
            console.print(f"Add to: {shell_config}\n")

            return True
        else:
            console.print(f"[red]UV installation failed:[/red] {stderr}")
            return False

    except Exception as e:
        console.print(f"[red]Error installing UV:[/red] {e}")
        return False

def create_moai_directory(config: InstallationConfig) -> bool:
    """Create MoAI configuration directory structure"""

    console.print("[cyan]Creating MoAI directory structure...[/cyan]")

    try:
        # Check if exists
        if MOAI_CONFIG_DIR.exists() and config.force_reinstall:
            backup_dir = MOAI_CONFIG_DIR.parent / f".moai.backup.{int(os.time())}"
            shutil.move(str(MOAI_CONFIG_DIR), str(backup_dir))
            console.print(f"[yellow]Backed up existing config to:[/yellow] {backup_dir}")

        # Create directory structure
        directories = [
            MOAI_CONFIG_DIR / "models",
            MOAI_CONFIG_DIR / "cache",
            MOAI_CONFIG_DIR / "logs",
            MOAI_CONFIG_DIR / "config"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        console.print(f"[green]✓[/green] Created directory: {MOAI_CONFIG_DIR}")
        return True

    except Exception as e:
        console.print(f"[red]Error creating directories:[/red] {e}")
        return False

def install_moai_adk(config: InstallationConfig) -> bool:
    """Install MoAI-ADK package using UV"""

    console.print("[cyan]Installing MoAI-ADK package...[/cyan]")

    if not shutil.which("uv"):
        console.print("[red]Error:[/red] UV not found in PATH")
        console.print("Run: [cyan]source ~/.bashrc[/cyan] or [cyan]source ~/.zshrc[/cyan]")
        return False

    cmd = ["uv", "pip", "install"]

    if config.force_reinstall:
        cmd.append("--force-reinstall")

    cmd.append(MOAI_PACKAGE)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Installing MoAI-ADK...", total=None)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            progress.update(task, completed=100)
            console.print("[green]✓[/green] MoAI-ADK installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[red]✗[/red] Installation failed: {e}")
            return False

def verify_installation() -> bool:
    """Verify MoAI-ADK installation"""

    console.print("[cyan]Verifying installation...[/cyan]")

    try:
        result = subprocess.run(
            [sys.executable, "-c", "import moai_adk; print(moai_adk.__version__)"],
            capture_output=True,
            text=True,
            check=True
        )

        version = result.stdout.strip()
        console.print(f"[green]✓[/green] MoAI-ADK version {version} is correctly installed")
        return True

    except subprocess.CalledProcessError:
        console.print("[red]✗[/red] MoAI-ADK import failed")
        return False

# ============================================================================
# Korean Language Support
# ============================================================================

def install_korean_fonts_macos() -> bool:
    """Install Korean fonts on macOS"""

    if not shutil.which("brew"):
        console.print("[yellow]Homebrew not found. Skipping Korean fonts.[/yellow]")
        console.print("Install Homebrew: [cyan]https://brew.sh[/cyan]")
        return False

    fonts = ["font-nanum", "font-nanum-gothic-coding"]

    for font in fonts:
        console.print(f"Installing {font}...")
        run_command(["brew", "install", "--cask", font], f"Installed {font}")

    return True

def install_korean_fonts_linux() -> bool:
    """Install Korean fonts on Linux"""

    if shutil.which("apt-get"):
        cmd = ["sudo", "apt-get", "install", "-y", "fonts-nanum", "fonts-nanum-coding"]
        return run_command(cmd, "Installed Korean fonts (apt)")

    elif shutil.which("yum"):
        cmd = ["sudo", "yum", "install", "-y", "google-noto-sans-cjk-ttc-fonts"]
        return run_command(cmd, "Installed Korean fonts (yum)")

    elif shutil.which("pacman"):
        cmd = ["sudo", "pacman", "-S", "--noconfirm", "noto-fonts-cjk"]
        return run_command(cmd, "Installed Korean fonts (pacman)")

    else:
        console.print("[yellow]Unknown package manager. Please install Korean fonts manually.[/yellow]")
        return False

def configure_korean_locale() -> bool:
    """Configure Korean locale settings"""

    console.print("[cyan]Configuring Korean locale...[/cyan]")

    config_file = MOAI_CONFIG_DIR / "config" / "settings.json"

    korean_config = {
        "language": "ko_KR",
        "locale": "ko_KR.UTF-8",
        "encoding": "UTF-8",
        "ui": {
            "font_family": "Nanum Gothic",
            "font_size": 14
        },
        "features": {
            "korean_nlp": True,
            "korean_tokenizer": True
        }
    }

    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(korean_config, f, indent=2, ensure_ascii=False)

        console.print(f"[green]✓[/green] Korean configuration created: {config_file}")
        return True

    except Exception as e:
        console.print(f"[red]Error creating config:[/red] {e}")
        return False

def setup_korean_support() -> bool:
    """Complete Korean language setup"""

    console.print("\n[bold cyan]Korean Language Setup[/bold cyan]\n")

    system = get_system_info()

    if system.os_type == "Darwin":
        install_korean_fonts_macos()
    elif system.os_type == "Linux":
        install_korean_fonts_linux()
    else:
        console.print(f"[yellow]Korean fonts not supported on {system.os_type}[/yellow]")

    configure_korean_locale()

    return True

# ============================================================================
# Post-Installation
# ============================================================================

def create_activation_script() -> bool:
    """Create shell activation script"""

    console.print("[cyan]Creating activation script...[/cyan]")

    activate_script = MOAI_CONFIG_DIR / "activate.sh"

    script_content = f'''#!/usr/bin/env bash
# MoAI-ADK Activation Script

export MOAI_CONFIG_DIR="{MOAI_CONFIG_DIR}"
export MOAI_CACHE_DIR="{MOAI_CONFIG_DIR}/cache"
export MOAI_LOG_DIR="{MOAI_CONFIG_DIR}/logs"

# Add UV to PATH
export PATH="$HOME/.cargo/bin:$PATH"

echo "MoAI-ADK environment activated"
echo "Config directory: $MOAI_CONFIG_DIR"
'''

    try:
        with open(activate_script, "w") as f:
            f.write(script_content)

        activate_script.chmod(0o755)
        console.print(f"[green]✓[/green] Activation script: {activate_script}")
        return True

    except Exception as e:
        console.print(f"[red]Error creating activation script:[/red] {e}")
        return False

def display_next_steps(korean_enabled: bool):
    """Display post-installation instructions"""

    steps = f"""
# Installation Complete!

## Next Steps:

1. **Activate MoAI environment:**
   ```bash
   source {MOAI_CONFIG_DIR}/activate.sh
   ```

2. **Verify installation:**
   ```bash
   python3 -c "import moai_adk; print(moai_adk.__version__)"
   ```

3. **View documentation:**
   ```bash
   python3 -m moai_adk --help
   ```

4. **Configuration directory:**
   {MOAI_CONFIG_DIR}

5. **View logs:**
   {LOG_FILE}
"""

    if korean_enabled:
        steps += f"""
## Korean Language Support

Korean fonts and locale have been configured.

**Settings file:** {MOAI_CONFIG_DIR}/config/settings.json
"""

    md = Markdown(steps)
    console.print(Panel(md, title="[bold green]Success![/bold green]", border_style="green"))

# ============================================================================
# CLI Commands
# ============================================================================

@click.group()
@click.version_option(VERSION)
def cli():
    """
    MoAI-ADK UV CLI Installer

    A comprehensive installer for MoAI-ADK with Korean language support.
    """
    setup_logging()

@cli.command()
@click.option("--korean", "-k", is_flag=True, help="Install Korean language support")
@click.option("--skip-python", "-s", is_flag=True, help="Skip Python version check")
@click.option("--skip-uv", "-u", is_flag=True, help="Skip UV installation")
@click.option("--force", "-f", is_flag=True, help="Force reinstallation")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def install(korean, skip_python, skip_uv, force, verbose):
    """Install MoAI-ADK with optional Korean support"""

    console.print(Panel.fit(
        "[bold cyan]MoAI-ADK Installer v{VERSION}[/bold cyan]\n"
        "Mixture of Agents AI Development Kit",
        border_style="cyan"
    ))

    # Create configuration
    config = InstallationConfig(
        install_korean_fonts=korean,
        skip_python_check=skip_python,
        skip_uv_install=skip_uv,
        force_reinstall=force,
        verbose=verbose
    )

    # Display system info
    system = get_system_info()

    table = Table(title="System Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("OS", f"{system.os_type} {system.os_version}")
    table.add_row("Architecture", system.architecture)
    table.add_row("Python", system.python_version)
    table.add_row("Disk Space", f"{system.disk_space_mb} MB")
    table.add_row("Locale", system.locale)
    table.add_row("Korean Detected", "Yes" if system.is_korean else "No")

    console.print(table)
    console.print()

    # Auto-detect Korean
    if system.is_korean and not korean:
        if Confirm.ask("Korean locale detected. Install Korean support?", default=True):
            config.install_korean_fonts = True

    # Confirm installation
    if not Confirm.ask("\nProceed with installation?", default=True):
        console.print("[yellow]Installation cancelled[/yellow]")
        return

    # Installation steps
    console.print("\n[bold]Starting installation...[/bold]\n")

    # 1. Python check
    if not config.skip_python_check:
        if not check_python_version():
            return

    # 2. Create directory
    if not create_moai_directory(config):
        return

    # 3. Install UV
    if not install_uv(config):
        console.print("[yellow]Continuing without UV...[/yellow]")

    # 4. Install MoAI-ADK
    if not install_moai_adk(config):
        return

    # 5. Verify installation
    if not verify_installation():
        return

    # 6. Korean support
    if config.install_korean_fonts:
        setup_korean_support()

    # 7. Create activation script
    create_activation_script()

    # Success
    display_next_steps(config.install_korean_fonts)

@cli.command()
def verify():
    """Verify MoAI-ADK installation"""

    console.print("[bold]Verifying MoAI-ADK installation...[/bold]\n")

    checks = []

    # Check directory
    if MOAI_CONFIG_DIR.exists():
        checks.append(("Config directory", True, str(MOAI_CONFIG_DIR)))
    else:
        checks.append(("Config directory", False, "Not found"))

    # Check UV
    has_uv = shutil.which("uv") is not None
    uv_info = "Installed" if has_uv else "Not found"
    checks.append(("UV package manager", has_uv, uv_info))

    # Check MoAI-ADK
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import moai_adk; print(moai_adk.__version__)"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        checks.append(("MoAI-ADK", True, f"v{version}"))
    except:
        checks.append(("MoAI-ADK", False, "Not installed"))

    # Check Korean config
    korean_config = MOAI_CONFIG_DIR / "config" / "settings.json"
    if korean_config.exists():
        checks.append(("Korean config", True, str(korean_config)))
    else:
        checks.append(("Korean config", False, "Not configured"))

    # Display results
    table = Table(title="Installation Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="yellow")
    table.add_column("Details", style="white")

    for name, status, details in checks:
        status_icon = "[green]✓[/green]" if status else "[red]✗[/red]"
        table.add_row(name, status_icon, details)

    console.print(table)

@cli.command()
def status():
    """Show current MoAI-ADK status and configuration"""

    system = get_system_info()

    # System info panel
    system_table = Table(title="System Information", show_header=False)
    system_table.add_column("Key", style="cyan")
    system_table.add_column("Value", style="white")

    for key, value in asdict(system).items():
        system_table.add_row(key.replace("_", " ").title(), str(value))

    console.print(system_table)
    console.print()

    # Configuration
    if MOAI_CONFIG_DIR.exists():
        config_file = MOAI_CONFIG_DIR / "config" / "settings.json"

        if config_file.exists():
            with open(config_file) as f:
                config_data = json.load(f)

            syntax = Syntax(json.dumps(config_data, indent=2), "json", theme="monokai")
            console.print(Panel(syntax, title="Configuration", border_style="cyan"))

@cli.command()
@click.confirmation_option(prompt="Are you sure you want to uninstall MoAI-ADK?")
def uninstall():
    """Uninstall MoAI-ADK and remove configuration"""

    console.print("[bold red]Uninstalling MoAI-ADK...[/bold red]\n")

    # Uninstall package
    if shutil.which("uv"):
        run_command(["uv", "pip", "uninstall", "-y", MOAI_PACKAGE], "Uninstalled MoAI-ADK package")

    # Remove config directory
    if MOAI_CONFIG_DIR.exists():
        if Confirm.ask(f"Remove configuration directory {MOAI_CONFIG_DIR}?", default=True):
            shutil.rmtree(MOAI_CONFIG_DIR)
            console.print(f"[green]✓[/green] Removed {MOAI_CONFIG_DIR}")

    console.print("\n[green]Uninstallation complete[/green]")

@cli.command("setup-korean")
def setup_korean_cmd():
    """Setup Korean language support"""

    console.print("[bold cyan]Korean Language Setup[/bold cyan]\n")

    if not MOAI_CONFIG_DIR.exists():
        console.print("[red]Error:[/red] MoAI-ADK not installed")
        console.print("Run: [cyan]uv run installer.py install[/cyan]")
        return

    setup_korean_support()
    console.print("\n[green]Korean language support configured[/green]")

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    cli()
