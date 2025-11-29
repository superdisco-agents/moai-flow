#!/bin/bash
# MoAI-ADK 한글 환경 자동 설정 스크립트

echo "=== MoAI-ADK 한글 환경 설정 시작 ==="
echo ""

# 1. D2Coding 폰트 설치 (수정됨: Homebrew cask-fonts tap 불필요)
echo "1️⃣ D2Coding 한글 폰트 설치 중..."
echo "   📌 참고: D2Coding Nerd Font는 프로그래밍 아이콘과 ligature를 포함합니다"
brew install --cask font-d2coding-nerd-font

# 2. Ghostty 설정 디렉토리 생성
echo "2️⃣ Ghostty 설정 디렉토리 생성 중..."
mkdir -p ~/.config/ghostty

# 3. Ghostty 설정 파일 업데이트
echo "3️⃣ Ghostty 한글 폰트 설정 추가 중..."
if [ -f ~/.config/ghostty/config ]; then
    # 기존 파일 백업
    cp ~/.config/ghostty/config ~/.config/ghostty/config.backup
    echo "   기존 설정 백업: ~/.config/ghostty/config.backup"
fi

# 한글 폰트 설정 추가
cat >> ~/.config/ghostty/config << 'EOF'

# MoAI-ADK 한글 폰트 설정
font-family = "D2CodingLigature Nerd Font"
font-family = "JetBrains Mono"
font-size = 14
font-feature = "calt"
font-feature = "liga"
EOF

echo "   Ghostty 설정 업데이트 완료"

# 4. 폰트 설치 확인
echo "4️⃣ 폰트 설치 확인 중..."
if fc-list 2>/dev/null | grep -q "D2Coding"; then
    echo "   ✅ D2Coding 폰트 설치 확인됨"
else
    echo "   ⚠️  D2Coding 폰트가 감지되지 않습니다"
    echo "   Ghostty를 재시작하면 적용됩니다"
fi

# 5. 한글 테스트
echo ""
echo "5️⃣ 한글 폰트 테스트:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   한글 테스트 - Korean Test"
echo "   프로그래밍: const 변수명 = 'value';"
echo "   함수 function() { return true; }"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "✅ 한글 환경 설정 완료!"
echo ""
echo "📌 다음 단계:"
echo "   1. Ghostty 재시작 (Cmd+Shift+, 또는 재시작)"
echo "   2. 위의 한글 텍스트가 제대로 보이는지 확인"
echo "   3. MoAI-ADK 설치 진행: cat INSTALL-MOAI-ADK.md"
echo ""
