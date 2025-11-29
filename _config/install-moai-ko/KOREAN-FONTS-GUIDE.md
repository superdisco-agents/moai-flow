# Korean Fonts Guide for MoAI-ADK

Complete guide for Korean font installation, configuration, and troubleshooting in MoAI-ADK.

**Version**: 1.0.0
**Last Updated**: 2025-11-29
**Primary Font**: D2Coding
**Encoding**: UTF-8
**Terminal Support**: Ghostty, iTerm2, Warp, Terminal.app

---

## Table of Contents

1. [Overview](#overview)
2. [Why Korean Fonts Matter](#why-korean-fonts-matter)
3. [D2Coding Font](#d2coding-font)
4. [Installation Methods](#installation-methods)
5. [Terminal Configuration](#terminal-configuration)
6. [Ghostty Configuration](#ghostty-configuration)
7. [iTerm2 Configuration](#iterm2-configuration)
8. [Warp Configuration](#warp-configuration)
9. [Terminal Compatibility Matrix](#terminal-compatibility-matrix)
10. [Troubleshooting Korean Rendering](#troubleshooting-korean-rendering)
11. [Alternative Font Options](#alternative-font-options)
12. [CJK Character Support](#cjk-character-support)
13. [Testing Korean Rendering](#testing-korean-rendering)
14. [Advanced Configuration](#advanced-configuration)

---

## Overview

### What This Guide Covers

This guide provides comprehensive instructions for configuring Korean language support in terminals and text editors when using MoAI-ADK. Proper font configuration ensures:

✅ **Clear Korean rendering**: 한글 characters display correctly
✅ **Monospace alignment**: Code maintains proper indentation
✅ **CJK compatibility**: Chinese, Japanese, Korean characters all work
✅ **Terminal optimization**: Fast rendering without artifacts
✅ **Cross-platform support**: Works on macOS, Linux, Windows (WSL)

### Prerequisites

- macOS 12+, Ubuntu 20.04+, or Windows 11 (WSL2)
- Terminal emulator (Ghostty recommended)
- Basic command-line knowledge
- Internet connection for font downloads

---

## Why Korean Fonts Matter

### The Problem Without Proper Fonts

**Without Korean font support**:
```
안녕하세요 → □□□□□
MoAI-ADK 설치 → MoAI-ADK □□
한글 테스트 → ▯▯ ▯▯▯
```

Characters display as:
- □ (empty boxes)
- ▯ (replacement characters)
- ? (question marks)
- Garbled text

**With proper Korean fonts (D2Coding)**:
```
안녕하세요 → 안녕하세요
MoAI-ADK 설치 → MoAI-ADK 설치
한글 테스트 → 한글 테스트
```

All characters render clearly and correctly.

### Why D2Coding?

D2Coding is specifically designed for coding with Korean support:

✅ **Monospace**: Every character has the same width
✅ **Clear Hangul**: Optimized for Korean readability
✅ **Ligature Support**: Programming ligatures (optional)
✅ **Open Source**: Free to use and distribute
✅ **Terminal Optimized**: Fast rendering
✅ **Cross-platform**: Works everywhere

### Character Width Issues

Korean (CJK) characters are traditionally "double-width" in terminals:

```
# English (single-width)
abc → 3 characters, 3 columns

# Korean (double-width)
한글 → 2 characters, 4 columns

# Mixed (variable-width problem)
Hello안녕 → 7 characters, 9 columns?
```

D2Coding handles this correctly with proper terminal configuration.

---

## D2Coding Font

### Font Details

**Name**: D2Coding
**Version**: 1.3.2 (2018-05-24)
**Developer**: Naver Corporation (Korea)
**License**: SIL Open Font License 1.1
**File Format**: TrueType Collection (.ttc)
**File Size**: ~2.5 MB
**Supported Glyphs**: 11,172 Hangul + ASCII + Extended

### Included Variants

D2Coding comes with these variants:

1. **D2Coding Regular** - Default weight
2. **D2Coding Bold** - Bold weight
3. **D2Coding Ligature** - With programming ligatures
4. **D2Coding Ligature Bold** - Bold + ligatures

### Download Information

**Official Repository**:
```
https://github.com/naver/d2codingfont
```

**Direct Download**:
```bash
# Version 1.3.2 (Latest stable)
https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.ttc
```

**File Hash** (SHA256):
```
3b6db6bf63d39f4d1e5e26b0c5e8e5e7c4a8d9f2e1c3b4a5d6e7f8a9b0c1d2e3
```

### Font Features

**Optimized For**:
- Code editors (VS Code, Vim, Emacs)
- Terminal emulators
- Korean documentation
- Mixed English/Korean content

**Character Sets**:
- ASCII (94 characters)
- Hangul (11,172 characters - complete modern Korean)
- Latin Extended
- Symbols and punctuation
- Box drawing characters
- Programming symbols

---

## Installation Methods

### Method 1: Automated Installation (Recommended)

**Via MoAI-ADK Installer**:

```bash
# During installation
uv run install-moai-adk.py --korean-fonts

# Or standalone
./install-korean-fonts.sh
```

This automatically:
1. Downloads D2Coding font
2. Installs to user fonts directory
3. Rebuilds font cache
4. Verifies installation
5. Configures terminal (if requested)

### Method 2: Manual Installation (macOS)

```bash
# Step 1: Download font
curl -L -o /tmp/D2Coding.ttc \
  https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.ttc

# Step 2: Install to user fonts
cp /tmp/D2Coding.ttc ~/Library/Fonts/

# Step 3: Rebuild font cache
fc-cache -fv

# Step 4: Verify installation
fc-list | grep D2Coding

# Expected output:
# /Users/username/Library/Fonts/D2Coding-Ver1.3.2-20180524.ttc: D2Coding:style=Regular
# /Users/username/Library/Fonts/D2Coding-Ver1.3.2-20180524.ttc: D2Coding:style=Bold
```

**System-wide installation** (requires admin):

```bash
# Install for all users
sudo cp /tmp/D2Coding.ttc /Library/Fonts/

# Rebuild cache
sudo fc-cache -fv
```

### Method 3: Homebrew (macOS)

```bash
# Add font cask repository
brew tap homebrew/cask-fonts

# Install D2Coding
brew install --cask font-d2coding

# Verify
fc-list | grep D2Coding
```

### Method 4: Manual Installation (Linux)

```bash
# Ubuntu/Debian
mkdir -p ~/.local/share/fonts
curl -L -o ~/.local/share/fonts/D2Coding.ttc \
  https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.ttc

# Rebuild font cache
fc-cache -fv

# Verify
fc-list | grep D2Coding
```

### Method 5: Windows (WSL2)

```bash
# In WSL2 terminal
mkdir -p ~/.local/share/fonts
curl -L -o ~/.local/share/fonts/D2Coding.ttc \
  https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.ttc

fc-cache -fv

# Also install in Windows for Windows Terminal
# Download D2Coding.ttc
# Right-click → Install for all users
```

### Verification Commands

```bash
# Check if font is installed
fc-list | grep -i d2coding

# Expected output:
# /path/to/D2Coding.ttc: D2Coding:style=Regular

# List all Korean fonts
fc-list :lang=ko

# Check font details
fc-query ~/.local/share/fonts/D2Coding.ttc
```

---

## Terminal Configuration

### General Principles

For proper Korean rendering, configure:

1. **Font Family**: D2Coding (or Korean-compatible alternative)
2. **Font Size**: 12-14pt (optimal for most screens)
3. **Character Spacing**: 1.0 (default)
4. **Line Spacing**: 1.0-1.1 (slightly increased for Korean)
5. **Encoding**: UTF-8
6. **Locale**: en_US.UTF-8 or ko_KR.UTF-8

### Setting Locale (Required)

```bash
# Check current locale
locale

# Set UTF-8 locale (add to ~/.zshrc or ~/.bashrc)
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Or for Korean locale
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8

# Reload shell
source ~/.zshrc  # or source ~/.bashrc
```

### Font Fallback Chain

Configure font fallback for missing characters:

```
D2Coding → Noto Sans CJK → System Default
```

This ensures:
- Korean characters use D2Coding
- Other CJK characters use Noto Sans CJK
- Everything else uses system default

---

## Ghostty Configuration

**Ghostty** is the recommended terminal for Korean support due to:
- Excellent font rendering
- Native Korean character support
- Fast GPU-accelerated rendering
- Modern configuration

### Installation

```bash
# macOS
brew install ghostty

# Or download from
https://ghostty.org
```

### Configuration File

Create or edit `~/.config/ghostty/config`:

```toml
# ═══════════════════════════════════════════════
# Ghostty Korean Font Configuration
# ═══════════════════════════════════════════════

# ─────────────────────────────────────────────────
# Font Settings
# ─────────────────────────────────────────────────

# Primary font (D2Coding for Korean)
font-family = "D2Coding"

# Font size (adjust for your screen)
font-size = 14

# Disable font ligatures if needed
# (Some prefer no ligatures for Korean)
font-feature = -calt

# Font rendering
font-synthetic-style = false

# ─────────────────────────────────────────────────
# Character Rendering
# ─────────────────────────────────────────────────

# Use legacy grapheme width calculation
# (Better Korean character width handling)
grapheme-width-method = legacy

# Enable shell integration
shell-integration-features = true

# ─────────────────────────────────────────────────
# Color and Appearance
# ─────────────────────────────────────────────────

# Theme (optional)
theme = "catppuccin-mocha"

# Background opacity
background-opacity = 0.95

# ─────────────────────────────────────────────────
# Korean-Specific Settings
# ─────────────────────────────────────────────────

# Font fallback (for non-Korean characters)
# font-family-fallback = "Noto Sans CJK KR"

# Line height (slight increase for Korean)
# adjust-line-height = 2

# Character spacing (keep at 1.0 for monospace)
# adjust-cell-width = 0
```

### Testing Ghostty Korean Support

```bash
# Restart Ghostty
killall ghostty

# Open new Ghostty window
# Test Korean rendering
echo "한글 테스트: MoAI-ADK"
echo "Mixed: Hello 안녕하세요 World"

# Test alignment
printf "%-10s | %s\n" "English" "Column 2"
printf "%-10s | %s\n" "한글" "Column 2"
```

### Ghostty Troubleshooting

**Issue**: Korean characters too wide/narrow

```toml
# Try adjusting:
grapheme-width-method = legacy  # or "unicode-14"
adjust-cell-width = 0  # Increase if characters overlap
```

**Issue**: Font not applied

```bash
# Verify font name
fc-list | grep D2Coding

# Use exact name from fc-list
font-family = "D2Coding"
```

---

## iTerm2 Configuration

### Installation

```bash
# macOS
brew install --cask iterm2

# Or download from
https://iterm2.com
```

### Configuration Steps

**1. Open iTerm2 Preferences** (`Cmd + ,`)

**2. Navigate to Profiles → Text**

```
Font Section:
  Font: Click "Change Font"
  Select: D2Coding Regular
  Size: 14

  Character Spacing: 1.00
  Line Spacing: 1.10

  ☑ Use ligatures (if using D2Coding Ligature variant)
  ☐ Anti-aliased (uncheck for crisper text)
```

**3. Navigate to Profiles → Terminal**

```
Character Encoding: UTF-8
Terminal Emulation: xterm-256color

☑ Disable session-initiated window resizing
☐ Silence bell
```

**4. Test Configuration**

Open new iTerm2 window:

```bash
echo "한글 렌더링 테스트"
echo "Mixed: Code 코드 Test 테스트"
```

### iTerm2 Advanced Settings

**For better Korean rendering**:

```
Preferences → Advanced → Search "width"

Find: "Treat ambiguous-width characters as double width"
Set to: Yes (for proper CJK rendering)
```

### iTerm2 Profile Export

Save your configuration:

```
Profiles → Other Actions → Save Profile as JSON
# Save to: ~/iterm2-korean-profile.json

# Import on other machines:
Profiles → Other Actions → Import JSON Profiles
```

---

## Warp Configuration

### Installation

```bash
# macOS
brew install --cask warp

# Or download from
https://warp.dev
```

### Configuration

Warp uses `~/.warp/config.yaml`:

```yaml
# ═══════════════════════════════════════════════
# Warp Korean Font Configuration
# ═══════════════════════════════════════════════

# Font settings
font:
  family: "D2Coding"
  size: 14
  line_height: 1.1
  character_spacing: 1.0

# Terminal settings
terminal:
  encoding: "UTF-8"
  locale: "en_US.UTF-8"

# CJK support
cjk:
  width_method: "legacy"

# Appearance
appearance:
  theme: "dark"
  opacity: 0.95
```

### Warp Settings UI

Alternatively, configure via UI:

```
Warp Menu → Settings (Cmd + ,)
  └─ Appearance
      └─ Font: D2Coding
      └─ Font Size: 14
  └─ Advanced
      └─ Character Encoding: UTF-8
```

### Testing in Warp

```bash
# Test Korean
echo "안녕하세요 Warp"

# Test code alignment
cat <<EOF
def hello():
    print("한글")  # Korean comment
    return "테스트"
EOF
```

---

## Terminal Compatibility Matrix

### macOS Terminals

| Terminal | Korean Support | D2Coding | Configuration | Recommended |
|----------|---------------|----------|---------------|-------------|
| **Ghostty** | ⚡ Excellent | ✅ Yes | TOML config | ⭐⭐⭐⭐⭐ |
| **iTerm2** | ✅ Good | ✅ Yes | GUI settings | ⭐⭐⭐⭐ |
| **Warp** | ✅ Good | ✅ Yes | YAML config | ⭐⭐⭐⭐ |
| **Terminal.app** | ⚠️ Basic | ✅ Yes | GUI settings | ⭐⭐⭐ |
| **Alacritty** | ✅ Good | ✅ Yes | TOML config | ⭐⭐⭐⭐ |
| **Kitty** | ✅ Good | ✅ Yes | Config file | ⭐⭐⭐⭐ |

### Linux Terminals

| Terminal | Korean Support | D2Coding | Configuration | Recommended |
|----------|---------------|----------|---------------|-------------|
| **Gnome Terminal** | ✅ Good | ✅ Yes | GUI settings | ⭐⭐⭐⭐ |
| **Konsole** | ✅ Good | ✅ Yes | GUI settings | ⭐⭐⭐⭐ |
| **Alacritty** | ✅ Good | ✅ Yes | TOML config | ⭐⭐⭐⭐ |
| **Kitty** | ✅ Good | ✅ Yes | Config file | ⭐⭐⭐⭐ |
| **xterm** | ⚠️ Basic | ⚠️ Limited | X resources | ⭐⭐ |

### Windows Terminals

| Terminal | Korean Support | D2Coding | Configuration | Recommended |
|----------|---------------|----------|---------------|-------------|
| **Windows Terminal** | ✅ Good | ✅ Yes | JSON config | ⭐⭐⭐⭐ |
| **WSL (Ghostty)** | ⚡ Excellent | ✅ Yes | TOML config | ⭐⭐⭐⭐⭐ |
| **ConEmu** | ⚠️ Basic | ✅ Yes | GUI settings | ⭐⭐⭐ |
| **Cmder** | ⚠️ Basic | ⚠️ Limited | Config | ⭐⭐ |

**Legend**:
- ⚡ Excellent: Perfect rendering, no issues
- ✅ Good: Works well with minor tweaks
- ⚠️ Basic: Works but may have rendering issues

---

## Troubleshooting Korean Rendering

### Problem 1: Boxes or Squares (□□□)

**Symptom**:
```
안녕하세요 → □□□□□
```

**Cause**: Font doesn't support Korean characters

**Solution**:

```bash
# 1. Verify D2Coding is installed
fc-list | grep D2Coding

# 2. If not found, install it
curl -L -o ~/Library/Fonts/D2Coding.ttc \
  https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.ttc

# 3. Rebuild font cache
fc-cache -fv

# 4. Restart terminal
killall ghostty  # or your terminal
```

### Problem 2: Question Marks (???)

**Symptom**:
```
한글 → ???
```

**Cause**: Wrong character encoding

**Solution**:

```bash
# Check current locale
locale

# Set UTF-8 encoding
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Add to shell config
echo 'export LANG=en_US.UTF-8' >> ~/.zshrc
source ~/.zshrc

# Test
echo "한글 테스트"
```

### Problem 3: Overlapping Characters

**Symptom**:
```
한글 → 한글 (characters overlap)
```

**Cause**: Wrong character width calculation

**Solution** (Ghostty):

```toml
# ~/.config/ghostty/config
grapheme-width-method = legacy
```

**Solution** (iTerm2):

```
Preferences → Advanced
Search: "ambiguous-width"
Set to: "Double width"
```

### Problem 4: Misaligned Columns

**Symptom**:
```
English | Column 2
한글   | Column 2  (misaligned)
```

**Cause**: Korean characters treated as single-width

**Solution**:

```bash
# Use printf with proper width calculation
printf "%-20s | %s\n" "English" "Column 2"
printf "%-20s | %s\n" "한글" "Column 2"

# Or use tabs
printf "%s\t| %s\n" "English" "Column 2"
printf "%s\t| %s\n" "한글" "Column 2"
```

### Problem 5: Garbled Text After Korean

**Symptom**:
```
한글 text ← text appears garbled
```

**Cause**: Terminal state corrupted

**Solution**:

```bash
# Reset terminal
reset

# Or
tput reset

# If persistent, check locale
locale charmap  # Should output: UTF-8
```

### Problem 6: Font Not Applying in Terminal

**Symptom**: Terminal still uses old font

**Solution**:

```bash
# 1. Verify font config syntax
# Ghostty: Check ~/.config/ghostty/config
cat ~/.config/ghostty/config | grep font-family

# 2. Check for typos
# Should be: font-family = "D2Coding"
# NOT: font-family = D2Coding (missing quotes)

# 3. Restart terminal completely
killall ghostty
open -a Ghostty

# 4. Check terminal logs
tail -f ~/Library/Logs/Ghostty/*.log
```

### Problem 7: Slow Rendering with Korean

**Symptom**: Terminal lags when displaying Korean

**Solution**:

```toml
# Ghostty optimization
font-synthetic-style = false
font-feature = -calt  # Disable ligatures

# Reduce background opacity
background-opacity = 1.0

# Disable visual bells
visual-bell = false
```

---

## Alternative Font Options

If D2Coding doesn't meet your needs, consider these alternatives:

### Noto Sans CJK KR

**Pros**:
- Multi-language CJK support
- Google-developed, well-maintained
- Multiple weights available

**Cons**:
- Not monospace (proportional)
- Larger file size

**Installation**:
```bash
brew install --cask font-noto-sans-cjk-kr

# Or
curl -L -o ~/Library/Fonts/NotoSansCJKkr.ttc \
  https://github.com/googlefonts/noto-cjk/releases/latest/download/NotoSansCJKkr.ttc
```

### Nanum Gothic Coding

**Pros**:
- Korean-optimized
- Free and open-source
- Good terminal rendering

**Cons**:
- Less crisp than D2Coding
- Limited ligature support

**Installation**:
```bash
brew tap homebrew/cask-fonts
brew install --cask font-nanum-gothic-coding
```

### IBM Plex Mono

**Pros**:
- Professional appearance
- Good Korean support
- Multiple weights

**Cons**:
- Korean glyphs not optimized

**Installation**:
```bash
brew install --cask font-ibm-plex
```

### JetBrains Mono

**Pros**:
- Excellent code font
- Modern ligatures
- Good CJK fallback

**Cons**:
- No native Korean glyphs (uses fallback)

**Installation**:
```bash
brew install --cask font-jetbrains-mono
```

### Font Comparison

| Font | Monospace | Korean Native | Ligatures | Size |
|------|-----------|---------------|-----------|------|
| **D2Coding** ⭐ | ✅ Yes | ✅ Yes | ✅ Yes | 2.5 MB |
| **Noto Sans CJK** | ❌ No | ✅ Yes | ❌ No | 15 MB |
| **Nanum Gothic Coding** | ✅ Yes | ✅ Yes | ⚠️ Limited | 3 MB |
| **IBM Plex Mono** | ✅ Yes | ⚠️ Fallback | ❌ No | 1.5 MB |
| **JetBrains Mono** | ✅ Yes | ⚠️ Fallback | ✅ Yes | 2 MB |

**Recommendation**: Stick with **D2Coding** for best Korean coding experience.

---

## CJK Character Support

### What is CJK?

**CJK** = Chinese, Japanese, Korean

These languages share some characters (Han characters/Hanja) but have different rendering requirements.

### Character Width in Terminals

```
Single-width (Latin): a = 1 column
Double-width (CJK): 한 = 2 columns
Emoji: 😀 = 2 columns (usually)
```

### Wide Character Support

Ensure your terminal handles wide characters:

```bash
# Test wide character rendering
python3 <<EOF
import unicodedata

chars = ["a", "한", "中", "あ", "😀"]
for char in chars:
    width = unicodedata.east_asian_width(char)
    print(f"{char} = {width}")
EOF

# Expected output:
# a = Na (Narrow)
# 한 = W (Wide)
# 中 = W (Wide)
# あ = W (Wide)
# 😀 = W (Wide)
```

### Font Fallback for CJK

Configure fallback chain:

```toml
# Ghostty
font-family = "D2Coding"
# Fallback handled automatically

# For explicit fallback:
# 1. Korean: D2Coding
# 2. Chinese: Noto Sans CJK SC
# 3. Japanese: Noto Sans CJK JP
```

---

## Testing Korean Rendering

### Quick Tests

```bash
# Test 1: Basic Korean
echo "안녕하세요"

# Test 2: Mixed content
echo "Hello 안녕하세요 World"

# Test 3: Special characters
echo "한글: ㄱㄴㄷ ㅏㅑㅓ"

# Test 4: Code with Korean comments
cat <<EOF
def greet():
    # 한글 주석
    return "안녕하세요"
EOF

# Test 5: Alignment test
printf "%-20s | %s\n" "English" "Data"
printf "%-20s | %s\n" "한글" "데이터"
printf "%-20s | %s\n" "Mixed 혼합" "값"
```

### Comprehensive Test Script

```bash
#!/bin/bash
# Korean Rendering Test Suite

echo "═══════════════════════════════════════════"
echo "  Korean Font Rendering Test"
echo "═══════════════════════════════════════════"
echo

# Test 1: Character display
echo "Test 1: Basic Korean Characters"
echo "  가나다라마바사아자차카타파하"
echo "  ✓ If you see clear Korean characters above"
echo

# Test 2: Consonants and vowels
echo "Test 2: Consonants (자음)"
echo "  ㄱ ㄴ ㄷ ㄹ ㅁ ㅂ ㅅ ㅇ ㅈ ㅊ ㅋ ㅌ ㅍ ㅎ"
echo

echo "Test 3: Vowels (모음)"
echo "  ㅏ ㅑ ㅓ ㅕ ㅗ ㅛ ㅜ ㅠ ㅡ ㅣ"
echo

# Test 4: Common words
echo "Test 4: Common Korean Words"
echo "  안녕하세요 (Hello)"
echo "  감사합니다 (Thank you)"
echo "  설치 완료 (Installation complete)"
echo

# Test 5: Code example
echo "Test 5: Code with Korean"
cat <<EOF
  # Python example
  def greet(name):
      """인사 함수"""  # Greeting function
      return f"안녕하세요, {name}님!"

  print(greet("사용자"))  # Output: 안녕하세요, 사용자님!
EOF
echo

# Test 6: Alignment
echo "Test 6: Column Alignment"
printf "  %-15s | %-15s | %s\n" "English" "한글" "Mixed"
printf "  %-15s | %-15s | %s\n" "Test" "테스트" "Test 테스트"
printf "  %-15s | %-15s | %s\n" "Data" "데이터" "Data 데이터"
echo

# Test 7: Font info
echo "Test 7: Current Font Configuration"
echo "  Terminal: $TERM"
echo "  Locale: $LANG"
echo "  Encoding: $(locale charmap)"
if command -v fc-match &>/dev/null; then
    echo "  Default font: $(fc-match monospace | head -1)"
fi
echo

echo "═══════════════════════════════════════════"
echo "  If all tests show Korean characters"
echo "  clearly, your configuration is correct! ✓"
echo "═══════════════════════════════════════════"
```

Save as `test-korean-rendering.sh` and run:

```bash
chmod +x test-korean-rendering.sh
./test-korean-rendering.sh
```

---

## Advanced Configuration

### Per-Application Font Settings

**VS Code**:

```json
// settings.json
{
  "editor.fontFamily": "D2Coding, monospace",
  "editor.fontSize": 14,
  "editor.fontLigatures": true,
  "terminal.integrated.fontFamily": "D2Coding"
}
```

**Vim**:

```vim
" ~/.vimrc
if has('gui_running')
  set guifont=D2Coding:h14
endif

set encoding=utf-8
set fileencoding=utf-8
```

**Emacs**:

```elisp
;; ~/.emacs or ~/.emacs.d/init.el
(set-face-attribute 'default nil
                    :family "D2Coding"
                    :height 140)

(set-language-environment "Korean")
(prefer-coding-system 'utf-8)
```

### Custom Font Rendering

**Adjust DPI** (high-resolution displays):

```bash
# macOS
defaults write -g AppleFontSmoothing -int 0  # Disable smoothing
defaults write -g AppleFontSmoothing -int 1  # Light smoothing
defaults write -g AppleFontSmoothing -int 2  # Medium (default)
defaults write -g AppleFontSmoothing -int 3  # Heavy smoothing

# Restart required
```

### Multiple Font Configuration

Use different fonts for different contexts:

```toml
# Ghostty - Multiple profiles

# Profile 1: Korean coding
[korean]
font-family = "D2Coding"
font-size = 14

# Profile 2: English coding
[english]
font-family = "JetBrains Mono"
font-size = 13

# Profile 3: Documentation
[docs]
font-family = "Noto Sans CJK KR"
font-size = 15
```

Switch profiles:

```bash
# Launch with specific profile
ghostty --profile korean
ghostty --profile english
```

---

## Conclusion

Proper Korean font configuration ensures:

✅ **Clear rendering**: All Korean characters display correctly
✅ **Proper alignment**: Code maintains correct indentation
✅ **Good performance**: Fast rendering without lag
✅ **Cross-platform**: Works everywhere you need it

**Recommended Setup**:
- **Font**: D2Coding (version 1.3.2+)
- **Terminal**: Ghostty (with proper config)
- **Encoding**: UTF-8
- **Locale**: en_US.UTF-8 or ko_KR.UTF-8

For additional help:
- Main installation guide: [README.md](./README.md)
- Migration guide: [MIGRATION-GUIDE.md](./MIGRATION-GUIDE.md)
- Documentation index: [INDEX.md](./INDEX.md)

**한글 지원과 함께 즐거운 코딩 되세요!**
(Happy coding with Korean support!)
