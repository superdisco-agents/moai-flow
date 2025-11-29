# Korean Fonts Quick Reference for Ghostty

## Top 3 Recommendations

### 1. D2Coding Nerd Font ⭐ (Recommended)
```bash
brew install --cask font-d2coding-nerd-font
```
**Config:**
```toml
font-family = "D2CodingLigature Nerd Font"
font-size = 13
```
**Why:** Native Korean + ligatures + Nerd icons

---

### 2. Sarasa Gothic (Multilingual)
```bash
brew install --cask font-sarasa-gothic
```
**Config:**
```toml
font-family = "Sarasa Term K"
font-size = 13
```
**Why:** Best CJK support (Korean/Japanese/Chinese)

---

### 3. JetBrains Mono NF (Modern)
```bash
brew install --cask font-jetbrains-mono-nerd-font
```
**Config:**
```toml
font-family = "JetBrainsMono Nerd Font"
font-size = 13
```
**Why:** Modern + macOS Korean fallback

---

## Quick Comparison

| Font | Korean | Ligatures | Icons | Size | Best For |
|------|--------|-----------|-------|------|----------|
| D2Coding Nerd ⭐ | Native | ✅ | ✅ | 10 MB | Korean dev |
| Sarasa Gothic | Native | ✅ | ❌ | 130 MB | Multilingual |
| JetBrains Mono NF | Fallback | ✅ | ✅ | 15 MB | Modern style |
| Hack Nerd (Most popular) | Fallback | ❌ | ✅ | 12 MB | General use |
| Nanum Gothic Coding | Native | ❌ | ❌ | 2 MB | Lightweight |

---

## Install All Korean Fonts

```bash
brew install --cask \
  font-d2coding-nerd-font \
  font-sarasa-gothic \
  font-nanum-gothic-coding
```

---

## Test Fonts

```bash
echo "Hello 안녕하세요 こんにちは"
echo "== != => -> <= >="
echo "       "
```

---

## Full Guide
See: `korean-fonts-ghostty-guide.md` for comprehensive details

**Created:** 2025-11-28
