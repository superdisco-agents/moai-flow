# Ghostty 한글 폰트 간격 문제 해결 가이드

**생성일**: 2025년 11월 28일  
**문제**: D2Coding Nerd Font에서 한글 글자 간격이 너무 넓게 표시됨

---

## 🎯 핵심 원인

**Nerd Font 패치 과정에서 CJK Compatibility Ideographs 영역에 글리프가 추가되면서 한글 간격이 깨짐**

- D2Coding Nerd Font: ❌ 간격 문제 발생
- D2Coding (원본): ✅ 정상적인 간격

---

## ✅ 해결방법 1: Sarasa Term K (권장)

**Sarasa Gothic**은 CJK 프로그래밍에 최적화된 폰트입니다.

### 설치

```bash
# Sarasa Gothic 설치 (모든 변형 포함)
brew install --cask font-sarasa-gothic

# 프로그래밍 아이콘용 Symbols Nerd Font 설치
brew install --cask font-symbols-only-nerd-font
```

### Ghostty 설정

```bash
# ~/.config/ghostty/config

# === 폰트 렌더링 ===
# Sarasa Term K - 한글 간격이 완벽한 CJK 프로그래밍 폰트
# Symbols Nerd Font Mono - 프로그래밍 아이콘
font-family = "Sarasa Term K"
font-family = "Symbols Nerd Font Mono"
font-family = "Apple SD Gothic Neo"
font-size = 14

# 한글 렌더링을 위한 간격 조정
adjust-cell-width = -2%
grapheme-width-method = unicode

# 폰트 기능
font-feature = "calt"
font-feature = "liga"
```

---

## 🧪 테스트 방법

### 1. Ghostty 재시작

```bash
# Ghostty 완전 종료 후 재시작
pkill Ghostty && sleep 1 && open -a Ghostty
```

### 2. 한글 간격 테스트

```bash
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "한글 테스트 - Korean Test"
echo "설정 업데이트 완료!"
echo "const 변수명 = 'value';"
echo "function 테스트함수() { return true; }"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

---

## 📚 참고 자료

- **Sarasa Gothic**: https://github.com/be5invis/Sarasa-Gothic
- **Ghostty 설정**: https://ghostty.org/docs/config/font
- **문서 위치**: `_config/MOAI-ADK-KO/docs/ghostty-korean-font-spacing.md`

---

**문서 버전**: 1.0.0  
**최종 업데이트**: 2025년 11월 28일
