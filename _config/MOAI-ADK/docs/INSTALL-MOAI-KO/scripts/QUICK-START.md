# MOAI Korean Setup - Quick Start Guide

Get Korean font support in Ghostty running in 5 minutes.

## 30-Second Overview

```bash
cd /path/to/scripts
./install-korean-fonts.sh    # Install fonts (3-5 min)
./apply-ghostty-config.sh    # Configure Ghostty (1-2 min)
./verify-setup.sh            # Verify everything works (30 sec)
```

## Prerequisites Check

Before running scripts, verify:

```bash
# Check macOS version (10.13+)
sw_vers -productVersion

# Check if Homebrew is installed (optional - script installs if missing)
brew --version

# Check Ghostty installation
ghostty --version
```

## Step-by-Step Installation

### Step 1: Install Korean Fonts (3-5 minutes)

```bash
./install-korean-fonts.sh
```

**What happens:**
- Checks macOS compatibility
- Installs/verifies Homebrew
- Installs Noto Sans/Serif CJK fonts
- Optionally installs terminal fonts (Meslo, Fira Code, Hack)
- Refreshes font cache
- Creates installation log

**Questions you'll be asked:**
- Install Homebrew? (yes/no)
- Install optional terminal fonts? (yes/no for each)

**What to look for:**
- Green checkmarks (✓) for successful installs
- Yellow warnings (⚠) are usually OK to ignore
- Red errors (✗) indicate problems to fix

**Typical output:**
```
✓ Running on macOS
✓ Homebrew is installed
✓ Fonts tap already configured
✓ Noto Sans CJK installed successfully
✓ Noto Serif CJK installed successfully
✓ Noto Mono installed successfully
✓ All required fonts are installed
✓ Font cache refreshed
```

### Step 2: Configure Ghostty (1-2 minutes)

```bash
./apply-ghostty-config.sh
```

**What happens:**
- Verifies Ghostty is installed
- Creates/backs up config directory
- Prompts for font selection
- Prompts for font size
- Generates optimized configuration
- Validates configuration
- Optionally displays and restarts Ghostty

**Questions you'll be asked:**
```
? Select a font (1-5):
  1. Noto Sans Mono CJK KR      <- Recommended for Korean
  2. Noto Serif CJK KR
  3. Meslo LG M Nerd Font Mono
  4. Fira Code Nerd Font
  5. Hack Nerd Font Mono

? Enter font size (default: 12):
  10-11  for high DPI displays
  12-14  for regular displays (12 is default)
  15-18  for accessibility

? Display configuration? (y/n):
? Restart Ghostty? (y/n):
```

**What gets created:**
- `~/.config/ghostty/config` - Main configuration file
- `~/.config/ghostty/config.backup.YYYYMMDD_HHMMSS` - Automatic backup

**Sample configuration generated:**
```
font-family = Noto Sans Mono CJK KR
font-size = 12
font-fallback = Noto Sans Mono CJK KR
font-fallback = AppleColorEmoji
line-height = 1.2
background = #1e1e2e
foreground = #cdd6f4
# ... more settings
```

### Step 3: Verify Setup (30 seconds)

```bash
./verify-setup.sh
```

**What happens:**
- Checks macOS version and architecture
- Verifies font installation
- Validates Ghostty configuration
- Tests Korean text rendering
- Generates colored status report
- Provides recommendations if needed

**Expected output:**
```
✓ Checks Passed:     15/15
✗ Checks Failed:     0/15
⚠ Warnings:         0/15

Overall Status:    100%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Setup Status: READY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Test Korean text rendering:**
```
안녕하세요 - Hello (Korean)
こんにちは - Hello (Japanese)
你好 - Hello (Chinese Simplified)
```

If above displays correctly, everything works!

## What Each Script Does

### install-korean-fonts.sh

**Input:**
- macOS system check
- Homebrew availability
- User choices for optional fonts

**Output:**
- Installed fonts in ~/Library/Fonts
- Log file: install-korean-fonts.log
- Status messages with timestamps

**Time:** 3-5 minutes (mostly download time)

**Can be skipped if:**
- Fonts already installed via other means
- Manual font installation preferred

### apply-ghostty-config.sh

**Input:**
- Font selection (interactive)
- Font size selection (interactive)
- Optional template configuration

**Output:**
- ~/.config/ghostty/config (new or replaced)
- ~/.config/ghostty/config.backup.* (automatic backup)
- Log file: apply-ghostty-config.log

**Time:** 1-2 minutes

**Can be skipped if:**
- Ghostty config already optimized
- Manual configuration preferred

### verify-setup.sh

**Input:**
- System checks (no user input needed)
- Optional Korean text rendering test

**Output:**
- Verification report with color-coded status
- Recommendations for fixes (if needed)
- Log file: verify-setup.log

**Time:** 30 seconds

**Cannot be skipped if:**
- You want to confirm everything works

## Troubleshooting

### Issue: "Homebrew is not installed"

**Solution:** Let script install it
```bash
# or manually:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Issue: "Ghostty is not installed"

**Solution:** Install Ghostty first
```bash
# Via GitHub releases
brew install ghostty

# or build from source
git clone https://github.com/ghostty-org/ghostty.git
cd ghostty && ./zig build -Doptimize=ReleaseFast
```

### Issue: Fonts don't appear after installation

**Solution:** Refresh font cache
```bash
fc-cache -fv
```

**Solution:** Restart Ghostty completely
```bash
killall ghostty
# then reopen Ghostty
```

### Issue: Korean text appears as boxes/squares

**Solution:** Check font installation
```bash
# List Noto fonts
ls ~/Library/Fonts | grep -i noto

# Reinstall if missing
./install-korean-fonts.sh
```

**Solution:** Verify Ghostty config font-family
```bash
# Check what font is set
cat ~/.config/ghostty/config | grep font-family

# Should see: font-family = Noto Sans Mono CJK KR (or similar)
```

## Next Steps After Installation

### 1. Customize Font Size

Edit `~/.config/ghostty/config`:
```bash
nano ~/.config/ghostty/config

# Change font-size to your preference:
# 10-11 for smaller, 14-16 for larger
font-size = 14
```

### 2. Customize Colors

Edit `~/.config/ghostty/config`:
```bash
# Change background/foreground colors
background = #0a0e27    # Darker
foreground = #d5d8df    # Lighter

# Or use a theme
cursor-color = #ff6f42  # Custom cursor color
```

### 3. Add Custom Keybindings

Edit `~/.config/ghostty/config`:
```bash
# Example keybindings
keybind = global:super+n=new_window
keybind = global:super+t=new_tab
keybind = super+w=close_surface
```

### 4. Enable Shell Integration

Edit `~/.config/ghostty/config`:
```bash
shell-integration = true
shell-integration-features = sudo,title
```

### 5. Set as Default Terminal

```bash
# In macOS System Settings:
# Settings > General > Default web browser > Ghostty
# (if your version supports it)
```

## Testing Your Setup

### Test 1: Korean Text

Open Ghostty and type/paste:
```
안녕하세요
こんにちは
你好
Bonjour
```

All should display correctly with proper font rendering.

### Test 2: Font Size

Verify font size matches your selection:
- Should be comfortable to read
- Not too small or blurry
- Consistent line height

### Test 3: Copy/Paste

```bash
# Test copying Korean text
echo "안녕하세요" | pbcopy
pbpaste  # Should show Korean text
```

### Test 4: Check Configuration

```bash
# Display your Ghostty config
cat ~/.config/ghostty/config

# Should show:
# - font-family set to your selection
# - font-size set to your choice
# - font-fallback entries for CJK and emoji
```

## Performance Tips

### Reduce Startup Time

Already optimized in default config:
- Animations disabled
- GPU acceleration enabled
- Efficient font fallback chain

### Optimize for Coding

```bash
# In ~/.config/ghostty/config

# Increase scrollback for development
scrollback-limit = 50000

# Disable selection copy for better performance
copy-on-select = false

# Enable bold colors
bold-is-bright = true
```

### Optimize for Terminal Work

```bash
# In ~/.config/ghostty/config

# Better spacing for readability
line-height = 1.3
letter-spacing = 0.5

# Faster response
scrollback-multiplier = 1
```

## Reverting Changes

### Restore Previous Ghostty Config

```bash
# List backups
ls -la ~/.config/ghostty/config.backup.*

# Restore most recent backup
cp ~/.config/ghostty/config.backup.* ~/.config/ghostty/config
```

### Remove Installed Fonts

```bash
# Via Homebrew
brew uninstall --cask font-noto-sans-cjk
brew uninstall --cask font-noto-serif-cjk
brew uninstall --cask font-noto-mono

# Or manually
rm -rf ~/Library/Fonts/NotoSans*.otf
rm -rf ~/Library/Fonts/NotoSerif*.otf
```

## Accessing Logs

### View Installation Log

```bash
cat install-korean-fonts.log
```

### View Configuration Log

```bash
cat apply-ghostty-config.log
```

### View Verification Log

```bash
cat verify-setup.log
```

### Search Logs for Errors

```bash
grep ERROR *.log
grep WARNING *.log
```

## Common Settings

### Recommended Configuration

```bash
# ~/.config/ghostty/config

# Fonts
font-family = Noto Sans Mono CJK KR
font-size = 12
font-fallback = Noto Sans Mono CJK KR
font-fallback = AppleColorEmoji

# Display
background = #1e1e2e
foreground = #cdd6f4
line-height = 1.2
window-padding-x = 8
window-padding-y = 8

# Terminal
copy-on-select = true
shell-integration = true
scrollback-limit = 10000
```

### Minimal Configuration

```bash
# Bare minimum for Korean support
font-family = Noto Sans Mono CJK KR
font-size = 12
font-fallback = AppleColorEmoji
```

## Getting Help

### Check Script Help

```bash
# View script with comments
less install-korean-fonts.sh

# Run with verbose output
bash -x ./install-korean-fonts.sh
```

### Run Full Verification

```bash
./verify-setup.sh
```

Verification will show:
- What's installed
- What's missing
- What needs fixing
- Step-by-step recommendations

### Manual Configuration

```bash
# Open config directly
nano ~/.config/ghostty/config

# Validate with Ghostty
ghostty --config-check
```

## Time Estimates

| Task | Time | User Input |
|------|------|-----------|
| Install Fonts | 3-5 min | Minimal (optional fonts) |
| Apply Config | 1-2 min | Yes (font, size) |
| Verify Setup | 30 sec | Optional (render test) |
| **Total** | **5-8 min** | **~2 minutes** |

## Success Indicators

After running all three scripts:

- ✓ All scripts complete without errors
- ✓ Ghostty launches with new config
- ✓ Korean text displays correctly
- ✓ Font appears crisp and clear
- ✓ No performance degradation
- ✓ Verification script shows "READY"

## Next: Advanced Configuration

Once basic setup is complete, explore:
- Custom color schemes
- Terminal multiplexers (tmux, zellij)
- Shell integration
- Custom keybindings
- Font ligatures

See `README.md` for advanced options.

---

**Quick Reference**
```bash
# The 3-command setup
./install-korean-fonts.sh
./apply-ghostty-config.sh
./verify-setup.sh
```

That's it! You're ready to use Korean fonts in Ghostty.
