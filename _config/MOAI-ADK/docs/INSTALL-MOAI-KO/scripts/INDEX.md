# MOAI Korean Font Setup - Script Index

Complete index of all installation scripts and documentation.

## Quick Navigation

### Getting Started
- **New to setup?** Start with [QUICK-START.md](QUICK-START.md) (5 min read)
- **Want details?** Read [INSTALLATION-GUIDE.md](INSTALLATION-GUIDE.md) (20 min read)
- **Full documentation?** Check [README.md](README.md) (comprehensive reference)

### Run Installation
- **One-command setup:** `./setup-all.sh` (easiest)
- **Step-by-step:** Run scripts individually
- **Manual setup:** Follow INSTALLATION-GUIDE.md

---

## Files Overview

### Executable Scripts

#### 1. install-korean-fonts.sh
**Purpose:** Install Korean fonts from Homebrew  
**Duration:** 3-5 minutes  
**User Input:** Minimal (optional font selection)  
**Output:** Fonts installed in ~/Library/Fonts

```bash
./install-korean-fonts.sh
```

**What it does:**
- Checks macOS compatibility
- Installs/verifies Homebrew
- Adds fonts tap to Homebrew
- Installs Noto Sans/Serif CJK fonts
- Optionally installs terminal fonts (Meslo, Fira Code, Hack)
- Refreshes font cache
- Creates detailed log file

**Fonts installed:**
- Noto Sans CJK (sans serif)
- Noto Serif CJK (serif)
- Noto Mono (monospace)

**Optional terminal fonts:**
- Meslo LG Nerd Font
- Fira Code Nerd Font
- Hack Nerd Font

**Log file:** `install-korean-fonts.log`

---

#### 2. apply-ghostty-config.sh
**Purpose:** Configure Ghostty for Korean font support  
**Duration:** 1-2 minutes  
**User Input:** Required (font and size selection)  
**Output:** Ghostty configuration at ~/.config/ghostty/config

```bash
./apply-ghostty-config.sh
```

**What it does:**
- Verifies Ghostty installation
- Creates config directory if needed
- Backs up existing configuration
- Prompts for font selection (5 options)
- Prompts for font size (8-50pt)
- Generates optimized configuration
- Validates configuration syntax
- Optionally displays and restarts Ghostty

**Configuration created:**
- Font family selection
- Font size setting
- Font fallback chain
- Display settings (colors, padding, etc.)
- Terminal behavior (shell integration, etc.)
- Performance optimizations

**Output files:**
- `~/.config/ghostty/config` (main config)
- `~/.config/ghostty/config.backup.YYYYMMDD_HHMMSS` (automatic backup)

**Log file:** `apply-ghostty-config.log`

---

#### 3. verify-setup.sh
**Purpose:** Verify installation and configuration  
**Duration:** 30 seconds  
**User Input:** Optional (Korean text rendering test)  
**Output:** Color-coded status report with recommendations

```bash
./verify-setup.sh
```

**What it does:**
- Checks macOS version and architecture
- Verifies font directory accessibility
- Detects installed Korean fonts
- Checks Ghostty installation
- Validates configuration file presence
- Tests configuration content
- Optionally tests Korean text rendering
- Generates detailed verification report
- Provides actionable recommendations

**Verification checklist:**
- System environment (macOS version, architecture)
- Font directory (exists, writable)
- Font installation (Noto fonts found)
- Terminal fonts (optional, recommended)
- Ghostty installation
- Configuration file presence
- Font family configuration
- Font size configuration
- Fallback fonts
- Shell integration
- Korean text rendering

**Output report:**
- Total checks count
- Passed/failed/warning counts
- Overall status percentage
- Status indicator (READY/PARTIALLY READY/NEEDS ATTENTION)
- Actionable recommendations

**Log file:** `verify-setup.log`

---

#### 4. setup-all.sh
**Purpose:** Run all installation scripts in sequence  
**Duration:** 5-10 minutes  
**User Input:** Minimal (confirmation and font selection)  
**Output:** Complete setup with master log

```bash
./setup-all.sh
```

**What it does:**
- Checks all prerequisites
- Verifies script files exist
- Verifies executable permissions
- Runs all three scripts in sequence
- Displays progress with step counting
- Creates master log file
- Generates comprehensive summary
- Provides next steps and troubleshooting info

**Features:**
- Automatic script dependency checking
- Progress tracking (Step X/3)
- Error handling with recovery options
- Elapsed time calculation
- Detailed logging to `logs/setup-all.log`
- Summary with configuration file locations

**Log files:**
- `logs/setup-all.log` (master log)
- `install-korean-fonts.log`
- `apply-ghostty-config.log`
- `verify-setup.log`

---

### Documentation Files

#### QUICK-START.md
**Target Audience:** Users who want to get started immediately  
**Reading Time:** 5 minutes  
**Content:**
- 30-second overview
- Step-by-step instructions for each script
- What to expect at each stage
- Expected output examples
- Quick troubleshooting for common issues
- Performance tips
- Testing your setup
- Getting help section

**Use when:**
- You want the fastest path to setup
- You're experienced with terminal commands
- You prefer minimal reading

---

#### INSTALLATION-GUIDE.md
**Target Audience:** Users who want complete understanding  
**Reading Time:** 20 minutes  
**Content:**
- Detailed table of contents
- System requirements (minimum and recommended)
- Three installation methods (automated, step-by-step, manual)
- Detailed step-by-step instructions
- Extensive troubleshooting section
- Advanced configuration options
- Font customization guide
- Color scheme options
- Terminal behavior tweaking
- Performance tuning
- Verification procedures
- Reverting/uninstalling instructions
- Resources and support

**Use when:**
- You want to understand everything
- You're troubleshooting issues
- You want advanced customization
- You're new to Ghostty/macOS

---

#### README.md
**Target Audience:** Complete reference documentation  
**Reading Time:** 30+ minutes  
**Content:**
- Complete overview of all scripts
- Detailed feature descriptions
- Workflow recommendations
- Font information and options
- Configuration options
- Advanced features and tips
- Log file locations
- Performance considerations
- Security considerations
- Uninstallation instructions
- Version history
- Support and contribution info

**Use when:**
- You want comprehensive reference material
- You're building on top of these scripts
- You need to understand every detail
- You're documenting your setup

---

#### This File: INDEX.md
**Target Audience:** Everyone  
**Reading Time:** 5 minutes  
**Content:**
- Navigation guide
- File descriptions and purposes
- Quick reference table
- Usage recommendations

**Use when:**
- You need to find a specific document
- You're new to the package
- You want to understand what's available

---

## Quick Reference Table

| File | Type | Size | Purpose | Time |
|------|------|------|---------|------|
| install-korean-fonts.sh | Script | 10KB | Font installation | 3-5 min |
| apply-ghostty-config.sh | Script | 15KB | Ghostty configuration | 1-2 min |
| verify-setup.sh | Script | 16KB | Setup verification | 30 sec |
| setup-all.sh | Script | 11KB | Complete automated setup | 5-10 min |
| QUICK-START.md | Doc | 12KB | Fast start guide | 5 min read |
| INSTALLATION-GUIDE.md | Doc | 20KB | Complete guide | 20 min read |
| README.md | Doc | 12KB | Full documentation | 30 min read |
| INDEX.md | Doc | 5KB | This file | 5 min read |

---

## Usage Paths

### Path 1: Fastest Setup (5 minutes)
```
1. Read: QUICK-START.md (2 min)
2. Run: ./setup-all.sh (3 min)
3. Done!
```

### Path 2: Controlled Setup (8 minutes)
```
1. Read: QUICK-START.md (2 min)
2. Run: ./install-korean-fonts.sh (3 min)
3. Run: ./apply-ghostty-config.sh (2 min)
4. Run: ./verify-setup.sh (30 sec)
5. Done!
```

### Path 3: Complete Understanding (40 minutes)
```
1. Read: QUICK-START.md (5 min)
2. Read: INSTALLATION-GUIDE.md (20 min)
3. Run: ./setup-all.sh (10 min)
4. Read: README.md for reference (5 min)
5. Customize as needed
6. Done!
```

### Path 4: Troubleshooting (15 minutes)
```
1. Read: Relevant section in INSTALLATION-GUIDE.md (5 min)
2. Check logs: cat *.log (5 min)
3. Run: ./verify-setup.sh (30 sec)
4. Follow recommendations (5 min)
5. Done!
```

---

## Directory Structure

```
scripts/
├── install-korean-fonts.sh      (Executable script)
├── apply-ghostty-config.sh      (Executable script)
├── verify-setup.sh              (Executable script)
├── setup-all.sh                 (Executable script)
├── logs/                         (Created during setup)
│   ├── setup-all.log
│   ├── install-korean-fonts.log
│   ├── apply-ghostty-config.log
│   └── verify-setup.log
├── QUICK-START.md               (Quick reference)
├── INSTALLATION-GUIDE.md        (Complete guide)
├── README.md                    (Full documentation)
└── INDEX.md                     (This file)
```

---

## Common Tasks

### Task: Complete installation
**Best file:** QUICK-START.md  
**Run:** `./setup-all.sh`

### Task: Install fonts only
**Best file:** QUICK-START.md (Step 1)  
**Run:** `./install-korean-fonts.sh`

### Task: Configure Ghostty only
**Best file:** QUICK-START.md (Step 2)  
**Run:** `./apply-ghostty-config.sh`

### Task: Verify setup
**Best file:** QUICK-START.md (Step 3)  
**Run:** `./verify-setup.sh`

### Task: Troubleshoot
**Best file:** INSTALLATION-GUIDE.md (Troubleshooting section)  
**Check:** `cat *.log` for error messages

### Task: Customize fonts
**Best file:** INSTALLATION-GUIDE.md (Advanced Configuration)  
**Edit:** `nano ~/.config/ghostty/config`

### Task: Change font size
**Best file:** INSTALLATION-GUIDE.md (Font Size section)  
**Edit:** `nano ~/.config/ghostty/config`

### Task: Understand everything
**Best file:** README.md (complete reference)

### Task: Uninstall/Revert
**Best file:** INSTALLATION-GUIDE.md (Reverting Changes section)

---

## Getting Started

### First Time Users
1. Open Terminal: `Cmd+Space`, type "Terminal", press Enter
2. Navigate to scripts directory:
   ```bash
   cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/MOAI-ADK/docs/INSTALL-MOAI-KO/scripts
   ```
3. Choose your path above (Path 1 recommended for first-time)
4. Follow the instructions

### Experienced Users
1. Run: `./setup-all.sh` or `./install-korean-fonts.sh && ./apply-ghostty-config.sh && ./verify-setup.sh`
2. Check: Review logs if any issues
3. Test: Open Ghostty and test Korean text

### Troubleshooting
1. Read relevant section in INSTALLATION-GUIDE.md
2. Check logs: `cat *.log | grep ERROR`
3. Run: `./verify-setup.sh` for diagnostic report
4. Check config: `cat ~/.config/ghostty/config`

---

## Key Features

### Automation
- Automatic Homebrew installation if needed
- Automatic font cache refresh
- Automatic configuration backup
- Automatic error detection and reporting

### Safety
- Configuration backups created automatically
- Scripts can be run multiple times safely
- No system-wide changes (user-only)
- Reversible installation

### Usability
- Color-coded output for easy reading
- Detailed logging for troubleshooting
- Interactive prompts for customization
- Clear status indicators

### Reliability
- Comprehensive error handling
- Validation at each step
- Detailed verification script
- Complete logging system

---

## Support & Help

### Check Logs
```bash
# View logs
cat *.log

# Search for errors
grep ERROR *.log

# View specific log
cat verify-setup.log
```

### Run Diagnostic
```bash
./verify-setup.sh
```

### Read Documentation
- Quick answers: QUICK-START.md
- Detailed help: INSTALLATION-GUIDE.md
- Full reference: README.md

### Manual Configuration
```bash
# Edit config directly
nano ~/.config/ghostty/config

# View current config
cat ~/.config/ghostty/config

# Check installed fonts
ls ~/Library/Fonts | grep -i noto
```

---

## File Permissions

All scripts should be executable. If not:

```bash
# Make all scripts executable
chmod +x *.sh

# Verify
ls -la *.sh
# Should show: -rwxr-xr-x
```

---

## Version & Compatibility

- **Version:** 1.0.0
- **Last Updated:** November 28, 2025
- **Compatible macOS:** 10.13+ (Mojave or newer)
- **Recommended macOS:** 12.0+ (Monterey or newer)
- **Required Shell:** bash 4.0+
- **Package Manager:** Homebrew

---

## Next Steps

1. **Choose your path** from "Usage Paths" section above
2. **Read the appropriate documentation** (QUICK-START or INSTALLATION-GUIDE)
3. **Run the scripts** (setup-all.sh is easiest)
4. **Verify installation** with verify-setup.sh
5. **Enjoy Korean font support** in Ghostty!

---

**Questions?** Check the appropriate documentation file listed above.  
**Issues?** See Troubleshooting section in INSTALLATION-GUIDE.md.  
**Need details?** Read README.md for complete reference.

Good luck with your MOAI Korean setup!
