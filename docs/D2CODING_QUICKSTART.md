# D2Coding Font - Quick Start Guide

**Status:** ✅ WORKING (Verified 2025-11-28)

---

## 🚀 TL;DR - Just Install It

### Recommended (Most Popular - 3x installs):
```bash
brew install --cask font-d2coding-nerd-font
```

### Standard Version:
```bash
brew install --cask font-d2coding
```

**No tapping required!** The `homebrew/cask-fonts` tap was deprecated in May 2024, and all fonts are now in the main cask repository.

---

## ❌ What Changed (Deprecated Commands)

**OLD (DO NOT USE):**
```bash
# ❌ This will fail
brew tap homebrew/cask-fonts
brew install --cask font-d2coding
```

**NEW (CORRECT):**
```bash
# ✅ This works
brew install --cask font-d2coding
```

---

## 🎯 Which Version Should I Install?

| Use Case | Install Command | Why? |
|----------|----------------|------|
| **Terminal/iTerm2** | `brew install --cask font-d2coding-nerd-font` | Powerline, icons, ligatures |
| **VS Code/IntelliJ** | `brew install --cask font-d2coding-nerd-font` | Better features, more popular |
| **Minimal Install** | `brew install --cask font-d2coding` | Smaller size, official Naver |
| **Offline/No Homebrew** | [Download from GitHub](https://github.com/naver/d2codingfont/releases/tag/VER1.3.2) | Manual install |

---

## 📦 Installation Methods

### Method 1: One-Line Install (Recommended)

```bash
# Install Nerd Font variant (recommended)
brew install --cask font-d2coding-nerd-font

# OR install standard version
brew install --cask font-d2coding
```

### Method 2: Interactive Script

```bash
# Run interactive installer
./scripts/install-d2coding-font.sh

# Or specify variant directly
./scripts/install-d2coding-font.sh nerd      # Nerd Font
./scripts/install-d2coding-font.sh standard  # Standard
./scripts/install-d2coding-font.sh manual    # Manual guide
```

### Method 3: Manual Download

1. Download: https://github.com/naver/d2codingfont/releases/tag/VER1.3.2
2. Extract files
3. Copy to `~/Library/Fonts/`
4. Restart apps

---

## ⚙️ Configuration

### VS Code (`settings.json`):

```json
{
  "editor.fontFamily": "D2CodingLigature Nerd Font",
  "editor.fontLigatures": true,
  "editor.fontSize": 14
}
```

### iTerm2:

1. Preferences → Profiles → Text
2. Font → D2CodingLigature Nerd Font
3. Size: 14

### Terminal.app:

1. Preferences → Profiles → Font
2. Change → D2CodingLigature Nerd Font
3. Size: 14

---

## 🔍 Verification

```bash
# Check if Homebrew can find it
brew search d2coding

# Check installation status
brew info --cask font-d2coding-nerd-font

# List installed fonts
ls ~/Library/Fonts/ | grep -i d2coding
```

---

## 🆘 Troubleshooting

### Font not appearing after installation?

```bash
# Clear font cache
sudo atsutil databases -remove
atsutil server -shutdown
atsutil server -ping
```

### Homebrew installation fails?

```bash
# Update Homebrew
brew update

# Try again
brew install --cask font-d2coding-nerd-font
```

### Still not working?

Use manual installation:
```bash
./scripts/install-d2coding-font.sh manual
```

---

## 📊 Version Information

| Package | Version | Files | Size | Installs/Year |
|---------|---------|-------|------|---------------|
| font-d2coding | 1.3.2 | 1 TTC | ~2MB | 1,297 |
| font-d2coding-nerd-font | 3.4.0 | 6 TTF | ~12MB | 3,969 |

---

## 📚 Full Documentation

For detailed information, see:
- **Full Guide:** `/docs/D2CODING_INSTALLATION_GUIDE.md`
- **Installation Script:** `/scripts/install-d2coding-font.sh`
- **Official Repo:** https://github.com/naver/d2codingfont
- **Nerd Fonts:** https://github.com/ryanoasis/nerd-fonts

---

**Last Updated:** 2025-11-28
**Research Status:** ✅ COMPLETE & VERIFIED
