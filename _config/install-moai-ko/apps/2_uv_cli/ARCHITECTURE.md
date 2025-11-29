# MoAI-ADK UV CLI Installer Architecture

Deep technical documentation of the installer's architecture, design patterns, and implementation details.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Design Patterns](#design-patterns)
3. [Data Flow](#data-flow)
4. [Component Architecture](#component-architecture)
5. [Korean Language Integration](#korean-language-integration)
6. [Error Handling Strategy](#error-handling-strategy)
7. [Performance Optimization](#performance-optimization)
8. [Security Considerations](#security-considerations)

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Entry Point                       │
│                   (Click Framework)                      │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│   Commands   │          │   Utilities  │
│              │          │              │
│ • install    │          │ • logging    │
│ • verify     │◄────────►│ • sys_info   │
│ • status     │          │ • validation │
│ • uninstall  │          │ • prompts    │
│ • setup-ko   │          └──────┬───────┘
└──────┬───────┘                 │
       │                         │
       ▼                         ▼
┌──────────────────────────────────────┐
│        Core Installation Logic       │
│                                      │
│  • UV Installation                   │
│  • MoAI-ADK Installation            │
│  • Korean Language Setup            │
│  • Verification & Validation        │
└──────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│         Rich UI Rendering            │
│                                      │
│  • Console Output                    │
│  • Tables & Panels                   │
│  • Progress Bars                     │
│  • Interactive Prompts               │
└──────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| CLI Framework | Click 8.1+ | Command-line interface structure |
| UI Library | Rich 13.0+ | Terminal output formatting |
| Dependency Management | UV + PEP 723 | Single-file script dependencies |
| Package Installation | UV pip | Fast Python package installation |
| Configuration | JSON | Settings and locale configuration |
| Shell Integration | Bash/Zsh | Environment activation scripts |

### File Structure

```
installer.py (700 lines)
├── Header & Dependencies (PEP 723)     [20 lines]
├── Configuration & Constants           [30 lines]
├── Data Classes                        [50 lines]
│   ├── SystemInfo                      [15 lines]
│   ├── InstallationConfig              [10 lines]
│   └── InstallationStatus              [10 lines]
├── Utility Functions                   [100 lines]
│   ├── setup_logging()                 [10 lines]
│   ├── log_message()                   [15 lines]
│   ├── get_system_info()               [40 lines]
│   ├── check_python_version()          [15 lines]
│   └── run_command()                   [20 lines]
├── Installation Functions              [200 lines]
│   ├── install_uv()                    [60 lines]
│   ├── create_moai_directory()         [30 lines]
│   ├── install_moai_adk()              [40 lines]
│   └── verify_installation()           [20 lines]
├── Korean Language Support             [150 lines]
│   ├── install_korean_fonts_macos()    [30 lines]
│   ├── install_korean_fonts_linux()    [40 lines]
│   ├── configure_korean_locale()       [30 lines]
│   └── setup_korean_support()          [50 lines]
├── Post-Installation                   [50 lines]
│   ├── create_activation_script()      [25 lines]
│   └── display_next_steps()            [25 lines]
└── CLI Commands                        [300 lines]
    ├── cli() - main group              [10 lines]
    ├── install()                       [100 lines]
    ├── verify()                        [50 lines]
    ├── status()                        [50 lines]
    ├── uninstall()                     [40 lines]
    └── setup_korean_cmd()              [30 lines]
```

## Design Patterns

### 1. Command Pattern (Click CLI)

**Implementation:**
```python
@click.group()
@click.version_option(VERSION)
def cli():
    """Main command group"""
    setup_logging()

@cli.command()
@click.option("--korean", "-k", is_flag=True)
def install(korean):
    """Install command"""
    # Implementation
```

**Benefits:**
- Modular command structure
- Consistent option handling
- Built-in help generation
- Version management

### 2. Data Class Pattern

**Implementation:**
```python
@dataclass
class SystemInfo:
    os_type: str
    os_version: str
    architecture: str
    python_version: str
    # ... more fields

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
```

**Benefits:**
- Type safety
- Immutability
- Automatic `__init__` generation
- Easy serialization

### 3. Strategy Pattern (Platform-Specific Installation)

**Implementation:**
```python
def setup_korean_support() -> bool:
    system = get_system_info()

    strategies = {
        "Darwin": install_korean_fonts_macos,
        "Linux": install_korean_fonts_linux,
        "Windows": lambda: console.print("[yellow]Not supported[/yellow]")
    }

    strategy = strategies.get(system.os_type)
    if strategy:
        return strategy()
```

**Benefits:**
- Platform abstraction
- Extensible to new platforms
- Clean conditional logic

### 4. Builder Pattern (Configuration)

**Implementation:**
```python
config = InstallationConfig(
    install_korean_fonts=korean,
    skip_python_check=skip_python,
    force_reinstall=force,
    verbose=verbose
)
```

**Benefits:**
- Flexible configuration
- Clear parameter naming
- Easy to extend

### 5. Template Method Pattern (Installation Flow)

**Implementation:**
```python
def install(korean, skip_python, force, verbose):
    # Template method
    config = create_config(korean, skip_python, force, verbose)
    display_system_info()
    confirm_installation()

    # Hooks
    check_python_version()
    create_moai_directory(config)
    install_uv(config)
    install_moai_adk(config)
    verify_installation()

    if config.install_korean_fonts:
        setup_korean_support()

    create_activation_script()
    display_next_steps()
```

**Benefits:**
- Consistent installation flow
- Easy to add/remove steps
- Clear sequence

## Data Flow

### Installation Data Flow

```
User Input (CLI flags)
    │
    ▼
┌──────────────────┐
│ Parse Arguments  │
│  (Click)         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Create Config    │
│ InstallationConf │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Gather System    │
│ Info             │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Auto-detect      │
│ Korean Locale    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Interactive      │
│ Prompts          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Execute Install  │
│ Steps            │
└────────┬─────────┘
         │
         ├─► Create Directory
         ├─► Install UV
         ├─► Install MoAI-ADK
         ├─► Verify Installation
         ├─► Setup Korean (optional)
         └─► Create Activation Script
         │
         ▼
┌──────────────────┐
│ Display Results  │
│  (Rich UI)       │
└──────────────────┘
```

### Korean Language Auto-Detection Flow

```
System Locale Check
    │
    ├─► Read LANG environment variable
    ├─► Read LC_ALL environment variable
    └─► Check platform locale settings
    │
    ▼
Locale Analysis
    │
    ├─► Starts with "ko_"?
    ├─► Contains "KR"?
    └─► Contains "Korea"?
    │
    ▼
Korean Detection Result
    │
    ├─► is_korean = True
    │       │
    │       ▼
    │   Interactive Prompt:
    │   "Korean locale detected. Install Korean support?"
    │       │
    │       ├─► Yes → install_korean_fonts = True
    │       └─► No  → install_korean_fonts = False
    │
    └─► is_korean = False
            │
            └─► Skip Korean prompt
```

## Component Architecture

### 1. System Information Component

**Purpose:** Gather comprehensive system details

**Data Structure:**
```python
SystemInfo
├── os_type: str          # "Darwin", "Linux", "Windows"
├── os_version: str       # "23.0.0"
├── architecture: str     # "arm64", "x86_64"
├── python_version: str   # "3.11.5"
├── python_executable: str # "/usr/bin/python3"
├── disk_space_mb: int    # 45000
├── has_uv: bool         # True/False
├── uv_version: str      # "0.1.0"
├── locale: str          # "ko_KR.UTF-8"
└── is_korean: bool      # True/False
```

**Implementation:**
```python
def get_system_info() -> SystemInfo:
    os_type = platform.system()
    os_version = platform.version()
    architecture = platform.machine()

    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    python_executable = sys.executable

    stat = shutil.disk_usage(Path.home())
    disk_space_mb = stat.free // (1024 * 1024)

    has_uv = shutil.which("uv") is not None
    uv_version = get_uv_version() if has_uv else None

    locale = os.environ.get("LANG", "en_US.UTF-8")
    is_korean = locale.startswith("ko_") or "KR" in locale

    return SystemInfo(...)
```

### 2. Installation Configuration Component

**Purpose:** Manage installation options

**Data Structure:**
```python
InstallationConfig
├── install_korean_fonts: bool  # Default: False
├── skip_python_check: bool     # Default: False
├── skip_uv_install: bool       # Default: False
├── force_reinstall: bool       # Default: False
└── verbose: bool               # Default: False
```

**Configuration Builder:**
```python
def create_config(korean, skip_python, skip_uv, force, verbose) -> InstallationConfig:
    return InstallationConfig(
        install_korean_fonts=korean,
        skip_python_check=skip_python,
        skip_uv_install=skip_uv,
        force_reinstall=force,
        verbose=verbose
    )
```

### 3. UV Installation Component

**Purpose:** Install UV package manager

**Flow:**
```
Check if UV exists
    │
    ├─► Yes + not force_reinstall
    │       │
    │       └─► Skip installation
    │
    └─► No or force_reinstall
            │
            ▼
        Download installer script
            │
            ▼
        Execute installer via shell
            │
            ▼
        Add UV to PATH
            │
            ▼
        Display PATH instructions
```

**Implementation:**
```python
def install_uv(config: InstallationConfig) -> bool:
    system = get_system_info()

    if system.has_uv and not config.force_reinstall:
        return True  # Already installed

    # Download installer
    curl_cmd = ["curl", "-LsSf", "https://astral.sh/uv/install.sh"]
    result = subprocess.run(curl_cmd, capture_output=True, text=True)

    # Run installer
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
        # Success
        display_path_instructions()
        return True
    else:
        # Failure
        return False
```

### 4. MoAI-ADK Installation Component

**Purpose:** Install MoAI-ADK package

**Flow:**
```
Check UV availability
    │
    ▼
Build install command
    │
    ├─► Base: uv pip install
    └─► Add --force-reinstall if config.force_reinstall
    │
    ▼
Execute with progress bar
    │
    ▼
Verify installation
    │
    └─► Import moai_adk and check version
```

**Implementation:**
```python
def install_moai_adk(config: InstallationConfig) -> bool:
    if not shutil.which("uv"):
        return False

    cmd = ["uv", "pip", "install"]

    if config.force_reinstall:
        cmd.append("--force-reinstall")

    cmd.append(MOAI_PACKAGE)

    with Progress(...) as progress:
        task = progress.add_task("Installing MoAI-ADK...", total=None)

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        progress.update(task, completed=100)

    return True
```

### 5. Korean Language Component

**Purpose:** Setup Korean fonts and locale

**Architecture:**
```
Korean Language Support
│
├── Font Installation
│   ├── macOS Strategy
│   │   └── Homebrew casks
│   │       ├── font-nanum
│   │       └── font-nanum-gothic-coding
│   │
│   └── Linux Strategy
│       ├── apt-get (Ubuntu/Debian)
│       │   └── fonts-nanum
│       ├── yum (Fedora/RHEL)
│       │   └── google-noto-sans-cjk
│       └── pacman (Arch)
│           └── noto-fonts-cjk
│
└── Locale Configuration
    └── Create settings.json
        ├── language: ko_KR
        ├── locale: ko_KR.UTF-8
        ├── ui.font_family: Nanum Gothic
        └── features.korean_nlp: true
```

**Implementation:**
```python
def setup_korean_support() -> bool:
    system = get_system_info()

    # Platform-specific font installation
    if system.os_type == "Darwin":
        install_korean_fonts_macos()
    elif system.os_type == "Linux":
        install_korean_fonts_linux()

    # Universal locale configuration
    configure_korean_locale()

    return True

def install_korean_fonts_macos() -> bool:
    fonts = ["font-nanum", "font-nanum-gothic-coding"]

    for font in fonts:
        run_command(
            ["brew", "install", "--cask", font],
            f"Installed {font}"
        )

    return True

def configure_korean_locale() -> bool:
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

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(korean_config, f, indent=2, ensure_ascii=False)

    return True
```

## Korean Language Integration

### Auto-Detection Logic

**Detection Priority:**
1. `LANG` environment variable
2. `LC_ALL` environment variable
3. System locale settings

**Detection Algorithm:**
```python
def detect_korean_locale() -> bool:
    locale = os.environ.get("LANG", "en_US.UTF-8")

    # Check for Korean indicators
    korean_indicators = ["ko_", "KR", "Korea", "korean"]

    for indicator in korean_indicators:
        if indicator in locale:
            return True

    return False
```

### Interactive Korean Prompt

**User Experience Flow:**
```
System locale: ko_KR.UTF-8
    │
    ▼
is_korean = True
    │
    ▼
Display prompt:
┌────────────────────────────────────────┐
│ Korean locale detected.                │
│ Install Korean support? [Y/n]:        │
└────────────────────────────────────────┘
    │
    ├─► User enters 'y' or 'Y' or <Enter>
    │       │
    │       └─► install_korean_fonts = True
    │
    └─► User enters 'n' or 'N'
            │
            └─► install_korean_fonts = False
```

### Korean Font Selection by Platform

| Platform | Font Package | Installation Method |
|----------|--------------|---------------------|
| macOS | font-nanum | Homebrew cask |
| macOS | font-nanum-gothic-coding | Homebrew cask |
| Ubuntu/Debian | fonts-nanum | apt-get |
| Ubuntu/Debian | fonts-nanum-coding | apt-get |
| Fedora/RHEL | google-noto-sans-cjk-ttc-fonts | yum |
| Arch Linux | noto-fonts-cjk | pacman |

## Error Handling Strategy

### Error Hierarchy

```
Installation Errors
│
├── System Errors
│   ├── Insufficient disk space
│   ├── Missing Python version
│   └── Network connectivity issues
│
├── Dependency Errors
│   ├── UV installation failure
│   ├── MoAI-ADK installation failure
│   └── Korean font installation failure
│
├── Configuration Errors
│   ├── Directory creation failure
│   ├── Permission denied
│   └── File write errors
│
└── Validation Errors
    ├── Import verification failure
    └── Version mismatch
```

### Error Handling Patterns

**1. Graceful Degradation:**
```python
def setup_korean_support() -> bool:
    try:
        install_korean_fonts()
    except Exception as e:
        console.print(f"[yellow]Warning:[/yellow] {e}")
        # Continue without Korean fonts

    configure_korean_locale()
    return True
```

**2. Retry Logic:**
```python
def install_with_retry(package, max_retries=3):
    for attempt in range(max_retries):
        try:
            subprocess.run(["uv", "pip", "install", package], check=True)
            return True
        except subprocess.CalledProcessError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return False
```

**3. User Feedback:**
```python
def run_command(cmd, description):
    try:
        subprocess.run(cmd, check=True)
        console.print(f"[green]✓[/green] {description}")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗[/red] {description}")
        console.print(f"[red]Error:[/red] {e}")
        return False
```

## Performance Optimization

### 1. Lazy Loading

```python
# Don't import heavy libraries at module level
def install_moai_adk():
    # Import only when needed
    from rich.progress import Progress
    with Progress() as progress:
        # Installation code
```

### 2. Subprocess Optimization

```python
# Use capture_output for better performance
subprocess.run(cmd, capture_output=True, text=True)

# vs slower alternative
subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
```

### 3. Parallel Operations

```python
# Future enhancement: parallel downloads
from concurrent.futures import ThreadPoolExecutor

def install_multiple_packages(packages):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(install_package, pkg) for pkg in packages]
        return all(f.result() for f in futures)
```

## Security Considerations

### 1. Input Validation

```python
def validate_path(path: str) -> bool:
    # Prevent directory traversal
    abs_path = Path(path).resolve()
    return abs_path.is_relative_to(Path.home())
```

### 2. Subprocess Safety

```python
# Use list-based commands (prevents shell injection)
subprocess.run(["uv", "pip", "install", package])  # Safe

# Avoid string-based commands
# subprocess.run(f"uv pip install {package}", shell=True)  # Unsafe
```

### 3. File Permissions

```python
def create_activation_script():
    script = MOAI_CONFIG_DIR / "activate.sh"

    with open(script, "w") as f:
        f.write(content)

    # Set secure permissions
    script.chmod(0o755)  # rwxr-xr-x
```

### 4. Secrets Management

```python
# Never log sensitive data
log_message("INFO", f"Installing {MOAI_PACKAGE}")
# Don't log API keys, tokens, passwords
```

## Extension Points

### Adding New Commands

```python
@cli.command()
@click.option("--option", "-o")
def new_command(option):
    """New command description"""
    # Implementation
```

### Adding New Platforms

```python
def install_korean_fonts_windows() -> bool:
    # Windows font installation logic
    pass

# Register in strategy map
strategies = {
    "Darwin": install_korean_fonts_macos,
    "Linux": install_korean_fonts_linux,
    "Windows": install_korean_fonts_windows  # New
}
```

### Adding New Languages

```python
def detect_language() -> str:
    locale = os.environ.get("LANG", "en_US.UTF-8")

    language_map = {
        "ko_": "korean",
        "ja_": "japanese",
        "zh_": "chinese"
    }

    for prefix, lang in language_map.items():
        if locale.startswith(prefix):
            return lang

    return "english"
```

## Testing Strategy

See [test_installer.sh](./test_installer.sh) for implementation.

**Test Categories:**
1. Unit tests for individual functions
2. Integration tests for complete installation flow
3. Platform-specific tests
4. Korean language detection tests
5. Error handling tests

## Future Enhancements

1. **Plugin System:** Allow third-party extensions
2. **Configuration Profiles:** Save/load installation presets
3. **Rollback Capability:** Undo installations
4. **Update Management:** Check for newer versions
5. **Telemetry:** Anonymous usage statistics
6. **Multi-language Support:** Beyond Korean
