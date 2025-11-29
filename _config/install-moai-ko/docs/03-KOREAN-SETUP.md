# 🇰🇷 Korean Language Setup for MoAI-ADK

**Version**: 1.0.0
**Last Updated**: November 29, 2025
**Target Users**: Korean developers, CJK language support

## 📋 Overview

This guide provides comprehensive Korean language support configuration for MoAI-ADK, including font installation, terminal setup, locale configuration, and character encoding.

**What You'll Get**:
- ✅ Proper Korean character rendering in terminal
- ✅ UTF-8 encoding for all file operations
- ✅ Korean input support for commands
- ✅ Clear display of CJK (Chinese/Japanese/Korean) characters
- ✅ Optimized fonts for programming with Korean

---

## 🎯 Why Korean Support?

### **Benefits**

1. **Clear Character Display**: No more boxes (□) or question marks (?) for Korean text
2. **Programming Fonts**: Optimized monospace fonts with proper Korean glyphs
3. **File Encoding**: Consistent UTF-8 handling across all operations
4. **Command Support**: Use Korean commands and comments naturally
5. **Documentation**: Read Korean documentation without issues

### **Use Cases**

- Korean developers writing code with Korean comments
- Projects with Korean variable/function names
- Korean documentation and specifications
- Multi-language codebases (Korean + English)
- Korean-speaking teams and collaborations

---

## 🔤 Korean Font Installation

### **Recommended: D2Coding Font**

D2Coding is the best font for Korean programming:
- **Developer-Optimized**: Created by NAVER for programmers
- **Clear Distinction**: Easy to differentiate similar characters (0/O, 1/l/I)
- **Full CJK Support**: Korean (Hangul), Chinese (Hanzi), Japanese (Kanji)
- **Ligatures**: Programming-specific character combinations
- **Open Source**: Free to use (OFL license)

#### **macOS Installation**

```bash
# Method 1: Homebrew (Recommended)
brew tap homebrew/cask-fonts
brew install --cask font-d2coding

# Verify installation
fc-list | grep -i d2coding

# Expected output:
# /Users/you/Library/Fonts/D2Coding.ttc: D2Coding:style=Regular
# /Users/you/Library/Fonts/D2Coding.ttc: D2Coding:style=Bold

# Check font version
fc-list : file family style | grep D2Coding
```

```bash
# Method 2: Manual Installation
# 1. Download font
curl -L https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip -o D2Coding.zip

# 2. Extract
unzip D2Coding.zip -d D2Coding

# 3. Install (double-click .ttf files or use command)
cp D2Coding/D2Coding/*.ttf ~/Library/Fonts/

# 4. Refresh font cache (macOS does this automatically)
# Restart applications to see new font
```

#### **Linux Installation (Ubuntu/Debian)**

```bash
# Method 1: From GitHub (Latest Version)
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
```

```bash
# Method 2: User-Local Installation (No sudo)
# Create user font directory
mkdir -p ~/.local/share/fonts/d2coding

# Download and extract
wget https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip
unzip D2Coding-Ver1.3.2-20180524.zip -d D2Coding

# Install fonts
cp D2Coding/D2Coding/*.ttf ~/.local/share/fonts/d2coding/

# Update user font cache
fc-cache -f -v ~/.local/share/fonts

# Verify
fc-list : file family | grep D2Coding
```

#### **Windows (WSL2)**

```bash
# Option 1: Install on Windows (WSL2 inherits Windows fonts)
# Download D2Coding font
# Navigate to: https://github.com/naver/d2codingfont/releases
# Download: D2Coding-Ver1.3.2-20180524.zip
# Extract and double-click .ttf files to install on Windows
# Restart WSL2 terminal

# Option 2: Install in WSL2 directly (for terminal use)
wget https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip
unzip D2Coding-Ver1.3.2-20180524.zip
mkdir -p ~/.local/share/fonts
cp D2Coding/D2Coding/*.ttf ~/.local/share/fonts/
fc-cache -f -v
```

### **Alternative Korean Fonts**

If D2Coding is not available, these are good alternatives:

#### **Nanum Gothic Coding**
```bash
# macOS
brew install --cask font-nanum-gothic-coding

# Linux
sudo apt install fonts-nanum-coding

# Verify
fc-list | grep -i nanum
```

#### **JetBrains Mono (with Korean)**
```bash
# macOS
brew install --cask font-jetbrains-mono

# Linux
wget https://download.jetbrains.com/fonts/JetBrainsMono-2.304.zip
unzip JetBrainsMono-2.304.zip
sudo cp fonts/ttf/*.ttf /usr/share/fonts/truetype/
sudo fc-cache -f -v
```

#### **Source Code Pro (with Korean subset)**
```bash
# macOS
brew install --cask font-source-code-pro

# Linux
sudo apt install fonts-source-code-pro
```

### **Font Comparison**

| Font | Korean Coverage | Coding Features | License | Recommendation |
|------|-----------------|-----------------|---------|----------------|
| **D2Coding** | 🇰🇷 Complete | ⭐⭐⭐⭐⭐ | OFL | **Best for Korean** |
| Nanum Gothic | 🇰🇷 Complete | ⭐⭐⭐ | OFL | Good alternative |
| JetBrains Mono | 🇰🇷 Partial | ⭐⭐⭐⭐⭐ | OFL | Good for mixed |
| Source Code Pro | 🇰🇷 Subset | ⭐⭐⭐⭐ | OFL | English-focused |
| Cascadia Code | 🇰🇷 Partial | ⭐⭐⭐⭐ | OFL | Windows users |

---

## 🖥️ Terminal Configuration

### **Ghostty Terminal (Recommended for Korean)**

Ghostty has excellent Unicode and CJK support out-of-the-box.

#### **Installation**
```bash
# macOS (Homebrew)
brew install --cask ghostty

# Or download from: https://ghostty.org
```

#### **Configuration**
```bash
# Create config directory
mkdir -p ~/.config/ghostty

# Create/edit configuration file
cat > ~/.config/ghostty/config << 'EOF'
# ===================================
# Ghostty Korean Configuration
# ===================================

# Font Settings
font-family = "D2Coding"
font-size = 13
font-feature = +liga +calt

# Character Encoding
locale = ko_KR.UTF-8
shell-integration-features = true

# Korean Input Support
allow-alternate-screen = true
mouse-shift-capture = false

# Display Settings
theme = dark
background-opacity = 0.95
window-padding-x = 10
window-padding-y = 10

# Terminal Type
term = xterm-256color

# Cursor
cursor-style = block
cursor-style-blink = true

# Shell (use your preferred shell)
shell-integration = zsh
EOF

# Restart Ghostty
# Korean text should now display perfectly
```

#### **Testing Ghostty**
```bash
# Open Ghostty and test Korean characters
echo "한글 테스트: MoAI-ADK 설치 완료"
echo "Korean Test: ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ"
echo "Mixed: Hello 안녕하세요 World 세계"

# Should display perfectly without boxes or errors
```

### **iTerm2 (macOS)**

Popular terminal for macOS with good Korean support.

#### **Configuration Steps**

1. **Open iTerm2 Preferences**: Press `⌘,` (Command + Comma)

2. **Navigate to Profiles → Text**

3. **Change Font**:
   - Click "Change" button under "Font"
   - Select "D2Coding"
   - Set size to 13pt or larger
   - Check "Use ligatures" (optional)

4. **Configure Character Encoding**:
   - Set "Character Encoding" to "UTF-8"
   - Check "Unicode normalization form" → "NFC"
   - Check "Treat ambiguous characters as double-width"

5. **Unicode Settings**:
   - Go to Profiles → Text → Unicode
   - Enable "Use Unicode version 9 widths"
   - Enable "East Asian Ambiguous characters are wide"

6. **Locale Settings**:
   - Go to Profiles → General → Command
   - Set custom shell command:
     ```bash
     /bin/zsh -c "export LANG=ko_KR.UTF-8; exec /bin/zsh"
     ```

#### **iTerm2 Profile Export**
```bash
# Save profile configuration
# Preferences → Profiles → Other Actions → Save Profile as JSON

# Or use this config snippet
cat > ~/Library/Application\ Support/iTerm2/DynamicProfiles/korean.json << 'EOF'
{
  "Profiles": [
    {
      "Name": "Korean Development",
      "Guid": "korean-dev-profile",
      "Normal Font": "D2Coding 13",
      "Non Ascii Font": "D2Coding 13",
      "Character Encoding": 4,
      "Use Unicode Version 9 Widths": true,
      "Treat Ambiguous-Width Characters As Double Width": true,
      "Custom Command": "Yes",
      "Command": "/bin/zsh -c \"export LANG=ko_KR.UTF-8; exec /bin/zsh\""
    }
  ]
}
EOF

# Restart iTerm2 and select "Korean Development" profile
```

### **Terminal.app (macOS Default)**

Built-in macOS terminal with basic Korean support.

#### **Configuration Steps**

1. **Open Terminal Preferences**: Press `⌘,`

2. **Select Profile** (or create new):
   - Go to Profiles tab
   - Select "Basic" or "Pro" profile
   - Or click "+" to create "Korean Dev" profile

3. **Configure Text**:
   - Tab: Text
   - Uncheck "Use system font"
   - Click "Change" and select "D2Coding Regular 13"

4. **Set Character Encoding**:
   - Tab: Advanced
   - Set "Character encoding" to "UTF-8"
   - Check "Set locale environment variables on startup"

5. **Configure Shell** (optional):
   - Tab: Shell
   - Set "Run command": `/bin/zsh -c "export LANG=ko_KR.UTF-8; exec /bin/zsh"`

6. **Make Default**:
   - Click "Default" button at bottom

### **GNOME Terminal (Linux)**

Default terminal for Ubuntu and many Linux distributions.

#### **GUI Configuration**

1. **Open Preferences**: Edit → Preferences

2. **Select/Create Profile**:
   - Select existing profile or click "+" for new
   - Name: "Korean Development"

3. **Configure Text**:
   - Tab: Text
   - Uncheck "Use system font"
   - Select "D2Coding Regular 13"

4. **Set Character Encoding**:
   - Tab: General
   - Ensure "Use the system locale" is checked
   - Or manually set to "UTF-8 (Unicode)"

5. **Shell Configuration**:
   - Tab: Command
   - Check "Run a custom command instead of my shell"
   - Custom command: `/bin/bash -c "export LANG=ko_KR.UTF-8; exec /bin/bash"`

#### **Command-Line Configuration**

```bash
# Create Korean profile via dconf
dconf write /org/gnome/terminal/legacy/profiles:/:profile-id/font "'D2Coding 13'"
dconf write /org/gnome/terminal/legacy/profiles:/:profile-id/use-system-font false

# Set encoding
dconf write /org/gnome/terminal/legacy/profiles:/:profile-id/encoding "'UTF-8'"

# Or use gsettings
gsettings set org.gnome.desktop.interface monospace-font-name 'D2Coding 13'
```

### **Konsole (KDE/Linux)**

KDE's default terminal emulator.

```bash
# Edit profile configuration
nano ~/.local/share/konsole/Korean.profile

# Add configuration:
[Appearance]
Font=D2Coding,13,-1,5,50,0,0,0,0,0

[General]
Name=Korean Development
Parent=FALLBACK/

[Encoding Options]
DefaultEncoding=UTF-8

# Set as default profile
kwriteconfig5 --file konsolerc --group "Desktop Entry" --key DefaultProfile "Korean.profile"
```

### **Alacritty (Cross-Platform)**

Modern GPU-accelerated terminal.

```bash
# Edit configuration
mkdir -p ~/.config/alacritty
nano ~/.config/alacritty/alacritty.yml

# Add Korean configuration:
font:
  normal:
    family: D2Coding
    style: Regular
  bold:
    family: D2Coding
    style: Bold
  size: 13.0

env:
  LANG: ko_KR.UTF-8
  LC_ALL: ko_KR.UTF-8

# Restart Alacritty
```

---

## 🌏 Locale Configuration

### **Understanding Locales**

Locales control:
- Language for system messages
- Character encoding (UTF-8)
- Date/time formats
- Number formats
- Currency display

**Korean Locale**: `ko_KR.UTF-8`
- `ko` = Korean language
- `KR` = South Korea region
- `UTF-8` = Character encoding

### **macOS Locale Setup**

```bash
# Check current locale
locale

# Expected output for Korean:
# LANG="ko_KR.UTF-8"
# LC_COLLATE="ko_KR.UTF-8"
# LC_CTYPE="ko_KR.UTF-8"
# LC_MESSAGES="ko_KR.UTF-8"
# ...

# If not set, add to shell configuration
echo '# Korean locale' >> ~/.zshrc
echo 'export LANG=ko_KR.UTF-8' >> ~/.zshrc
echo 'export LC_ALL=ko_KR.UTF-8' >> ~/.zshrc

# Reload shell
source ~/.zshrc

# Verify
locale | grep ko_KR
```

### **Linux Locale Setup**

```bash
# Check available locales
locale -a | grep ko_KR

# If Korean locale not available, generate it
sudo locale-gen ko_KR.UTF-8

# Update locale database
sudo update-locale LANG=ko_KR.UTF-8

# Add to shell configuration
echo '# Korean locale' >> ~/.bashrc
echo 'export LANG=ko_KR.UTF-8' >> ~/.bashrc
echo 'export LC_ALL=ko_KR.UTF-8' >> ~/.bashrc

# Reload
source ~/.bashrc

# Verify
locale
```

### **MoAI-ADK Locale Configuration**

```bash
# Create .env file in MoAI-ADK directory
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko

cat > .env << 'EOF'
# Korean Language Configuration
LANG=ko_KR.UTF-8
LC_ALL=ko_KR.UTF-8
LC_CTYPE=ko_KR.UTF-8

# Ensure UTF-8 encoding for all operations
PYTHONIOENCODING=utf-8
EOF

# Source .env when activating virtual environment
echo 'source .env' >> .venv/bin/activate
```

---

## 🔧 Character Encoding Configuration

### **Python UTF-8 Mode**

Ensure Python uses UTF-8 for all file operations:

```bash
# Add to shell configuration
echo '# Python UTF-8 mode' >> ~/.zshrc
echo 'export PYTHONUTF8=1' >> ~/.zshrc
echo 'export PYTHONIOENCODING=utf-8' >> ~/.zshrc

# Reload
source ~/.zshrc

# Verify
python3 -c "import sys; print(sys.getdefaultencoding())"
# Expected: utf-8
```

### **File Encoding Detection**

```bash
# Install file command (if not available)
# macOS
brew install file-formula

# Linux
sudo apt install file

# Check file encoding
file -I filename.txt

# Expected for Korean files:
# filename.txt: text/plain; charset=utf-8
```

### **MoAI-ADK File Encoding**

```python
# All MoAI-ADK files use UTF-8
# Verify in Python scripts:

# scripts/configure-agents.py
# -*- coding: utf-8 -*-

# Ensure file operations use UTF-8
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write("한글 테스트\n")
```

---

## ✅ Verification & Testing

### **Font Verification**

```bash
# Check D2Coding installation
fc-list | grep -i d2coding

# Expected output:
# /path/to/D2Coding.ttc: D2Coding:style=Regular
# /path/to/D2Coding.ttc: D2Coding:style=Bold

# Test in terminal
echo "폰트 테스트: 가나다라마바사아자차카타파하"
echo "Font test: ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ"
echo "Mixed: Hello 안녕하세요 123 456"

# All characters should display clearly
```

### **Locale Verification**

```bash
# Check locale settings
locale

# Verify Korean locale
locale | grep ko_KR.UTF-8

# Test Korean characters in command
echo "한글 테스트 성공!" | grep "성공"

# Expected output:
# 한글 테스트 성공!
```

### **Encoding Verification**

```bash
# Test UTF-8 encoding
python3 << 'EOF'
# -*- coding: utf-8 -*-
import sys
print(f"Default encoding: {sys.getdefaultencoding()}")
print(f"Filesystem encoding: {sys.getfilesystemencoding()}")
print(f"Korean test: 한글 테스트")

# Write Korean to file
with open('/tmp/korean-test.txt', 'w', encoding='utf-8') as f:
    f.write("MoAI-ADK 한글 지원 테스트\n")

# Read back
with open('/tmp/korean-test.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    print(f"File content: {content.strip()}")
EOF

# Expected output:
# Default encoding: utf-8
# Filesystem encoding: utf-8
# Korean test: 한글 테스트
# File content: MoAI-ADK 한글 지원 테스트
```

### **MoAI-ADK Korean Test**

```bash
# Activate MoAI-ADK environment
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko
source .venv/bin/activate

# Test with Korean command
./moai.sh /moai:0 "간단한 웹 서버 사양 작성"

# Expected: Proper Korean display in output

# Test Korean file operations
./moai.sh /moai:0 "사용자 관리 API 명세서 작성" > outputs/korean-spec.txt
cat outputs/korean-spec.txt

# Verify file encoding
file -I outputs/korean-spec.txt
# Expected: charset=utf-8
```

---

## 🐛 Troubleshooting Korean Support

### **Korean Characters Display as Boxes**

**Problem**: Korean text shows as `□□□`

**Solutions**:
```bash
# 1. Verify font installation
fc-list | grep -i d2coding

# 2. If not installed, install D2Coding
brew install --cask font-d2coding  # macOS
# or follow Linux instructions above

# 3. Configure terminal font to D2Coding

# 4. Restart terminal application
```

### **Mixed Character Width Issues**

**Problem**: Korean and English characters have inconsistent spacing

**Solutions**:
```bash
# iTerm2: Enable "Treat ambiguous characters as double-width"
# Preferences → Profiles → Text → Unicode

# GNOME Terminal: Use D2Coding font (auto-handles widths)

# Alacritty: Add to config:
# font:
#   offset:
#     x: 0
#     y: 0
```

### **Locale Not Set**

**Problem**: `locale: Cannot set LC_ALL to default locale`

**Solutions**:
```bash
# Generate Korean locale
sudo locale-gen ko_KR.UTF-8

# Update locale
sudo update-locale LANG=ko_KR.UTF-8

# Verify generation
locale -a | grep ko_KR

# Add to shell config
echo 'export LANG=ko_KR.UTF-8' >> ~/.bashrc
```

### **File Encoding Errors**

**Problem**: `UnicodeDecodeError` when reading Korean files

**Solutions**:
```python
# Always specify UTF-8 encoding
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Set Python UTF-8 mode
export PYTHONUTF8=1

# Verify file encoding
file -I file.txt  # Should show charset=utf-8
```

For additional troubleshooting, see `05-TROUBLESHOOTING.md`.

---

## 📚 Additional Resources

- **D2Coding Font**: https://github.com/naver/d2codingfont
- **Korean Locale Guide**: https://wiki.archlinux.org/title/Locale
- **UTF-8 Encoding**: https://en.wikipedia.org/wiki/UTF-8
- **CJK in Terminals**: https://en.wikipedia.org/wiki/CJK_characters

---

## 🎉 Success!

Your MoAI-ADK environment now has complete Korean language support! You can use Korean commands, comments, and documentation seamlessly.

**Test your setup**:
```bash
source .venv/bin/activate
./moai.sh /moai:0 "한국어로 할 수 있는 첫 번째 프로젝트 사양"
```

Happy coding in Korean! 🇰🇷🚀
