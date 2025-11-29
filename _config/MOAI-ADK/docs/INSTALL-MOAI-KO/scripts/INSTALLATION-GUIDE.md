# MOAI Korean Font & Ghostty Installation Guide

Complete installation guide for setting up Korean font support and Ghostty configuration on macOS.

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation Methods](#installation-methods)
4. [Detailed Instructions](#detailed-instructions)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Configuration](#advanced-configuration)

## Overview

This installation package provides automated scripts to:
- Install Korean fonts via Homebrew
- Configure Ghostty for optimal Korean text rendering
- Verify the complete setup with comprehensive testing

### What You'll Get

**Fonts:**
- Noto Sans CJK (sans serif with full Korean support)
- Noto Serif CJK (serif font with full Korean support)
- Noto Mono (monospace font)
- Optional: Meslo LG, Fira Code, Hack Nerd Fonts for terminals

**Configuration:**
- Optimized Ghostty config for Korean rendering
- Proper font fallback chains
- Display and terminal optimization
- Automatic backups of existing configs

**Verification:**
- System compatibility checks
- Font installation verification
- Configuration validation
- Korean text rendering test
- Detailed status reports

## System Requirements

### Minimum Requirements

- macOS 10.13 or later (Mojave or newer recommended)
- 500 MB free disk space for fonts
- bash 4.0 or later
- Internet connection for downloading fonts

### Recommended Specifications

- macOS 12.0 or later
- 1 GB available disk space
- Homebrew (script can install automatically)
- Ghostty installed (script checks for this)

### Check Your System

```bash
# Check macOS version
sw_vers -productVersion  # Should be 10.13+

# Check bash version
bash --version  # Should be 4.0+

# Check architecture
uname -m  # Should be arm64 or x86_64
```

## Installation Methods

### Method 1: Automated Complete Setup (Recommended)

Run everything in one command:

```bash
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/MOAI-ADK/docs/INSTALL-MOAI-KO/scripts
./setup-all.sh
```

**Time:** 5-10 minutes
**Interaction:** Minimal (font selection prompts)
**Best for:** First-time setup

### Method 2: Step-by-Step Installation

Run scripts individually for more control:

```bash
./install-korean-fonts.sh
./apply-ghostty-config.sh
./verify-setup.sh
```

**Time:** 5-8 minutes total
**Interaction:** Interactive (font/size selection)
**Best for:** Customization, debugging

### Method 3: Manual Installation

For advanced users who prefer manual setup:

```bash
# Install fonts via Homebrew
brew tap homebrew/cask-fonts
brew install --cask font-noto-sans-cjk
brew install --cask font-noto-serif-cjk
brew install --cask font-noto-mono

# Create Ghostty config
mkdir -p ~/.config/ghostty
echo "font-family = Noto Sans Mono CJK KR" > ~/.config/ghostty/config
echo "font-size = 12" >> ~/.config/ghostty/config
echo "font-fallback = AppleColorEmoji" >> ~/.config/ghostty/config
```

## Detailed Instructions

### Preparation

1. **Open Terminal**
   ```bash
   # macOS: Press Cmd+Space, type "Terminal", press Enter
   ```

2. **Navigate to Scripts Directory**
   ```bash
   cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/MOAI-ADK/docs/INSTALL-MOAI-KO/scripts
   ```

3. **Verify Scripts Exist**
   ```bash
   ls -la *.sh
   # Should show: install-korean-fonts.sh, apply-ghostty-config.sh, verify-setup.sh, setup-all.sh
   ```

4. **Make Scripts Executable** (if not already)
   ```bash
   chmod +x *.sh
   ```

### Using setup-all.sh (Easiest)

**Step 1: Run Setup Script**
```bash
./setup-all.sh
```

**Step 2: Answer Prompts**

When asked "Continue with installation?":
- Type `y` and press Enter to proceed
- Type `n` and press Enter to cancel

**Step 3: Make Font Selection**

When prompted:
```
Select a font (1-5):
  1. Noto Sans Mono CJK KR      <- Best for Korean
  2. Noto Serif CJK KR
  3. Meslo LG M Nerd Font Mono
  4. Fira Code Nerd Font
  5. Hack Nerd Font Mono
```

Enter the number (1-5) and press Enter. Recommended: **1**

**Step 4: Select Font Size**

When prompted:
```
Enter font size (default: 12):
```

- For Retina/High DPI displays: Enter `10` or `11`
- For regular displays: Enter `12` or `13` (press Enter for default)
- For accessibility: Enter `14` or higher

**Step 5: Review Configuration**

When asked "Display configuration?":
- Type `y` to see the generated config
- Type `n` to skip

**Step 6: Restart Ghostty**

When asked "Restart Ghostty?":
- Type `y` to automatically close and restart Ghostty
- Type `n` if you'll restart manually

**Step 7: Wait for Completion**

The script will:
- Install fonts (3-5 minutes)
- Configure Ghostty (1-2 minutes)
- Verify setup (30 seconds)
- Display final summary

### Using Individual Scripts

**Step 1: Install Fonts**
```bash
./install-korean-fonts.sh
```

What to expect:
```
✓ Running on macOS
✓ Homebrew is installed
? Install optional terminal fonts? (y/n):
  Type 'y' for Meslo, Fira Code, Hack fonts (recommended)
  Type 'n' to skip optional fonts
✓ Font installation complete
```

**Step 2: Configure Ghostty**
```bash
./apply-ghostty-config.sh
```

What to expect:
```
ℹ Setting up Ghostty configuration directory...
✓ Created directory: ~/.config/ghostty

Select a font (1-5):
  1. Noto Sans Mono CJK KR
  [... choose your font ...]

Enter font size (default: 12):
  [... enter or press Enter ...]

✓ Configuration generated successfully
? Display configuration? (y/n):
? Restart Ghostty? (y/n):
```

**Step 3: Verify Setup**
```bash
./verify-setup.sh
```

What to expect:
```
ℹ macOS version: 14.2
✓ Running on macOS
✓ Font directory exists

✓ Found: Noto Sans Mono CJK
✓ Found: Noto Serif CJK
✓ Ghostty is installed
✓ Configuration file found

Sample Korean text:
안녕하세요 - Hello (Korean)
こんにちは - Hello (Japanese)

? Does the Korean text display correctly? (y/n):

✓ Checks Passed: 15/15
Overall Status: 100%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Setup Status: READY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Troubleshooting

### Common Issues & Solutions

#### Issue: "Ghostty is not installed"

**Problem:** Script cannot find Ghostty

**Solution:**
```bash
# Check if Ghostty is installed
ghostty --version

# If not installed, install via Homebrew
brew install ghostty

# If Homebrew installation fails, install from source:
git clone https://github.com/ghostty-org/ghostty.git
cd ghostty
./zig build -Doptimize=ReleaseFast
```

#### Issue: "Homebrew is not installed"

**Problem:** Homebrew is required for font installation

**Solution:**
```bash
# Let the script install it automatically
# Or manually:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# After installation, verify
brew --version
```

#### Issue: "Font directory not writable"

**Problem:** Permission denied when installing fonts

**Solution:**
```bash
# Check permissions
ls -la ~/Library/Fonts

# Fix if needed
chmod 755 ~/Library/Fonts

# If still failing, use sudo carefully:
sudo chown $USER ~/Library/Fonts
```

#### Issue: Korean text displays as boxes/squares

**Problem:** Fonts not properly installed or not selected in config

**Solutions:**

1. **Verify font installation:**
   ```bash
   ls ~/Library/Fonts | grep -i noto
   # Should show files like: NotoSansCJKkr-Regular.otf
   ```

2. **Refresh font cache:**
   ```bash
   fc-cache -fv
   ```

3. **Restart Ghostty:**
   ```bash
   killall ghostty
   # Then reopen Ghostty
   ```

4. **Check Ghostty config:**
   ```bash
   cat ~/.config/ghostty/config | grep font-family
   # Should see: font-family = Noto Sans Mono CJK KR (or similar)
   ```

5. **Re-run configuration:**
   ```bash
   ./apply-ghostty-config.sh
   ```

#### Issue: Fonts appear blurry or pixelated

**Problem:** Incorrect font size or display scaling

**Solutions:**

1. **Try different font size:**
   ```bash
   nano ~/.config/ghostty/config
   # Change: font-size = 12
   # Try: font-size = 11 or font-size = 13
   ```

2. **Check display resolution:**
   ```bash
   system_profiler SPDisplaysDataType
   ```

3. **For Retina displays:**
   - Use smaller font sizes (10-11pt)
   - Disable font smoothing if needed

4. **Restart Ghostty** after changes

#### Issue: Script permissions denied

**Problem:** Scripts not executable

**Solution:**
```bash
# Make all scripts executable
chmod +x *.sh

# Verify
ls -la *.sh
# Should show: -rwxr-xr-x (executable)
```

#### Issue: Installation takes too long

**Problem:** Slow internet or large file downloads

**Solutions:**

1. **Check internet connection:**
   ```bash
   ping -c 3 github.com
   ```

2. **Improve download speed:**
   - Close other applications
   - Use a faster network connection
   - Try installing later during off-peak hours

3. **Resume interrupted installation:**
   ```bash
   # Re-run the script - it will resume
   ./install-korean-fonts.sh
   ```

#### Issue: "Configuration file not found" or "No existing config"

**Problem:** Ghostty config doesn't exist yet

**Solution:** This is normal for first-time setup
```bash
# The script will create config for you
./apply-ghostty-config.sh

# Or manually create
mkdir -p ~/.config/ghostty
touch ~/.config/ghostty/config
```

### Getting More Help

**Check Log Files:**
```bash
# View all logs
cat *.log

# View specific log
cat install-korean-fonts.log
cat apply-ghostty-config.log
cat verify-setup.log

# Search for errors
grep ERROR *.log
grep WARNING *.log
```

**Run with Verbose Output:**
```bash
# Run script with bash debugging
bash -x ./install-korean-fonts.sh

# This shows every command being executed
```

**Test Korean Text Rendering:**
```bash
# In Ghostty, type or paste:
echo "안녕하세요"
echo "한글 테스트"
echo "😀 🎉 🚀"
```

If text displays correctly, fonts are working.

## Advanced Configuration

### Customizing Font Settings

**Edit Configuration File:**
```bash
nano ~/.config/ghostty/config
```

**Change Font Family:**
```
font-family = Noto Serif CJK KR  # Use serif font
font-family = Meslo LG M Nerd Font Mono  # Use terminal font
```

**Change Font Size:**
```
font-size = 11  # Smaller
font-size = 14  # Larger
font-size = 18  # Large (accessibility)
```

**Enable Font Features:**
```
font-feature = calt    # Contextual alternates
font-feature = liga    # Ligatures (code ligatures)
font-feature = ss02    # Stylistic set 2
```

### Color Scheme Customization

**Dark Theme (Default):**
```
background = #1e1e2e
foreground = #cdd6f4
cursor-color = #89b4fa
selection-background = #45475a40
```

**Light Theme:**
```
background = #fffaf3
foreground = #3c3c3c
cursor-color = #007aff
selection-background = #d4d4d440
```

**Custom Colors:**
```bash
# Edit ~/.config/ghostty/config and set:
background = #0a0e27    # Your background color
foreground = #d5d8df    # Your text color
cursor-color = #ff6f42  # Cursor color
```

### Terminal Behavior

**Enable Shell Integration:**
```
shell-integration = true
shell-integration-features = sudo,title
```

**Copy on Select:**
```
copy-on-select = true   # Auto-copy selected text
```

**Scrollback Buffer:**
```
scrollback-limit = 10000     # Number of lines to keep
scrollback-multiplier = 3    # Multiplier for scrollback
```

**Keybindings:**
```
keybind = global:super+n=new_window
keybind = global:super+t=new_tab
keybind = super+w=close_surface
keybind = super+cmd+i=increase_font_size
keybind = super+cmd+d=decrease_font_size
```

### Performance Tuning

**For Development:**
```
scrollback-limit = 50000
copy-on-select = false
animation = false
```

**For Minimal Resource Usage:**
```
scrollback-limit = 5000
animation = false
tab-bar = false
```

## Verifying Your Installation

### Verification Checklist

- [ ] All scripts executed without errors
- [ ] Fonts installed in ~/Library/Fonts
- [ ] Ghostty config created at ~/.config/ghostty/config
- [ ] Ghostty launches with new configuration
- [ ] Korean text displays correctly
- [ ] Font appears crisp and clear
- [ ] No performance issues
- [ ] ./verify-setup.sh shows "READY"

### Testing Korean Text

**Test 1: Basic Korean**
```bash
echo "안녕하세요"  # Hello
echo "한글"       # Korean
```

**Test 2: Mixed Text**
```bash
echo "Hello 안녕 World"
echo "你好 こんにちは مرحبا"
```

**Test 3: Emoji Support**
```bash
echo "😀 🎉 🚀 🌍"
```

**Test 4: Font Rendering**
```bash
ls -la ~
# Check that output displays clearly and correctly
```

All should display correctly with proper alignment.

## Reverting Changes

### Restore Previous Configuration

```bash
# List backups
ls -la ~/.config/ghostty/config.backup.*

# Restore most recent
cp ~/.config/ghostty/config.backup.* ~/.config/ghostty/config

# Restart Ghostty
killall ghostty
```

### Remove Installed Fonts

```bash
# Via Homebrew
brew uninstall --cask font-noto-sans-cjk
brew uninstall --cask font-noto-serif-cjk
brew uninstall --cask font-noto-mono

# Or manually delete files
rm -rf ~/Library/Fonts/NotoSans*.otf
rm -rf ~/Library/Fonts/NotoSerif*.otf
rm -rf ~/Library/Fonts/NotoMono*.otf
```

### Clean Up Installation Files

```bash
# Remove logs
rm -rf logs/

# Remove backup configs
rm ~/.config/ghostty/config.backup.*

# Keep scripts for future use or delete them
rm *.sh  # Only if you want to remove scripts
```

## Next Steps

After successful installation:

1. **Customize Font Size**
   - Edit ~/.config/ghostty/config
   - Adjust font-size to your preference

2. **Choose Color Scheme**
   - Add custom colors to config
   - Try different theme combinations

3. **Set Up Shell Integration**
   - Enable shell-integration in config
   - Enhance terminal functionality

4. **Configure Keybindings**
   - Add custom keybindings
   - Improve workflow efficiency

5. **Install Terminal Tools**
   - tmux or zellij for multiplexing
   - Oh My Zsh for better shell
   - Starship for prompt customization

## Resources

### Documentation
- [Ghostty Official Docs](https://github.com/ghostty-org/ghostty)
- [Noto Fonts](https://fonts.google.com/noto)
- [Homebrew Cask Fonts](https://github.com/Homebrew/homebrew-cask-fonts)

### Related Guides
- QUICK-START.md - Quick reference guide
- README.md - Complete documentation

### Community
- GitHub Issues: Report bugs or request features
- Stack Overflow: Tag with [ghostty] for questions

## Support

### Getting Help

1. **Review Log Files**
   ```bash
   cat *.log | grep ERROR
   ```

2. **Run Verification**
   ```bash
   ./verify-setup.sh
   ```

3. **Check Configuration**
   ```bash
   cat ~/.config/ghostty/config
   ```

4. **Test Rendering**
   ```bash
   echo "안녕하세요"
   ```

5. **Consult Documentation**
   - QUICK-START.md for quick answers
   - README.md for detailed information
   - Script comments for implementation details

## Appendix

### Script Descriptions

| Script | Purpose | Duration |
|--------|---------|----------|
| install-korean-fonts.sh | Install fonts via Homebrew | 3-5 min |
| apply-ghostty-config.sh | Configure Ghostty | 1-2 min |
| verify-setup.sh | Verify installation | 30 sec |
| setup-all.sh | Run all scripts | 5-10 min |

### Font Information

| Font | Type | Use Case |
|------|------|----------|
| Noto Sans CJK | Sans Serif | General use, web, UI |
| Noto Serif CJK | Serif | Documents, reading |
| Noto Mono | Monospace | Coding, terminal |
| Meslo LG Nerd Font | Monospace | Terminal, coding, glyphs |
| Fira Code Nerd Font | Monospace | Code, ligatures |
| Hack Nerd Font | Monospace | Terminal, minimal |

### Recommended Font Sizes

| DPI | Size |
|-----|------|
| High (Retina) | 10-11pt |
| Regular | 12-14pt |
| Low DPI | 14-16pt |
| Accessibility | 16-18pt |

---

**Version:** 1.0.0  
**Last Updated:** November 28, 2025  
**Tested on:** macOS 12.0+  
**Required:** bash 4.0+
