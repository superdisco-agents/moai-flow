---
description: Execute MoAI-ADK installation with Korean language support
tags: [moai, install, korean, i18n]
---

# Install Korean: MoAI-ADK with Korean Support

Execute complete MoAI-ADK installation with Korean fonts, terminal configuration, and locale setup.

## Progressive Disclosure Structure

### Level 1: Quick Start (Immediate Action)

Execute the `installer` agent with Korean support enabled:

```bash
# Spawn installer agent for Korean installation
installer --mode korean --fonts d2coding --terminal ghostty --locale ko_KR.UTF-8
```

**Expected Duration**: 10-15 minutes
**What Gets Installed**:
- MoAI-ADK Python package (26 agents)
- D2Coding font (Korean monospace)
- Ghostty terminal configuration
- Korean locale (ko_KR.UTF-8)
- Noto Sans KR (UI font)

### Level 2: Korean Support Overview

**Why Korean Support?**
- Proper rendering of Korean characters in terminal
- Optimized monospace font for coding with Hangul
- UTF-8 locale for correct string handling
- Korean error messages and logging

**Components Installed**:
1. **D2Coding Font** - Monospace font designed for Korean coding
2. **Ghostty Terminal** - Modern terminal with excellent Korean support
3. **Noto Sans KR** - Korean UI font for applications
4. **Locale Configuration** - ko_KR.UTF-8 for proper encoding

### Level 3: Installation Workflow (Detailed Steps)

**Phase 1: Standard Installation** (inherits from `/install`)
```bash
# Execute standard installation first
npx claude-flow@alpha hooks pre-task --description "MoAI-ADK Korean installation"

# Run standard installation steps
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko

# Verify Python and uv
python --version  # 3.13+
uv --version || curl -LsSf https://astral.sh/uv/install.sh | sh

# Install MoAI-ADK
uv sync --all-extras
source .venv/bin/activate
```

**Phase 2: Korean Font Installation**
```bash
# Detect operating system
os_type=$(uname -s)

case "$os_type" in
  Darwin)
    # macOS: Install D2Coding via Homebrew
    echo "Installing D2Coding font on macOS..."
    if ! command -v brew &> /dev/null; then
      echo "Installing Homebrew..."
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    brew tap homebrew/cask-fonts
    brew install --cask font-d2coding
    brew install --cask font-noto-sans-cjk-kr

    echo "✓ D2Coding and Noto Sans KR installed"
    ;;

  Linux)
    # Linux: Install via package manager or manual download
    echo "Installing D2Coding font on Linux..."

    # Create fonts directory
    mkdir -p ~/.local/share/fonts

    # Download D2Coding
    d2coding_url="https://github.com/naver/d2codingfont/releases/latest/download/D2Coding-Ver1.3.2-20180524.zip"
    curl -L "$d2coding_url" -o /tmp/d2coding.zip
    unzip -o /tmp/d2coding.zip -d /tmp/d2coding
    cp /tmp/d2coding/*.ttf ~/.local/share/fonts/

    # Download Noto Sans KR
    noto_url="https://github.com/google/fonts/raw/main/ofl/notosanskr/NotoSansKR%5Bwght%5D.ttf"
    curl -L "$noto_url" -o ~/.local/share/fonts/NotoSansKR.ttf

    # Update font cache
    fc-cache -f -v

    echo "✓ D2Coding and Noto Sans KR installed"
    ;;

  *)
    echo "⚠ Unsupported OS: $os_type"
    echo "Please install D2Coding font manually"
    ;;
esac

# Verify font installation
if fc-list | grep -i "d2coding" > /dev/null; then
  echo "✓ D2Coding font verified"
else
  echo "⚠ Warning: D2Coding font not found in system fonts"
fi
```

**Phase 3: Ghostty Terminal Configuration**
```bash
# Install Ghostty (if not already installed)
echo "Configuring Ghostty terminal..."

case "$os_type" in
  Darwin)
    # macOS: Install via Homebrew
    if ! command -v ghostty &> /dev/null; then
      echo "Installing Ghostty..."
      brew install --cask ghostty
    fi

    # Ghostty config location
    ghostty_config="$HOME/.config/ghostty/config"
    ;;

  Linux)
    # Linux: Check if Ghostty is installed
    if ! command -v ghostty &> /dev/null; then
      echo "⚠ Ghostty not found. Install from: https://ghostty.org"
      echo "Skipping Ghostty configuration..."
      exit 0
    fi

    ghostty_config="$HOME/.config/ghostty/config"
    ;;
esac

# Create Ghostty configuration directory
mkdir -p "$(dirname "$ghostty_config")"

# Write Ghostty configuration with Korean support
cat > "$ghostty_config" << 'EOF'
# Ghostty Terminal Configuration - Korean Support

# Font Configuration
font-family = "D2Coding"
font-size = 14
font-feature = -calt  # Disable ligatures for Korean

# Korean Character Support
font-family-bold = "D2Coding"
font-family-italic = "D2Coding"
font-family-bold-italic = "D2Coding"

# UTF-8 Support
locale = "ko_KR.UTF-8"

# Terminal Settings
shell-integration = true
shell-integration-features = cursor,sudo

# Color Scheme (Korean-optimized contrast)
theme = "tokyo-night"
background-opacity = 0.95

# Window Settings
window-padding-x = 8
window-padding-y = 8
window-theme = dark

# Cursor Settings
cursor-style = block
cursor-style-blink = true

# Korean Input Method Support
macos-option-as-alt = true

# Performance
resize-overlay = never
EOF

echo "✓ Ghostty configured with D2Coding font"
```

**Phase 4: Korean Locale Configuration**
```bash
# Set Korean locale
echo "Configuring Korean locale (ko_KR.UTF-8)..."

case "$os_type" in
  Darwin)
    # macOS: Set system locale
    defaults write -g AppleLocale "ko_KR"
    defaults write -g AppleLanguages "(ko-KR, en-US)"

    # Add to shell profile
    shell_profile="$HOME/.zshrc"
    if [ -f "$HOME/.bashrc" ]; then
      shell_profile="$HOME/.bashrc"
    fi

    if ! grep -q "LC_ALL=ko_KR.UTF-8" "$shell_profile"; then
      cat >> "$shell_profile" << 'EOF'

# Korean Locale for MoAI-ADK
export LC_ALL=ko_KR.UTF-8
export LANG=ko_KR.UTF-8
export LANGUAGE=ko_KR.UTF-8
EOF
    fi

    echo "✓ Korean locale configured (restart terminal to apply)"
    ;;

  Linux)
    # Linux: Generate and set locale
    if command -v locale-gen &> /dev/null; then
      sudo locale-gen ko_KR.UTF-8
      sudo update-locale LANG=ko_KR.UTF-8
    fi

    # Add to shell profile
    shell_profile="$HOME/.bashrc"
    if ! grep -q "LC_ALL=ko_KR.UTF-8" "$shell_profile"; then
      cat >> "$shell_profile" << 'EOF'

# Korean Locale for MoAI-ADK
export LC_ALL=ko_KR.UTF-8
export LANG=ko_KR.UTF-8
export LANGUAGE=ko_KR.UTF-8
EOF
    fi

    echo "✓ Korean locale configured"
    ;;
esac

# Verify locale
if locale -a | grep -i "ko_KR.utf8" > /dev/null; then
  echo "✓ Korean locale verified"
else
  echo "⚠ Warning: Korean locale may not be available"
fi
```

**Phase 5: Korean Support Validation**
```bash
# Test Korean rendering
echo "Testing Korean character rendering..."

# Create test script
cat > /tmp/korean_test.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=" * 50)
print("MoAI-ADK 한글 지원 테스트")
print("=" * 50)
print()
print("✓ 한글 출력 테스트 성공")
print("✓ 유니코드 인코딩: UTF-8")
print("✓ D2Coding 폰트 렌더링 확인")
print()
print("Agent Names (Korean):")
print("  - 계층적 조정자 (Hierarchical Coordinator)")
print("  - 성능 분석기 (Performance Analyzer)")
print("  - 테스트 담당자 (Tester)")
print()
print("=" * 50)
EOF

# Run test
python /tmp/korean_test.py

# Verify font rendering in Ghostty
echo ""
echo "Korean Font Test (view in Ghostty terminal):"
echo "한글 테스트: 가나다라마바사아자차카타파하"
echo "Hangul Test: ABCDEFGHIJKLMNOPQRSTUVWXYZ"
echo "Monospace: 한글 English 123 !@#"

# Update coordination hooks
npx claude-flow@alpha hooks post-task --task-id "moai-adk-korean-install"
```

### Level 4: Troubleshooting (Korean-Specific)

**Issue 1: Korean Characters Show as Boxes**
```bash
Problem: □□□ instead of 한글
Solution: Font not installed or not selected in terminal

# Verify D2Coding installation
fc-list | grep -i d2coding

# If missing, reinstall
brew reinstall --cask font-d2coding  # macOS
fc-cache -f -v  # Linux
```

**Issue 2: Ghostty Won't Start**
```bash
Problem: Ghostty crashes on launch
Solution: Check configuration syntax

# Validate config
cat ~/.config/ghostty/config | grep -v "^#" | grep -v "^$"

# Reset to defaults
mv ~/.config/ghostty/config ~/.config/ghostty/config.backup
ghostty  # Will create new default config
```

**Issue 3: Locale Not Applied**
```bash
Problem: locale still shows en_US
Solution: Restart terminal or re-source profile

# Check current locale
locale

# Re-source profile
source ~/.zshrc  # or ~/.bashrc

# Verify
echo $LANG  # Should show ko_KR.UTF-8
```

**Issue 4: Korean Input Not Working**
```bash
Problem: Cannot type Korean characters
Solution: Enable system input method

# macOS: System Preferences > Keyboard > Input Sources
# Add "Korean - 2-Set Korean"

# Linux: Install ibus-hangul
sudo apt install ibus-hangul  # Debian/Ubuntu
sudo dnf install ibus-hangul  # Fedora
```

### Level 5: Expert Mode (Custom Korean Setup)

**Custom Font Configuration**:
```bash
# Use custom Korean font instead of D2Coding
cat > ~/.config/ghostty/config << EOF
font-family = "JetBrains Mono"
font-fallback = "Noto Sans CJK KR"
font-size = 13
EOF
```

**Multiple Locale Support**:
```bash
# Support both Korean and English
export LC_ALL=ko_KR.UTF-8
export LANG=ko_KR.UTF-8
export LC_MESSAGES=en_US.UTF-8  # English error messages
```

**Korean Error Messages**:
```python
# Configure MoAI-ADK for Korean logging
import moai_adk
moai_adk.configure(
    locale="ko_KR",
    log_language="korean",
    error_messages="korean"
)
```

## Post-Installation Verification

**Run Korean validation**:
```bash
/verify --korean-fonts true
```

**Test in Ghostty**:
```bash
# Open new Ghostty terminal
ghostty

# Run Korean test
python -c "print('한글 테스트: MoAI-ADK 설치 완료')"
```

## Success Criteria

Korean installation is successful when:
- ✓ All 26 agents installed and verified
- ✓ D2Coding font installed and active
- ✓ Ghostty terminal configured
- ✓ Korean locale (ko_KR.UTF-8) active
- ✓ Korean characters render correctly
- ✓ Korean input method available

## Next Steps

1. Restart terminal to apply locale changes
2. Open Ghostty and verify Korean rendering
3. Run `/verify --korean-fonts true`
4. Test Korean input: `python -m moai_adk.cli --lang ko`

---

**Installation Type**: Korean Support (extends standard)
**Estimated Time**: 10-15 minutes
**Agent**: `installer` (Sonnet 4.5, Korean mode)
**Korean Components**: D2Coding, Ghostty, ko_KR.UTF-8, Noto Sans KR
