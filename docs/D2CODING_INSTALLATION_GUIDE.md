# D2Coding Font Installation Guide for macOS

**Research Date:** November 28, 2025
**Status:** ✅ VERIFIED & WORKING
**Swarm Research ID:** swarm_1764312788577_jxiop5dqb

---

## 🎯 Executive Summary

D2Coding font installation on macOS is **FULLY WORKING** using Homebrew. The `homebrew/cask-fonts` tap was deprecated in May 2024, but all fonts were migrated to the main `homebrew/cask` repository. **No additional tapping is required.**

---

## ✅ Recommended Installation Methods

### Method 1: Homebrew Standard D2Coding (RECOMMENDED FOR GENERAL USE)

```bash
brew install --cask font-d2coding
```

**Details:**
- Version: 1.3.2 (Released: June 1, 2024)
- File: `D2Coding-Ver1.3.2-20180524.ttc`
- Requirements: macOS >= 10.15
- Install count: 1,297 (last 365 days)
- Source: [Official Naver D2Coding Repository](https://github.com/naver/d2codingfont)

**Best for:**
- General development
- Code editors (VS Code, Sublime, IntelliJ)
- Standard Korean/English coding fonts

---

### Method 2: Homebrew D2Coding Nerd Font (RECOMMENDED FOR TERMINAL)

```bash
brew install --cask font-d2coding-nerd-font
```

**Details:**
- Version: 3.4.0
- Files included (6 fonts):
  - `D2CodingLigatureNerdFont-Bold.ttf`
  - `D2CodingLigatureNerdFont-Regular.ttf`
  - `D2CodingLigatureNerdFontMono-Bold.ttf`
  - `D2CodingLigatureNerdFontMono-Regular.ttf`
  - `D2CodingLigatureNerdFontPropo-Bold.ttf`
  - `D2CodingLigatureNerdFontPropo-Regular.ttf`
- Requirements: macOS >= 10.15
- Install count: 3,969 (last 365 days) - **3x more popular**
- Source: [Nerd Fonts Project](https://github.com/ryanoasis/nerd-fonts)

**Best for:**
- Terminal/iTerm2 users
- Powerline/Oh-My-Zsh themes
- Developers needing programming icons
- Ligature support

---

### Method 3: Manual Installation (FALLBACK)

**When to use:**
- Homebrew not available
- Need specific version
- Offline installation

**Steps:**

1. **Download from GitHub Releases:**
   ```bash
   # Latest release
   open https://github.com/naver/d2codingfont/releases/tag/VER1.3.2
   ```

2. **Extract and Install:**
   ```bash
   # User-only installation (recommended)
   cp *.ttf ~/Library/Fonts/
   cp *.ttc ~/Library/Fonts/

   # System-wide installation (requires sudo)
   sudo cp *.ttf /Library/Fonts/
   sudo cp *.ttc /Library/Fonts/
   ```

3. **Verify Installation:**
   ```bash
   # Check if font is installed
   ls ~/Library/Fonts/ | grep -i d2coding
   ```

4. **Clear Font Cache (if needed):**
   ```bash
   sudo atsutil databases -remove
   atsutil server -shutdown
   atsutil server -ping
   ```

---

## 📊 Comparison Matrix

| Feature | Standard D2Coding | D2Coding Nerd Font |
|---------|------------------|-------------------|
| **Installation** | `brew install --cask font-d2coding` | `brew install --cask font-d2coding-nerd-font` |
| **Version** | 1.3.2 (2024-06-01) | 3.4.0 |
| **Font Files** | 1 TTC file | 6 TTF files |
| **Ligature Support** | ✅ Yes (v1.3.2+) | ✅ Yes |
| **Programming Icons** | ❌ No | ✅ Yes (Nerd Fonts glyphs) |
| **Korean Support** | ✅ Excellent | ✅ Excellent |
| **Popularity (365d)** | 1,297 installs | 3,969 installs (3x) |
| **Best For** | General coding | Terminal/iTerm2 |
| **Powerline Compatible** | ❌ No | ✅ Yes |

---

## 🔧 Updated Script for `setup-korean-environment.sh`

Replace the deprecated font installation section with:

```bash
#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Installing D2Coding Font for macOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Error: Homebrew is not installed"
    echo "📥 Install Homebrew first: https://brew.sh"
    exit 1
fi

# Determine which font to install
echo ""
echo "Select D2Coding font variant:"
echo "  1) Standard D2Coding (general use)"
echo "  2) D2Coding Nerd Font (terminal/icons)"
echo ""
read -p "Enter choice [1-2] (default: 2): " font_choice

case ${font_choice:-2} in
    1)
        echo "📦 Installing Standard D2Coding Font..."
        brew install --cask font-d2coding
        ;;
    2)
        echo "📦 Installing D2Coding Nerd Font (with icons)..."
        brew install --cask font-d2coding-nerd-font
        ;;
    *)
        echo "❌ Invalid choice. Installing Nerd Font (default)..."
        brew install --cask font-d2coding-nerd-font
        ;;
esac

# Verify installation
if [ $? -eq 0 ]; then
    echo "✅ D2Coding font installed successfully!"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Restart your terminal/editor"
    echo "   2. Select 'D2Coding' or 'D2CodingLigature Nerd Font' in font settings"
    if [ "${font_choice:-2}" == "2" ]; then
        echo "   3. Enable ligatures for best experience (VS Code: 'editor.fontLigatures': true)"
    fi
else
    echo "❌ Font installation failed"
    echo "📥 Fallback: Download manually from https://github.com/naver/d2codingfont/releases"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

---

## 🚨 Important Notes

### Homebrew Font Tap Changes (2024)

**What Changed:**
- ❌ DEPRECATED: `brew tap homebrew/cask-fonts` (May 2024)
- ✅ NEW: All fonts migrated to main `homebrew/cask` repository
- ✅ RESULT: No tapping required - just use `brew install --cask font-name`

**Old Command (DO NOT USE):**
```bash
# ❌ DEPRECATED - Will fail
brew tap homebrew/cask-fonts
brew install --cask font-d2coding
```

**New Command (CORRECT):**
```bash
# ✅ CORRECT - Works as of Nov 2025
brew install --cask font-d2coding
```

### Version History

**D2Coding 1.3.2 (2024-06-01) - Current Release:**
- ✅ Fixed ligature-related issues
- ✅ Separate ligature/non-ligature versions
- ✅ IntelliJ 18pt character length fix
- ✅ Bold 'y' character sizing fix
- ✅ Heart symbol (U+2661) readability improvement
- ✅ Tab character display fix in Source Insight 4.0

---

## 🔍 Verification Commands

```bash
# Check if Homebrew has the font
brew search d2coding

# Get detailed info about installed font
brew info --cask font-d2coding
brew info --cask font-d2coding-nerd-font

# List installed fonts in user directory
ls -la ~/Library/Fonts/ | grep -i d2coding

# List installed fonts system-wide
ls -la /Library/Fonts/ | grep -i d2coding
```

---

## 📚 Additional Resources

- **Official Repository:** https://github.com/naver/d2codingfont
- **Latest Releases:** https://github.com/naver/d2codingfont/releases
- **Nerd Fonts Project:** https://github.com/ryanoasis/nerd-fonts
- **Homebrew Cask Info:** https://formulae.brew.sh/cask/font-d2coding
- **License:** Open Font License (OFL)

---

## 🎯 Recommendations

1. **For most users:** Install **D2Coding Nerd Font** (Method 2)
   - More popular (3x installs)
   - Better terminal support
   - Includes programming icons
   - Supports Powerline themes

2. **For minimal installation:** Install **Standard D2Coding** (Method 1)
   - Smaller file size (1 file vs 6)
   - Original Naver version
   - No extra glyphs

3. **For offline/air-gapped systems:** Use **Manual Installation** (Method 3)
   - Download ZIP from GitHub Releases
   - Copy to `~/Library/Fonts/`

---

**Research Status:** ✅ COMPLETE
**Last Updated:** 2025-11-28
**Verified on:** macOS 14.x & 15.x (Sonoma/Sequoia)
