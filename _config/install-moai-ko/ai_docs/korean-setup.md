# Korean Language Setup (AI Documentation)

**Version**: 1.0.0
**Last Updated**: November 29, 2025
**Target**: AI Assistants

## Quick Summary

Korean language support for MoAI-ADK enables proper display and handling of Korean (Hangul) characters in terminal environments through D2Coding font installation and UTF-8 configuration.

**Status**: Optional (not required for English-only usage)

**Components**:
1. D2Coding font (Korean programming font)
2. Terminal configuration (font settings)
3. Korean locale (ko_KR.UTF-8)
4. UTF-8 encoding

---

## Why Korean Support?

### Problem Without Korean Support

```bash
# Without Korean font:
echo "한글 테스트"
# Output: □□ □□□  (boxes or question marks)

# Without UTF-8 encoding:
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

### With Korean Support

```bash
# With D2Coding font and UTF-8:
echo "한글 테스트"
# Output: 한글 테스트  (clear Korean characters)

# Korean commands work:
./moai.sh /moai:0 "사용자 관리 API 사양 작성"
# Generates specification in Korean
```

---

## D2Coding Font Installation

### macOS (Homebrew)

```bash
# Install D2Coding font
brew tap homebrew/cask-fonts
brew install --cask font-d2coding

# Verify installation
fc-list | grep -i d2coding

# Expected output:
# /Users/you/Library/Fonts/D2Coding.ttc: D2Coding:style=Regular
```

### Linux (Ubuntu/Debian)

```bash
# Download font
wget https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip

# Extract and install
unzip D2Coding-Ver1.3.2-20180524.zip
sudo mkdir -p /usr/share/fonts/truetype/d2coding
sudo cp D2Coding/D2Coding/*.ttf /usr/share/fonts/truetype/d2coding/

# Update font cache
sudo fc-cache -f -v

# Verify
fc-list | grep -i d2coding
```

### Windows (WSL2)

```bash
# Option 1: Install on Windows
# Download from: https://github.com/naver/d2codingfont/releases
# Double-click .ttf files to install
# WSL2 will inherit Windows fonts

# Option 2: Install in WSL2
wget https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip
unzip D2Coding-Ver1.3.2-20180524.zip
mkdir -p ~/.local/share/fonts
cp D2Coding/D2Coding/*.ttf ~/.local/share/fonts/
fc-cache -f -v
```

---

## Terminal Configuration

### Ghostty (Recommended)

Best terminal for Korean support.

**Configuration** (`~/.config/ghostty/config`):

```ini
# Font
font-family = "D2Coding"
font-size = 13

# Locale
locale = ko_KR.UTF-8

# Korean support
allow-alternate-screen = true
```

**Test**:
```bash
# Restart Ghostty, then test:
echo "한글 테스트: ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ"
# Should display clear Korean characters
```

### iTerm2 (macOS)

**Steps**:
1. Open Preferences (`⌘,`)
2. Profiles → Text
3. Change font to "D2Coding 13pt"
4. Set Character Encoding to "UTF-8"
5. Enable "Treat ambiguous characters as double-width"
6. Restart iTerm2

**Command-line config**:
```bash
# Set shell locale
echo 'export LANG=ko_KR.UTF-8' >> ~/.zshrc
source ~/.zshrc
```

### GNOME Terminal (Linux)

**GUI Configuration**:
1. Edit → Preferences
2. Profiles → Text
3. Select "D2Coding Regular 13"
4. Ensure UTF-8 encoding

**Command-line**:
```bash
# Set font via dconf
dconf write /org/gnome/terminal/legacy/profiles:/:UUID:/font "'D2Coding 13'"
dconf write /org/gnome/terminal/legacy/profiles:/:UUID:/use-system-font false
```

### Terminal.app (macOS)

**Steps**:
1. Preferences (`⌘,`)
2. Profiles → Text
3. Change font to "D2Coding Regular 13"
4. Advanced → Character encoding → UTF-8
5. Set as default profile

---

## Locale Configuration

### macOS

```bash
# Set Korean locale
echo 'export LANG=ko_KR.UTF-8' >> ~/.zshrc
echo 'export LC_ALL=ko_KR.UTF-8' >> ~/.zshrc
source ~/.zshrc

# Verify
locale | grep ko_KR

# Expected output:
# LANG=ko_KR.UTF-8
# LC_ALL=ko_KR.UTF-8
```

### Linux

```bash
# Generate Korean locale
sudo locale-gen ko_KR.UTF-8

# Update system locale
sudo update-locale LANG=ko_KR.UTF-8

# Add to shell config
echo 'export LANG=ko_KR.UTF-8' >> ~/.bashrc
echo 'export LC_ALL=ko_KR.UTF-8' >> ~/.bashrc
source ~/.bashrc

# Verify
locale -a | grep ko_KR
```

---

## UTF-8 Encoding

### Python UTF-8 Configuration

```bash
# Set Python UTF-8 mode
echo 'export PYTHONUTF8=1' >> ~/.zshrc
echo 'export PYTHONIOENCODING=utf-8' >> ~/.zshrc
source ~/.zshrc

# Verify
python3 -c "import sys; print(sys.getdefaultencoding())"
# Expected: utf-8
```

### MoAI-ADK `.env` Configuration

```bash
# Create/edit .env file
cat >> .env << 'EOF'
# Korean Language Configuration
LANG=ko_KR.UTF-8
LC_ALL=ko_KR.UTF-8
PYTHONIOENCODING=utf-8
PYTHONUTF8=1
EOF
```

### File Encoding

```python
# Always use explicit UTF-8 encoding in Python
with open('file.txt', 'w', encoding='utf-8') as f:
    f.write("한글 content")

with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()
```

---

## Verification Tests

### Font Verification

```bash
# Check D2Coding installation
fc-list | grep -i d2coding

# Expected output:
# /path/to/D2Coding.ttc: D2Coding:style=Regular
# /path/to/D2Coding.ttc: D2Coding:style=Bold

# Test Korean display
echo "폰트 테스트: 가나다라마바사아자차카타파하"

# If clear: ✅ Font working
# If boxes: ❌ Font not configured
```

### Locale Verification

```bash
# Check locale settings
locale

# Should include:
# LANG=ko_KR.UTF-8
# LC_ALL=ko_KR.UTF-8

# Test Korean grep
echo "한글 테스트" | grep "한글"

# Expected: "한글 테스트"
```

### Encoding Verification

```bash
# Test UTF-8 encoding
python3 << 'EOF'
import sys
print(f"Default encoding: {sys.getdefaultencoding()}")
print(f"Korean test: 한글 테스트")

# Write Korean to file
with open('/tmp/korean-test.txt', 'w', encoding='utf-8') as f:
    f.write("MoAI-ADK 한글 지원\n")

# Read back
with open('/tmp/korean-test.txt', 'r', encoding='utf-8') as f:
    print(f"File content: {f.read().strip()}")
EOF

# Expected output:
# Default encoding: utf-8
# Korean test: 한글 테스트
# File content: MoAI-ADK 한글 지원
```

### MoAI-ADK Korean Test

```bash
# Activate MoAI-ADK
source .venv/bin/activate

# Test Korean command
./moai.sh /moai:0 "간단한 할 일 목록 애플리케이션" > outputs/korean-spec.txt

# Check output
cat outputs/korean-spec.txt
# Should display Korean clearly

# Verify file encoding
file -I outputs/korean-spec.txt
# Expected: charset=utf-8
```

---

## Troubleshooting

### Problem: Korean Characters Show as Boxes

**Symptoms**:
```bash
echo "한글"
# Output: □□
```

**Solutions**:

1. **Install D2Coding font**:
   ```bash
   # macOS
   brew install --cask font-d2coding

   # Linux
   wget https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip
   unzip D2Coding-Ver1.3.2-20180524.zip
   sudo cp D2Coding/D2Coding/*.ttf /usr/share/fonts/truetype/
   sudo fc-cache -f -v
   ```

2. **Configure terminal font**:
   - Open terminal preferences
   - Change font to "D2Coding"
   - Size: 13 or larger
   - Restart terminal

3. **Verify font installation**:
   ```bash
   fc-list | grep -i d2coding
   ```

---

### Problem: Locale Not Set

**Symptoms**:
```bash
locale
# No ko_KR.UTF-8 shown
```

**Solutions**:

**macOS**:
```bash
echo 'export LANG=ko_KR.UTF-8' >> ~/.zshrc
echo 'export LC_ALL=ko_KR.UTF-8' >> ~/.zshrc
source ~/.zshrc
```

**Linux**:
```bash
sudo locale-gen ko_KR.UTF-8
sudo update-locale LANG=ko_KR.UTF-8
echo 'export LANG=ko_KR.UTF-8' >> ~/.bashrc
source ~/.bashrc
```

---

### Problem: File Encoding Errors

**Symptoms**:
```python
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

**Solutions**:

1. **Set Python UTF-8 mode**:
   ```bash
   export PYTHONUTF8=1
   export PYTHONIOENCODING=utf-8
   ```

2. **Always specify encoding**:
   ```python
   # Good
   with open('file.txt', 'r', encoding='utf-8') as f:
       content = f.read()

   # Bad
   with open('file.txt', 'r') as f:  # May use wrong encoding
       content = f.read()
   ```

3. **Convert file encoding**:
   ```bash
   # From EUC-KR to UTF-8
   iconv -f EUC-KR -t UTF-8 old.txt > new.txt
   ```

---

### Problem: Korean Input Not Working

**Symptoms**:
- Cannot type Korean characters
- Korean keyboard shows English

**Solutions**:

**macOS**:
1. System Settings → Keyboard → Input Sources
2. Add "Korean - 2-Set Korean"
3. Switch input: Control+Space

**Linux (Ubuntu)**:
```bash
# Install Korean input method
sudo apt install ibus ibus-hangul

# Configure
ibus-setup

# Add Hangul input method
# Settings → Input Sources → Add Korean (Hangul)
```

---

## D2Coding Font Details

### Font Specifications

| Property | Value |
|----------|-------|
| **Name** | D2Coding |
| **Version** | 1.3.2 |
| **Developer** | NAVER Corporation |
| **License** | OFL (Open Font License) |
| **Weights** | Regular (400), Bold (700) |
| **Size** | ~10 MB |

### Character Coverage

- **Hangul**: 11,172 modern Korean syllables
- **Latin**: A-Z, a-z, accented characters
- **Numbers**: 0-9 with clear distinction
- **Symbols**: Programming symbols, operators

### Key Features

1. **Clear Character Distinction**:
   - `0` vs `O` - Different shapes
   - `1` vs `l` vs `I` - Easily distinguished
   - `5` vs `S` - Clear difference

2. **Monospace**:
   - Korean = 2x Latin width
   - Perfect alignment in code

3. **Programming Optimized**:
   - Clear brackets: `{}` `[]` `()`
   - Distinct operators: `!= == >= <=`
   - Arrow ligatures: `-> =>`

### Character Display Test

```bash
cat << 'EOF'
Korean Font Test:

Consonants: ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ
Vowels: ㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣ
Words: 한글 테스트 MoAI-ADK 설치

Programming:
0O 1lI 5S 8B
!= == >= <= -> =>
{} [] () <>

Mixed:
const msg = "안녕하세요";
function greet() {
  console.log("Hello 세계");
}
EOF
```

---

## Korean Language Resources

### Hangul Basics

**Hangul Structure**:
- Consonants (자음): ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ
- Vowels (모음): ㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣ
- Syllable blocks: Combine consonants + vowels

**Examples**:
- 한 = ㅎ + ㅏ + ㄴ
- 글 = ㄱ + ㅡ + ㄹ
- 테 = ㅌ + ㅔ
- 스 = ㅅ + ㅡ
- 트 = ㅌ + ㅡ

### Common Korean Words in Programming

| Korean | English | Usage |
|--------|---------|-------|
| 사양 | Specification | ./moai.sh /moai:0 "사양 작성" |
| 테스트 | Test | ./moai.sh /moai:10 "테스트 명세" |
| 코드 | Code | 코드 리뷰 |
| 함수 | Function | 함수 정의 |
| 변수 | Variable | 변수 선언 |
| 클래스 | Class | 클래스 설계 |
| 메서드 | Method | 메서드 구현 |
| 데이터 | Data | 데이터 구조 |
| 서버 | Server | 서버 설정 |
| 클라이언트 | Client | 클라이언트 요청 |

---

## Quick Reference

### Installation Commands

```bash
# macOS
brew install --cask font-d2coding
echo 'export LANG=ko_KR.UTF-8' >> ~/.zshrc

# Linux
wget https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip
unzip D2Coding-Ver1.3.2-20180524.zip
sudo cp D2Coding/D2Coding/*.ttf /usr/share/fonts/truetype/
sudo fc-cache -f -v
sudo locale-gen ko_KR.UTF-8
echo 'export LANG=ko_KR.UTF-8' >> ~/.bashrc
```

### Verification Commands

```bash
# Check font
fc-list | grep -i d2coding

# Check locale
locale | grep ko_KR

# Check encoding
python3 -c "import sys; print(sys.getdefaultencoding())"

# Test Korean
echo "한글 테스트"
```

### MoAI-ADK Korean Commands

```bash
# SPEC-First
./moai.sh /moai:0 "사용자 관리 시스템 사양"

# TDD
./moai.sh /moai:10 "로그인 기능 테스트"

# Code Review
./moai.sh /moai:30 "$(cat src/app.js)" --lang ko
```

---

## Related Documentation

- **Full Korean Setup**: `../docs/03-KOREAN-SETUP.md`
- **Font Details**: `../docs/api/korean-fonts.md`
- **MoAI-ADK Guide**: `moai-adk-guide.md`
- **Installation**: `../docs/02-INSTALLATION.md`

---

**Korean Language Support for MoAI-ADK** - Clear Korean character display for developers 🇰🇷
