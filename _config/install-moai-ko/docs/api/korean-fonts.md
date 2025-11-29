# 🇰🇷 Korean Fonts Configuration Guide

**Version**: 1.0.0
**Last Updated**: November 29, 2025
**Purpose**: Comprehensive Korean font setup for MoAI-ADK

## 📋 Overview

This guide provides detailed information about Korean font configuration for optimal terminal display in MoAI-ADK development environments.

---

## 🔤 D2Coding Font (Recommended)

### **Overview**

**D2Coding** is the recommended Korean programming font developed by NAVER, South Korea's leading technology company.

**Key Features**:
- ✅ Optimized for Korean programming
- ✅ Clear distinction between similar characters (0/O, 1/l/I, etc.)
- ✅ Complete CJK (Korean/Chinese/Japanese) support
- ✅ Programming ligatures
- ✅ Monospace design
- ✅ Open Source (OFL license)
- ✅ Regular and Bold weights

**Font Metrics**:
- **Name**: D2Coding
- **Version**: 1.3.2 (latest)
- **License**: SIL Open Font License (OFL)
- **Developer**: NAVER Corporation
- **Character Coverage**: 11,172 Hangul syllables + Latin + Symbols
- **Weight**: Regular (400), Bold (700)

---

## 💾 Installation

### **macOS Installation**

#### Method 1: Homebrew (Recommended)

```bash
# Add font tap (if not already added)
brew tap homebrew/cask-fonts

# Install D2Coding
brew install --cask font-d2coding

# Verify installation
fc-list | grep -i d2coding

# Expected output:
# /Users/username/Library/Fonts/D2Coding.ttc: D2Coding:style=Regular
# /Users/username/Library/Fonts/D2Coding.ttc: D2Coding:style=Bold
```

#### Method 2: Manual Installation

```bash
# Download font
curl -L https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip -o D2Coding.zip

# Extract
unzip D2Coding.zip -d D2Coding

# Install to user fonts directory
cp D2Coding/D2Coding/*.ttf ~/Library/Fonts/

# Or install to system fonts (requires sudo)
sudo cp D2Coding/D2Coding/*.ttf /Library/Fonts/

# Restart applications to detect new fonts
```

#### Method 3: Font Book.app

1. Download D2Coding from: https://github.com/naver/d2codingfont/releases
2. Extract the ZIP file
3. Open Font Book.app
4. Drag and drop `.ttf` files into Font Book
5. Fonts are automatically installed

---

### **Linux Installation**

#### Ubuntu/Debian

```bash
# Download font
wget https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip

# Extract
unzip D2Coding-Ver1.3.2-20180524.zip -d D2Coding

# Create font directory
sudo mkdir -p /usr/share/fonts/truetype/d2coding

# Install fonts
sudo cp D2Coding/D2Coding/*.ttf /usr/share/fonts/truetype/d2coding/

# Update font cache
sudo fc-cache -f -v

# Verify installation
fc-list | grep -i d2coding

# Expected output:
# /usr/share/fonts/truetype/d2coding/D2Coding.ttf: D2Coding:style=Regular
# /usr/share/fonts/truetype/d2coding/D2CodingBold.ttf: D2Coding:style=Bold
```

#### Fedora/RHEL/CentOS

```bash
# Download font
wget https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip

# Extract
unzip D2Coding-Ver1.3.2-20180524.zip -d D2Coding

# Install fonts
sudo mkdir -p /usr/share/fonts/d2coding
sudo cp D2Coding/D2Coding/*.ttf /usr/share/fonts/d2coding/

# Update font cache
sudo fc-cache -f -v

# Verify
fc-list | grep D2Coding
```

#### Arch Linux

```bash
# Using AUR
yay -S ttf-d2coding

# Or manual installation
wget https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip
unzip D2Coding-Ver1.3.2-20180524.zip
sudo cp D2Coding/D2Coding/*.ttf /usr/share/fonts/TTF/
sudo fc-cache -f -v
```

#### User-Local Installation (No sudo required)

```bash
# Download and extract
wget https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip
unzip D2Coding-Ver1.3.2-20180524.zip -d D2Coding

# Create user fonts directory
mkdir -p ~/.local/share/fonts/d2coding

# Install fonts
cp D2Coding/D2Coding/*.ttf ~/.local/share/fonts/d2coding/

# Update user font cache
fc-cache -f -v ~/.local/share/fonts

# Verify
fc-list : file family | grep D2Coding
```

---

### **Windows (WSL2) Installation**

#### Option 1: Install on Windows (Recommended)

Windows fonts are automatically available in WSL2.

```powershell
# In Windows PowerShell:
# 1. Download D2Coding from:
#    https://github.com/naver/d2codingfont/releases

# 2. Extract ZIP file

# 3. Right-click each .ttf file and select "Install"
#    Or: Copy .ttf files to C:\Windows\Fonts\

# 4. Restart WSL2 terminal
```

#### Option 2: Install in WSL2 Directly

```bash
# In WSL2 terminal
wget https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip
unzip D2Coding-Ver1.3.2-20180524.zip
mkdir -p ~/.local/share/fonts
cp D2Coding/D2Coding/*.ttf ~/.local/share/fonts/
fc-cache -f -v
```

---

## 🖥️ Terminal Configuration

### **Ghostty (Recommended)**

Ghostty provides excellent Korean character support.

**Configuration** (`~/.config/ghostty/config`):

```ini
# Font Configuration
font-family = "D2Coding"
font-size = 13
font-feature = +liga +calt

# Character Encoding
locale = ko_KR.UTF-8
shell-integration-features = true

# Korean Display Optimization
allow-alternate-screen = true
mouse-shift-capture = false

# Advanced Font Settings
font-thicken = false
adjust-cell-height = 0
adjust-cell-width = 0

# Ensure proper glyph rendering
font-synthetic-style = false
```

**Testing**:
```bash
# Test Korean display
echo "D2Coding 폰트 테스트: 가나다라마바사아자차카타파하"
echo "0O 1lI 5S 8B comparison test"
```

---

### **iTerm2 (macOS)**

**Step-by-Step Configuration**:

1. **Open Preferences**: `⌘,` (Command + Comma)

2. **Navigate to Profiles → Text**

3. **Font Configuration**:
   - Click "Change" button
   - Select "D2Coding"
   - Set size to "13" (recommended)
   - Weight: Regular
   - Check "Use ligatures" (optional)

4. **Unicode Settings**:
   - Go to Text → Unicode
   - Enable "Use Unicode version 9 widths"
   - Enable "Treat ambiguous characters as double-width"
   - Unicode normalization: NFC

5. **Character Encoding**:
   - Set "Character Encoding" to "UTF-8"

6. **Advanced Text Settings**:
   - Disable "Draw bold text in bold font"
   - Enable "Anti-aliased"
   - Enable "Use thin strokes for anti-aliased text"

**Profile Export**:

Save this profile for easy sharing:

```json
{
  "Name": "Korean D2Coding",
  "Guid": "d2coding-korean",
  "Normal Font": "D2Coding 13",
  "Non Ascii Font": "D2Coding 13",
  "Character Encoding": 4,
  "Use Unicode Version 9 Widths": true,
  "Treat Ambiguous-Width Characters As Double Width": true,
  "Unicode Normalization": 1,
  "Use Ligatures": true
}
```

---

### **Terminal.app (macOS)**

**Configuration**:

1. **Open Preferences**: `⌘,`

2. **Profiles Tab**:
   - Select profile or create new "Korean Development"

3. **Text Tab**:
   - Uncheck "Use system font"
   - Click "Change"
   - Select "D2Coding Regular"
   - Size: 13

4. **Advanced Tab**:
   - Character encoding: UTF-8
   - Check "Set locale environment variables on startup"

5. **Set as Default**:
   - Click "Default" button at bottom

**Shell Configuration** (optional):

```bash
# Add to ~/.zshrc
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8
```

---

### **GNOME Terminal (Linux)**

**GUI Configuration**:

1. **Preferences** → Edit → Preferences

2. **Create Profile**:
   - Click "+" to add profile
   - Name: "D2Coding Korean"

3. **Text Tab**:
   - Uncheck "Use system font"
   - Select "D2Coding Regular 13"

4. **General Tab**:
   - Ensure "Use the system locale" is checked

**Command-Line Configuration**:

```bash
# Get profile UUID
dconf list /org/gnome/terminal/legacy/profiles:/

# Set font (replace :UUID: with your profile UUID)
dconf write /org/gnome/terminal/legacy/profiles:/:UUID:/font "'D2Coding 13'"
dconf write /org/gnome/terminal/legacy/profiles:/:UUID:/use-system-font false

# Set encoding
dconf write /org/gnome/terminal/legacy/profiles:/:UUID:/encoding "'UTF-8'"
```

---

### **Konsole (KDE)**

**Configuration** (`~/.local/share/konsole/Korean.profile`):

```ini
[Appearance]
Font=D2Coding,13,-1,5,50,0,0,0,0,0

[General]
Name=Korean Development
Parent=FALLBACK/

[Encoding Options]
DefaultEncoding=UTF-8

[Scrolling]
HistorySize=10000
```

**Set as Default**:
```bash
kwriteconfig5 --file konsolerc --group "Desktop Entry" --key DefaultProfile "Korean.profile"
```

---

### **Alacritty (Cross-Platform)**

**Configuration** (`~/.config/alacritty/alacritty.yml`):

```yaml
# Font Configuration
font:
  normal:
    family: D2Coding
    style: Regular
  bold:
    family: D2Coding
    style: Bold
  italic:
    family: D2Coding
    style: Regular
  bold_italic:
    family: D2Coding
    style: Bold
  size: 13.0

  # Font offset
  offset:
    x: 0
    y: 0

  # Glyph offset
  glyph_offset:
    x: 0
    y: 0

# Locale
env:
  LANG: ko_KR.UTF-8
  LC_ALL: ko_KR.UTF-8

# Cell dimensions
draw_bold_text_with_bright_colors: true
```

---

## 🎨 Font Comparison

### **Character Display Test**

Use this test to compare fonts:

```bash
cat << 'EOF'
========================================
Korean Font Display Test
========================================

Hangul Consonants:
ㄱ ㄴ ㄷ ㄹ ㅁ ㅂ ㅅ ㅇ ㅈ ㅊ ㅋ ㅌ ㅍ ㅎ

Hangul Vowels:
ㅏ ㅑ ㅓ ㅕ ㅗ ㅛ ㅜ ㅠ ㅡ ㅣ

Korean Words:
한글 테스트 성공 MoAI-ADK 설치 완료
가나다라마바사아자차카타파하

Programming Characters:
0O 1lI 5S 8B {}[] ()
!= == >= <= -> =>

Mixed Text:
Hello 안녕하세요 World 세계 123

Code Example:
const message = "한글 메시지";
function greet() {
  console.log("안녕하세요");
}

========================================
EOF
```

---

## 📊 Font Specifications

### **D2Coding Font Details**

| Property | Value |
|----------|-------|
| **Family Name** | D2Coding |
| **Full Name** | D2Coding Regular / D2Coding Bold |
| **PostScript Name** | D2Coding |
| **Version** | 1.3.2 |
| **Release Date** | May 24, 2018 |
| **File Format** | TrueType Collection (.ttc) |
| **File Size** | ~10 MB |
| **Weights** | Regular (400), Bold (700) |
| **Glyph Count** | 11,172 Hangul + Latin + Symbols |

### **Character Coverage**

- **Hangul**: Complete (11,172 modern Korean syllables)
- **Latin**: Basic + Extended (A-Z, a-z, accented characters)
- **Numbers**: 0-9 with clear distinction
- **Symbols**: Programming symbols, math operators
- **Punctuation**: Korean and English punctuation
- **Arrows**: → ← ↑ ↓ ⇒ ⇐
- **Box Drawing**: ─ │ ┌ ┐ └ ┘

### **Design Features**

1. **Clear Character Distinction**:
   - `0` (zero) vs `O` (letter O) - Clear differentiation
   - `1` (one) vs `l` (lowercase L) vs `I` (uppercase i) - Distinct shapes
   - `5` vs `S` - Easy to distinguish
   - `8` vs `B` - Clear difference

2. **Monospace Alignment**:
   - All characters same width
   - Korean characters = 2x Latin character width
   - Perfect alignment in code

3. **Programming Ligatures** (optional):
   - `!=` → ≠
   - `>=` → ≥
   - `<=` → ≤
   - `->` → →
   - `=>` → ⇒

---

## 🔍 Verification

### **Font Installation Check**

```bash
# macOS
fc-list | grep -i d2coding
ls ~/Library/Fonts/ | grep -i d2
ls /Library/Fonts/ | grep -i d2

# Linux
fc-list | grep -i d2coding
ls /usr/share/fonts/truetype/d2coding/
ls ~/.local/share/fonts/ | grep -i d2

# Get detailed font information
fc-list : file family style | grep D2Coding
```

**Expected Output**:
```
/path/to/D2Coding.ttc: D2Coding:style=Regular
/path/to/D2Coding.ttc: D2Coding:style=Bold
```

### **Terminal Font Check**

```bash
# Test Korean character rendering
echo "폰트 테스트: ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ"
echo "한글 테스트 성공!"

# If characters display clearly: ✅ Font working
# If characters show as boxes: ❌ Font not configured in terminal
```

---

## 🐛 Troubleshooting

### **Issue: Font Not Appearing in Terminal**

**Solutions**:

1. **Restart Terminal Application**:
   ```bash
   # Close and reopen terminal
   # Or force restart:
   killall Terminal  # macOS Terminal.app
   killall iTerm2    # iTerm2
   killall ghostty   # Ghostty
   ```

2. **Rebuild Font Cache**:
   ```bash
   # macOS
   sudo atsutil databases -remove
   sudo atsutil server -shutdown
   sudo atsutil server -ping

   # Linux
   sudo fc-cache -f -v
   ```

3. **Verify Font Files**:
   ```bash
   # Check file integrity
   file ~/Library/Fonts/D2Coding.ttc
   # Expected: TrueType font collection data
   ```

---

### **Issue: Korean Characters Still Show as Boxes**

**Solutions**:

1. **Check Terminal Font Setting**:
   - Ensure D2Coding is selected in terminal preferences
   - Font size should be 13 or larger
   - Restart terminal after changing

2. **Verify Locale**:
   ```bash
   locale | grep ko_KR.UTF-8
   # If empty, set locale:
   export LANG=ko_KR.UTF-8
   export LC_ALL=ko_KR.UTF-8
   ```

3. **Test with Different Terminal**:
   - Try Ghostty (best Korean support)
   - Verify font works in other applications

---

## 📞 Support

For font-related issues:

1. **D2Coding GitHub**: https://github.com/naver/d2codingfont
2. **MoAI-ADK Docs**: See `03-KOREAN-SETUP.md`
3. **Troubleshooting**: See `05-TROUBLESHOOTING.md`

---

**D2Coding Font** - The best Korean programming font for developers 🇰🇷✨
