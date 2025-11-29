# MOAI Korean Font & Ghostty Installation Scripts

Automated installation and configuration scripts for setting up Korean font support in Ghostty terminal emulator on macOS.

## Overview

This package contains three comprehensive bash scripts designed to automate the installation, configuration, and verification of Korean fonts and Ghostty setup:

1. **install-korean-fonts.sh** - Installs Korean fonts from Homebrew
2. **apply-ghostty-config.sh** - Configures Ghostty for Korean font support
3. **verify-setup.sh** - Verifies all components are properly installed

## Requirements

- **macOS** 10.13 or later
- **Homebrew** (automatically installed if missing)
- **Ghostty** (checked during configuration)
- **bash** 4.0 or later

## Quick Start

```bash
# Make scripts executable (if not already)
chmod +x *.sh

# Run the complete installation workflow
./install-korean-fonts.sh
./apply-ghostty-config.sh
./verify-setup.sh
```

## Script Details

### 1. install-korean-fonts.sh

Installs Korean font packages from Homebrew with comprehensive error handling.

#### Features
- ✓ macOS compatibility verification
- ✓ Automatic Homebrew installation if needed
- ✓ Font tap management
- ✓ Multiple Korean font options (Noto Sans CJK, Noto Serif CJK, etc.)
- ✓ Optional terminal fonts with Nerd Font support
- ✓ Font cache refresh
- ✓ Detailed logging and error reporting

#### Usage
```bash
./install-korean-fonts.sh
```

#### Fonts Installed
- **Noto Sans CJK** - Sans serif font with full CJK support
- **Noto Serif CJK** - Serif font with full CJK support
- **Noto Mono** - Monospace font for coding

#### Optional Terminal Fonts
- **Meslo LG Nerd Font** - Popular monospace terminal font
- **Fira Code Nerd Font** - Code-optimized font with ligatures
- **Hack Nerd Font** - Minimal, clean terminal font

#### Output Files
- `install-korean-fonts.log` - Installation log with timestamps

### 2. apply-ghostty-config.sh

Automatically configures Ghostty for optimal Korean font rendering.

#### Features
- ✓ Ghostty installation detection
- ✓ Configuration directory setup
- ✓ Automatic config backup before changes
- ✓ Interactive font and size selection
- ✓ Template-based configuration (if available)
- ✓ Configuration validation
- ✓ Automatic Ghostty restart option
- ✓ Configuration display and review

#### Usage
```bash
./apply-ghostty-config.sh
```

#### Configuration Options

**Font Selection:**
- Noto Sans Mono CJK KR
- Noto Serif CJK KR
- Meslo LG M Nerd Font Mono
- Fira Code Nerd Font
- Hack Nerd Font Mono

**Font Size:**
- 10-11: High DPI displays
- 12-14: Regular displays (default: 12)
- 15-18: Accessibility

#### Generated Configuration

The script creates a comprehensive Ghostty config with:
- Font family and size
- Fallback fonts for missing glyphs
- Line spacing and letter spacing
- Window padding and appearance
- Terminal behavior settings
- Tab configuration
- Performance settings

#### Output Files
- `${HOME}/.config/ghostty/config` - Main configuration file
- `${HOME}/.config/ghostty/config.backup.YYYYMMDD_HHMMSS` - Auto backup
- `apply-ghostty-config.log` - Configuration log

### 3. verify-setup.sh

Comprehensive verification script that tests all components.

#### Features
- ✓ System environment checks
- ✓ Font installation verification
- ✓ Ghostty configuration validation
- ✓ Korean text rendering test
- ✓ Package manager verification
- ✓ System integration checks
- ✓ Detailed verification report
- ✓ Setup status indicator
- ✓ Actionable recommendations

#### Usage
```bash
./verify-setup.sh
```

#### Verification Checklist
- macOS version compatibility
- System architecture support
- Font directory accessibility
- Korean font detection
- Terminal font availability
- Ghostty installation
- Configuration file presence
- Configuration content validation
- Font family settings
- Font size settings
- Fallback fonts
- Shell integration
- Korean text rendering

#### Output Files
- `verify-setup.log` - Verification log with details

#### Output Report

The script generates a color-coded report showing:
- **Summary Statistics**: Total checks, passed, failed, warnings
- **Overall Status**: Percentage of successful checks
- **Status Indicator**:
  - 🟢 READY - Setup complete with no issues
  - 🟡 PARTIALLY READY - Setup works but has warnings
  - 🔴 NEEDS ATTENTION - Critical issues to fix
- **Recommendations**: Actionable steps to fix issues

## Workflow

### Recommended Installation Order

1. **Install Fonts**
   ```bash
   ./install-korean-fonts.sh
   ```
   - Takes 3-5 minutes
   - Requires user interaction for optional fonts
   - No system restart needed

2. **Apply Configuration**
   ```bash
   ./apply-ghostty-config.sh
   ```
   - Takes 1-2 minutes
   - Interactive font selection
   - Automatic Ghostty restart option

3. **Verify Setup**
   ```bash
   ./verify-setup.sh
   ```
   - Takes 30 seconds
   - Displays status report
   - Provides recommendations if needed

### Alternative: Automated Installation

```bash
#!/bin/bash
# Run all scripts non-interactively
./install-korean-fonts.sh
./apply-ghostty-config.sh
./verify-setup.sh

echo "Setup complete! Check logs for details."
```

## Error Handling

### Common Issues and Solutions

#### Issue: "Homebrew is not installed"
```bash
# Solution: Let the script install it, or:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Issue: "Font directory not writable"
```bash
# Solution: Check permissions
ls -la ~/Library/Fonts

# Fix if needed
chmod 755 ~/Library/Fonts
```

#### Issue: "Ghostty is not installed"
```bash
# Solution: Install from source
git clone https://github.com/ghostty-org/ghostty.git
cd ghostty
./zig build -Doptimize=ReleaseFast
```

#### Issue: "Fonts appear blurry or incorrect"
```bash
# Solution 1: Refresh font cache
fc-cache -fv

# Solution 2: Restart Ghostty completely
killall ghostty

# Solution 3: Try different font size
# Edit ~/.config/ghostty/config and adjust font-size
```

#### Issue: Korean text displays as boxes/squares
```bash
# Solution: Verify font installation
ls ~/Library/Fonts | grep -i noto

# Re-run installation if needed
./install-korean-fonts.sh
```

### Getting Help

1. **Check Logs**: Review the generated `.log` files for detailed error messages
2. **Read Comments**: Scripts have inline comments explaining each section
3. **Test Rendering**: Use `verify-setup.sh` to test Korean text display
4. **Manual Configuration**: Edit `~/.config/ghostty/config` directly if needed

## Log Files

All scripts generate detailed log files in the scripts directory:

```bash
# View logs
cat install-korean-fonts.log
cat apply-ghostty-config.log
cat verify-setup.sh
```

Log entries include:
- Timestamp
- Log level (INFO, SUCCESS, ERROR, WARNING, SECTION)
- Detailed messages
- Full command output for debugging

## Manual Configuration

### Edit Ghostty Config Directly

If you prefer manual configuration:

```bash
nano ~/.config/ghostty/config
```

**Minimal Korean configuration:**
```
font-family = Noto Sans Mono CJK KR
font-size = 12
font-fallback = Noto Sans CJK
font-fallback = AppleColorEmoji
```

**Full configuration example:**
```
# Font Configuration
font-family = Noto Sans Mono CJK KR
font-size = 12
font-feature = calt
font-feature = ss02
font-fallback = Noto Sans Mono CJK KR
font-fallback = AppleColorEmoji

# Display Settings
background = #1e1e2e
foreground = #cdd6f4
line-height = 1.2
letter-spacing = 0

# Terminal Behavior
copy-on-select = true
shell-integration = true
```

## Advanced Options

### Font Features

Enable ligatures and contextual alternates:
```
font-feature = calt    # Contextual alternates
font-feature = liga    # Ligatures
font-feature = dlig    # Discretionary ligatures
```

### Custom Font Sizes by DPI

```bash
# Check your display DPI
system_profiler SPDisplaysDataType | grep Resolution

# Adjust based on DPI:
# - High DPI (Retina): 10-11pt
# - Standard DPI: 12-14pt
```

### Korean Input Method Setup

For better Korean input support:

1. Enable Korean input in macOS settings
2. Configure input method switching:
   ```bash
   # Add to ~/.config/ghostty/config
   # keybind = global:cmd+space=next_input_source
   ```

## Testing Korean Text

Test strings to verify proper rendering:

```
Basic: 안녕하세요 (hello)
Mixed: Hello 안녕 World 世界
Symbols: ™ © ® ⓒ ㉠ ㉡
Emoji: 😀 🎉 🚀 🌍
```

If these display correctly in Ghostty, your setup is working!

## Performance Considerations

### Optimization Tips

1. **Font Caching**: First launch loads fonts, subsequent launches are faster
2. **Disable Animations**: Already set in default config for performance
3. **GPU Acceleration**: Enabled in default config
4. **Scrollback Buffer**: Set to 10,000 lines by default (adjust as needed)

### Memory Usage

- Base Ghostty: ~50-100 MB
- With fonts loaded: ~150-200 MB
- Typical usage: Well within normal limits

## Troubleshooting

### Debug Mode

Run scripts with verbose output:
```bash
bash -x ./install-korean-fonts.sh
```

### Check Font Installation

```bash
# List all fonts
ls -la ~/Library/Fonts | grep -i noto

# Check font metadata
mdls ~/Library/Fonts/NotoSansCJKkr-Regular.otf
```

### Test Configuration

```bash
# Validate config syntax
ghostty --config-check

# Start Ghostty in debug mode
ghostty --debug
```

## System Impact

- **Disk Space**: ~200 MB for fonts
- **Installation Time**: 5-10 minutes total
- **System Changes**: Adds fonts to user Library only
- **Reversible**: Safe to uninstall fonts via Homebrew

## Security Considerations

- ✓ Scripts run locally only
- ✓ No remote execution
- ✓ Configuration backups created automatically
- ✓ Logs contain no sensitive information
- ✓ No environment variables modified permanently

## Uninstallation

### Remove Installed Fonts

```bash
# Via Homebrew
brew uninstall --cask font-noto-sans-cjk
brew uninstall --cask font-noto-serif-cjk
brew uninstall --cask font-noto-mono

# Manual removal
rm -rf ~/Library/Fonts/NotoSans*.otf
rm -rf ~/Library/Fonts/NotoSerif*.otf
```

### Restore Ghostty Config

```bash
# Restore from backup
cp ~/.config/ghostty/config.backup.* ~/.config/ghostty/config
```

## Version History

### Version 1.0.0 (Current)
- Initial release
- Korean font installation
- Ghostty configuration
- Comprehensive verification
- Full error handling
- Detailed logging

## Support & Contributions

For issues or improvements:
1. Check log files for detailed error messages
2. Review script comments for implementation details
3. Test with latest macOS version
4. Report issues with complete log output

## License

These scripts are provided as part of the MOAI ADK project.

## Additional Resources

- [Ghostty Documentation](https://github.com/ghostty-org/ghostty)
- [Noto Fonts](https://fonts.google.com/noto)
- [Homebrew Cask Fonts](https://github.com/Homebrew/homebrew-cask-fonts)
- [macOS Font Management](https://support.apple.com/en-us/HT201749)

---

**Last Updated**: November 28, 2025
**Tested On**: macOS 12.0+
**Shell**: bash 4.0+
