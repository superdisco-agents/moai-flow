# MOAI-ADK Installation Verification Checklist

## Pre-Installation Requirements

### System Prerequisites
- [ ] **Python 3.11+** verified
  ```bash
  python3 --version
  # Expected: Python 3.11.x or higher
  ```

- [ ] **Node.js** installed
  ```bash
  npx --version
  # Expected: 10.x.x or higher
  ```

- [ ] **Git** installed
  ```bash
  git --version
  # Expected: git version 2.x.x or higher
  ```

- [ ] **pip** package manager available
  ```bash
  pip3 --version
  # Expected: pip 23.x.x or higher
  ```

### Pre-Installation Check
- [ ] **Run pre-install check script**
  ```bash
  python3 _config/MOAI-ADK/scripts/pre-install-check.py
  ```
  - Verifies Python version
  - Checks Node.js availability
  - Detects existing installations
  - Identifies potential conflicts

- [ ] **Clean up conflicts** (if detected)
  ```bash
  python3 _config/MOAI-ADK/scripts/pre-install-check.py --clean
  ```
  - Removes conflicting packages
  - Backs up existing configurations
  - Prepares clean installation environment

---

## During Installation

### Virtual Environment Setup
- [ ] **Create virtual environment**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate  # On macOS/Linux
  # .venv\Scripts\activate   # On Windows
  ```

- [ ] **Verify virtual environment is active**
  ```bash
  which python3
  # Expected: /path/to/project/.venv/bin/python3
  ```

### MOAI-ADK Installation
- [ ] **Install from latest release**
  ```bash
  pip install moai-adk
  # Or for specific version:
  # pip install moai-adk==0.30.2
  ```

- [ ] **Install dependencies**
  ```bash
  pip install -r requirements.txt
  # Or if provided by MOAI-ADK:
  # moai-adk install-deps
  ```

### Configuration Generation
- [ ] **Generate configuration files**
  ```bash
  moai-adk init
  # Or manually run:
  # python3 _config/MOAI-ADK/scripts/generate-configs.py
  ```

- [ ] **Verify directory structure created**
  - `.moai/` directory exists
  - `.moai/config/` directory exists
  - `.claude/commands/moai/` directory exists

---

## Post-Installation Verification

### Core Commands Verification
- [ ] **Check MOAI-ADK version**
  ```bash
  moai-adk --version
  # Expected: v0.30.2 or higher
  ```

- [ ] **Run system health check**
  ```bash
  moai-adk doctor
  # Expected: All checks passed ✓
  ```

- [ ] **Display system status**
  ```bash
  moai-adk status
  # Expected: Installation info, config paths, MCP servers status
  ```

### Script Verification
- [ ] **Version check script works**
  ```bash
  python3 _config/MOAI-ADK/scripts/check-latest-version.py
  # Expected: Current version vs latest release comparison
  ```

- [ ] **MCP servers verification**
  ```bash
  python3 _config/MOAI-ADK/scripts/verify-mcp-servers.py
  # Expected: All 4 MCP servers verified ✓
  ```

- [ ] **Configuration validation**
  ```bash
  python3 _config/MOAI-ADK/scripts/validate-config.py
  # Expected: All configuration files valid ✓
  ```

- [ ] **Quick doctor check**
  ```bash
  python3 _config/MOAI-ADK/scripts/quick-doctor.py
  # Expected: Quick health check passed ✓
  ```

- [ ] **Pre-install check (post-install verification)**
  ```bash
  python3 _config/MOAI-ADK/scripts/pre-install-check.py
  # Expected: All checks passed, no conflicts detected ✓
  ```

### Claude Commands Verification
- [ ] **All 7 MOAI commands present** in `.claude/commands/moai/`:
  1. `/moai-init` - Initialize MOAI-ADK
  2. `/moai-status` - Show installation status
  3. `/moai-doctor` - Run health diagnostics
  4. `/moai-update` - Update to latest version
  5. `/moai-config` - Manage configuration
  6. `/moai-verify` - Verify MCP servers
  7. `/moai-help` - Display help information

- [ ] **Test a command**
  ```bash
  # In Claude Code, run:
  /moai-status
  # Expected: Status information displayed
  ```

### Configuration Files Verification
- [ ] **`.moai/config/config.json`** exists and contains:
  ```json
  {
    "version": "0.30.2",
    "installation_date": "YYYY-MM-DD",
    "mcp_servers": ["flow-nexus", "github", "gsheets", "sequential-thinking"],
    "features": {
      "swarm_coordination": true,
      "neural_patterns": true,
      "github_integration": true
    }
  }
  ```

- [ ] **`.mcp.json`** configured with 4 MCP servers:
  1. `flow-nexus` (Claude Flow coordination)
  2. `github` (GitHub integration)
  3. `gsheets` (Google Sheets integration)
  4. `sequential-thinking` (Enhanced reasoning)

- [ ] **`CLAUDE.md`** exists at project root
  - Contains MOAI-ADK instructions
  - References swarm coordination
  - Includes command documentation

### Directory Structure Verification
```
project-root/
├── .moai/
│   ├── config/
│   │   ├── config.json
│   │   └── mcp-servers.json
│   ├── logs/
│   └── cache/
├── .claude/
│   └── commands/
│       └── moai/
│           ├── moai-init.md
│           ├── moai-status.md
│           ├── moai-doctor.md
│           ├── moai-update.md
│           ├── moai-config.md
│           ├── moai-verify.md
│           └── moai-help.md
├── _config/
│   └── MOAI-ADK/
│       ├── scripts/
│       │   ├── check-latest-version.py
│       │   ├── verify-mcp-servers.py
│       │   ├── validate-config.py
│       │   ├── quick-doctor.py
│       │   └── pre-install-check.py
│       └── INSTALLATION-CHECKLIST.md (this file)
├── .mcp.json
└── CLAUDE.md
```

- [ ] **All directories created**
- [ ] **All files present**
- [ ] **Proper permissions set** (read/write/execute where needed)

---

## Quick Reference Commands

### 1. Check Latest Version
```bash
python3 _config/MOAI-ADK/scripts/check-latest-version.py

# Common flags:
--update          # Auto-update if newer version available
--verbose         # Show detailed version information
--json            # Output in JSON format
--check-only      # Only check, don't offer to update
```

### 2. Verify MCP Servers
```bash
python3 _config/MOAI-ADK/scripts/verify-mcp-servers.py

# Common flags:
--fix             # Attempt to fix configuration issues
--verbose         # Show detailed verification steps
--server <name>   # Verify specific server only
--json            # Output results in JSON format
```

### 3. Validate Configuration
```bash
python3 _config/MOAI-ADK/scripts/validate-config.py

# Common flags:
--fix             # Auto-fix common configuration issues
--strict          # Use strict validation rules
--output <file>   # Save validation report to file
--verbose         # Show detailed validation steps
```

### 4. Quick Doctor Check
```bash
python3 _config/MOAI-ADK/scripts/quick-doctor.py

# Common flags:
--full            # Run comprehensive health check
--fix             # Attempt to fix detected issues
--json            # Output results in JSON format
--quiet           # Only show errors and warnings
```

### 5. Pre-Install Check
```bash
python3 _config/MOAI-ADK/scripts/pre-install-check.py

# Common flags:
--clean           # Clean up conflicts automatically
--backup          # Backup existing configs before cleaning
--dry-run         # Show what would be cleaned without doing it
--verbose         # Show detailed conflict detection
```

---

## Common Installation Issues & Solutions

### Issue: Python version too old
**Solution:**
```bash
# macOS (using Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt-get install python3.11

# Verify installation
python3.11 --version
```

### Issue: Virtual environment not activating
**Solution:**
```bash
# Ensure you're using the correct activation script
source .venv/bin/activate        # macOS/Linux (bash/zsh)
source .venv/bin/activate.fish   # Fish shell
.venv\Scripts\activate.bat       # Windows CMD
.venv\Scripts\Activate.ps1       # Windows PowerShell
```

### Issue: MCP servers not recognized
**Solution:**
```bash
# Verify .mcp.json exists and is valid JSON
cat .mcp.json | python3 -m json.tool

# Re-run MCP server verification
python3 _config/MOAI-ADK/scripts/verify-mcp-servers.py --fix
```

### Issue: Commands not appearing in Claude Code
**Solution:**
```bash
# Verify command files exist
ls -la .claude/commands/moai/

# Restart Claude Code CLI
# Then test with: /moai-status
```

### Issue: Permission denied errors
**Solution:**
```bash
# Make scripts executable
chmod +x _config/MOAI-ADK/scripts/*.py

# Verify permissions
ls -la _config/MOAI-ADK/scripts/
```

---

## Upgrade Checklist

When upgrading MOAI-ADK to a newer version:

- [ ] **Backup current configuration**
  ```bash
  cp -r .moai .moai.backup
  cp .mcp.json .mcp.json.backup
  ```

- [ ] **Check for breaking changes**
  ```bash
  python3 _config/MOAI-ADK/scripts/check-latest-version.py --changelog
  ```

- [ ] **Run pre-upgrade check**
  ```bash
  python3 _config/MOAI-ADK/scripts/pre-install-check.py
  ```

- [ ] **Upgrade MOAI-ADK**
  ```bash
  pip install --upgrade moai-adk
  ```

- [ ] **Run post-upgrade verification**
  ```bash
  moai-adk doctor
  python3 _config/MOAI-ADK/scripts/validate-config.py
  ```

- [ ] **Test key functionality**
  - Run `/moai-status` in Claude Code
  - Verify MCP servers still working
  - Test swarm coordination features

---

## Support & Resources

### Documentation
- **Installation Guide**: `_config/MOAI-ADK/INSTALLATION.md`
- **Configuration Guide**: `.moai/config/README.md`
- **MCP Servers Guide**: `.mcp.json` comments

### Commands
- `/moai-help` - Get help within Claude Code
- `/moai-doctor` - Diagnose issues
- `/moai-status` - Check current status

### Scripts
All verification scripts are located in `_config/MOAI-ADK/scripts/`

### Community
- GitHub Issues: Report bugs and request features
- Documentation: Read detailed guides
- Examples: See `_config/MOAI-ADK/examples/`

---

## Completion Sign-Off

Installation is complete when:
- ✅ All pre-installation checks pass
- ✅ All post-installation verification steps pass
- ✅ All 7 MOAI commands work in Claude Code
- ✅ All 5 verification scripts execute successfully
- ✅ All 4 MCP servers are configured and verified
- ✅ `moai-adk doctor` reports no issues

**Installation Date:** _______________
**Installed Version:** _______________
**Verified By:** _______________

---

*Last Updated: 2025-11-28*
*MOAI-ADK Version: 0.30.2+*
