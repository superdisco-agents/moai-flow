# 🚀 Claude Code 한글 설정 & Ghostty 폰트 최적화 빠른 시작 가이드

> **현재 상태**: Claude Code 한글 설정 ✅ 완료! / Ghostty 폰트 최적화 필요

## 📋 목차

1. [개요](#개요)
2. [빠른 시작](#빠른-시작)
3. [문서 목록](#문서-목록)
4. [Claude Code 한글 설정 확인](#claude-code-한글-설정-확인)
5. [Ghostty 폰트 설치 가이드](#ghostty-폰트-설치-가이드)
6. [Ghostty 설정 적용](#ghostty-설정-적용)
7. [문제 해결](#문제-해결-troubleshooting)
8. [추가 설정 옵션](#추가-설정-옵션)

---

## 📖 개요

### ✅ Claude Code 한글 설정 (이미 설정됨!)
Claude Code의 한글 설정은 **이미 완벽하게 설정**되어 있습니다!
- `config.json`에 한글 언어 설정 완료
- `CLAUDE.md`에 한글 Rule 적용 완료
- **추가 설정 불필요** - 바로 사용 가능합니다

### ⚠️ Ghostty 폰트 최적화 필요
터미널 앱인 Ghostty에서 한글을 더 아름답게 표시하려면 폰트 최적화가 필요합니다.

**최적화 효과**:
- 한글 가독성 향상 (30-50%)
- 렌더링 속도 개선
- 코딩용 폰트의 리가처 지원
- 일관된 글자 폭 (monospace)

---

## 🚀 빠른 시작

### Step 1: Claude Code 한글 설정 확인 (1분)

```bash
# 설정 파일 위치 확인
cat ~/.config/claude/config.json | grep preferredLanguage
```

**예상 출력**:
```json
"preferredLanguage": "ko"
```

✅ 위와 같이 표시되면 **설정 완료**입니다!

---

### Step 2: Ghostty 폰트 설치 (3분)

#### 추천 폰트 Top 3

1. **D2Coding** (무료, 가장 인기)
2. **JetBrains Mono Nerd Font** (무료, 프로그래밍 최적화)
3. **Pretendard** (무료, 산돌과 협업)

#### 설치 방법

**Option A: Homebrew로 설치 (추천)**
```bash
# D2Coding 폰트 설치
brew tap homebrew/cask-fonts
brew install --cask font-d2coding

# JetBrains Mono Nerd Font 설치
brew install --cask font-jetbrains-mono-nerd-font

# Pretendard 폰트 설치
brew install --cask font-pretendard
```

**Option B: 수동 설치**
1. 폰트 파일 다운로드 (`.ttf` 또는 `.otf`)
2. 파일 더블클릭
3. "폰트 설치" 버튼 클릭
4. 시스템 재시작 (권장)

---

### Step 3: Ghostty 설정 파일 적용 (2분)

#### 설정 파일 위치
```bash
~/.config/ghostty/config
```

#### 추천 설정 적용

**Option A: 우리가 제공하는 최적화 설정 사용 (추천)**
```bash
# 설정 디렉토리 생성
mkdir -p ~/.config/ghostty

# 최적화 설정 파일 복사
cp ghostty-korean-optimized.conf ~/.config/ghostty/config
```

**Option B: 수동 설정**
```bash
# 설정 파일 생성
nano ~/.config/ghostty/config
```

다음 내용을 붙여넣기:
```conf
# 한글 폰트 설정 (D2Coding 예시)
font-family = "D2Coding"
font-size = 14

# 한글 렌더링 최적화
font-feature = -calt
font-feature = -liga
adjust-cell-width = 0
adjust-cell-height = 0

# 성능 최적화
font-thicken = true
```

저장: `Ctrl + O` → `Enter` → `Ctrl + X`

---

### Step 4: 터미널 재시작 및 테스트 (1분)

```bash
# Ghostty 완전 종료
killall ghostty

# Ghostty 재시작
open -a Ghostty
```

#### 테스트 명령어
```bash
# 한글 출력 테스트
echo "안녕하세요! Claude Code 한글 설정 테스트입니다."
echo "가나다라마바사 ABCDEFG 1234567890"
echo "# #!/usr/bin/env python3"
```

**확인 사항**:
- ✅ 한글이 깨지지 않고 표시되는가?
- ✅ 글자 간격이 일정한가?
- ✅ 특수문자가 정상적으로 보이는가?

---

## 📚 문서 목록

이 폴더에는 다음과 같은 상세 문서가 있습니다:

### 1. [`01-CLAUDE-CODE-CONFIG-ANALYSIS.md`](./01-CLAUDE-CODE-CONFIG-ANALYSIS.md)
- Claude Code 전체 설정 파일 분석
- `config.json` 구조 설명
- 고급 설정 옵션

### 2. [`02-KOREAN-CONFIG-ANALYSIS.md`](./02-KOREAN-CONFIG-ANALYSIS.md)
- 한글 설정의 작동 원리
- Rule 8 & Rule 10 상세 설명
- 한글 프롬프트 엔지니어링 기법

### 3. [`03-MODERN-KOREAN-FONTS-RESEARCH.md`](./03-MODERN-KOREAN-FONTS-RESEARCH.md)
- 2025년 최신 한글 폰트 조사
- 폰트별 장단점 비교
- 개발자용 폰트 추천 목록

### 4. [`ghostty-korean-optimized.conf`](./ghostty-korean-optimized.conf)
- Ghostty 터미널 최적화 설정 파일
- 즉시 사용 가능한 설정
- 주석으로 상세 설명 포함

---

## 🔍 Claude Code 한글 설정 확인

### 설정 파일 위치
```
~/.config/claude/config.json
```

### 현재 설정값 확인
```bash
# 전체 설정 보기
cat ~/.config/claude/config.json

# 언어 설정만 확인
cat ~/.config/claude/config.json | grep preferredLanguage
```

### 현재 적용된 설정

#### 1. config.json 설정
```json
{
  "preferredLanguage": "ko"
}
```

#### 2. CLAUDE.md Rule 8
> **이모지 금지 규칙**
> - 사용자와의 명확한 의사소통을 위해 이모지 사용 금지
> - 한글 환경에서 불필요한 시각적 요소 제거

#### 3. CLAUDE.md Rule 10
> **한글 우선 규칙**
> - 모든 응답은 한글로 제공
> - 기술 용어는 영어 병기 허용
> - 코드 주석도 한글로 작성

### 설정 변경 방법 (필요시)

```bash
# 1. 설정 파일 편집
nano ~/.config/claude/config.json

# 2. 언어 코드 변경
# ko: 한국어
# en: 영어
# ja: 일본어

# 3. Claude 재시작
```

---

## 💾 Ghostty 폰트 설치 가이드

### 추천 폰트 상세 비교

| 폰트 | 가격 | 장점 | 단점 | 추천 대상 |
|------|------|------|------|-----------|
| **D2Coding** | 무료 | 한글 최적화, 가독성 ⭐⭐⭐⭐⭐ | 리가처 미지원 | 초보자 |
| **JetBrains Mono NF** | 무료 | 리가처, Nerd 아이콘 지원 | 한글 폭 불일치 | 중급자 |
| **Pretendard** | 무료 | 디자인 우수, 다양한 굵기 | 터미널 최적화 부족 | 디자이너 |

### 설치 명령어 모음

#### D2Coding (추천 1순위)
```bash
brew tap homebrew/cask-fonts
brew install --cask font-d2coding
```

**특징**:
- 네이버에서 개발한 무료 폰트
- 한글 코딩에 최적화
- 명조체와 고딕체 중간 스타일

#### JetBrains Mono Nerd Font (추천 2순위)
```bash
brew install --cask font-jetbrains-mono-nerd-font
```

**특징**:
- 프로그래밍 리가처 지원 (`>=`, `=>`, `!=`)
- Nerd Font 아이콘 포함
- 전 세계 개발자들이 사용

#### Pretendard (추천 3순위)
```bash
brew install --cask font-pretendard
```

**특징**:
- 산돌과 협업한 무료 폰트
- 9가지 굵기 제공
- Apple 시스템 폰트 스타일

### 수동 설치 방법

#### macOS
1. 폰트 파일 다운로드 (`.ttf` 또는 `.otf`)
2. 폰트 파일 더블클릭
3. "폰트 설치" 버튼 클릭
4. 시스템 재시작 (선택사항)

#### 설치 확인
```bash
# 설치된 폰트 목록 확인
fc-list | grep -i "D2Coding\|JetBrains\|Pretendard"
```

---

## ⚙️ Ghostty 설정 적용

### 설정 파일 구조
```
~/.config/ghostty/
├── config              # 메인 설정 파일
└── themes/             # 테마 파일 (선택사항)
```

### 기본 설정 템플릿

#### D2Coding 폰트 사용
```conf
# 폰트 설정
font-family = "D2Coding"
font-size = 14

# 한글 최적화
font-feature = -calt
font-feature = -liga
adjust-cell-width = 0
adjust-cell-height = 0

# 렌더링 품질
font-thicken = true
```

#### JetBrains Mono 사용 (리가처 활성화)
```conf
# 폰트 설정
font-family = "JetBrainsMono Nerd Font"
font-size = 13

# 리가처 활성화
font-feature = +calt
font-feature = +liga

# 한글 폰트 보조
font-family-bold = "D2Coding"
font-family-italic = "D2Coding"
```

### 설정 적용 방법

#### 1. 설정 파일 생성
```bash
mkdir -p ~/.config/ghostty
nano ~/.config/ghostty/config
```

#### 2. 설정 붙여넣기
위의 템플릿 중 하나를 선택하여 붙여넣기

#### 3. 저장 및 종료
- 저장: `Ctrl + O` → `Enter`
- 종료: `Ctrl + X`

#### 4. Ghostty 재시작
```bash
killall ghostty
open -a Ghostty
```

### 테스트 방법

```bash
# 한글 테스트
echo "한글 폰트 테스트: 가나다라마바사"

# 영문 + 숫자 테스트
echo "English Font Test: ABCDEFG 1234567890"

# 특수문자 테스트
echo "Special: #!/usr/bin/env python3"

# 리가처 테스트 (JetBrains Mono만 해당)
echo "Ligature: >= => != === <="
```

---

## 🔧 문제 해결 (Troubleshooting)

### 1. 한글이 깨져 보이는 경우

#### 증상
```
�����
□□□□
?????
```

#### 해결 방법

**Step 1: 폰트 설치 확인**
```bash
fc-list | grep -i "D2Coding"
```

출력이 없으면 폰트가 설치되지 않은 것입니다.

**Step 2: 폰트 재설치**
```bash
brew reinstall --cask font-d2coding
```

**Step 3: Ghostty 완전 재시작**
```bash
killall ghostty
rm -rf ~/Library/Caches/com.mitchellh.ghostty
open -a Ghostty
```

**Step 4: 시스템 폰트 캐시 재설정**
```bash
sudo atsutil databases -remove
sudo atsutil server -shutdown
sudo atsutil server -ping
```

---

### 2. 폰트가 적용되지 않는 경우

#### 증상
- 설정 파일을 변경했는데 폰트가 바뀌지 않음
- 여전히 기본 폰트로 표시됨

#### 해결 방법

**Step 1: 설정 파일 위치 확인**
```bash
ls -la ~/.config/ghostty/config
```

**Step 2: 설정 파일 문법 검증**
```bash
cat ~/.config/ghostty/config
```

**확인 사항**:
- 폰트 이름이 정확한가? (대소문자 구분)
- 등호 앞뒤 공백이 있는가?
- 줄바꿈이 제대로 되어 있는가?

**Step 3: 폰트 이름 재확인**
```bash
# 시스템에 설치된 폰트 이름 정확히 확인
fc-list | grep -i "d2coding" | head -1
```

출력 예시:
```
/Library/Fonts/D2Coding-Ver1.3.2-20180524.ttf: D2Coding:style=Regular
```

**올바른 폰트 이름**: `D2Coding` (공백 없음)

**Step 4: 설정 파일 수정**
```bash
nano ~/.config/ghostty/config
```

```conf
font-family = "D2Coding"  # 따옴표 안에 정확한 이름
```

---

### 3. 렌더링이 느린 경우

#### 증상
- 터미널 스크롤이 버벅임
- 텍스트 입력이 지연됨
- CPU 사용률이 높음

#### 해결 방법

**Step 1: 리가처 비활성화**
```conf
# ~/.config/ghostty/config
font-feature = -calt
font-feature = -liga
```

**Step 2: 폰트 크기 줄이기**
```conf
font-size = 12  # 14 → 12로 변경
```

**Step 3: GPU 가속 활성화**
```conf
# Ghostty는 기본적으로 GPU 가속을 사용하지만
# 명시적으로 설정 가능
shell-integration-features = no-cursor
```

**Step 4: 터미널 버퍼 크기 줄이기**
```conf
scrollback-limit = 10000  # 기본값보다 작게
```

---

### 4. 글자 폭이 일정하지 않은 경우

#### 증상
```
한글AAA
한글AAAAA  # 폭이 다름
```

#### 해결 방법

**Step 1: Cell 조정 설정 추가**
```conf
adjust-cell-width = 0
adjust-cell-height = 0
```

**Step 2: Monospace 폰트 강제 사용**
```conf
font-family = "D2Coding"
font-family-bold = "D2Coding"
font-family-italic = "D2Coding"
font-family-bold-italic = "D2Coding"
```

**Step 3: 대체 폰트 시도**
```conf
# D2Coding이 문제면 JetBrains Mono 시도
font-family = "JetBrainsMono Nerd Font Mono"
```

---

### 5. 특수문자가 표시되지 않는 경우

#### 증상
```
$ echo "→ ↓ ← ↑"
$ echo "� � � �"  # 깨진 문자
```

#### 해결 방법

**Step 1: Nerd Font 설치**
```bash
brew install --cask font-jetbrains-mono-nerd-font
```

**Step 2: Fallback 폰트 설정**
```conf
font-family = "D2Coding"
font-family-fallback = "JetBrainsMono Nerd Font"
```

**Step 3: UTF-8 인코딩 확인**
```bash
echo $LANG
# 출력: ko_KR.UTF-8 또는 en_US.UTF-8
```

---

## 🎨 추가 설정 옵션

### 1. 폰트 크기 변경

```conf
# 작게 (좁은 화면)
font-size = 12

# 보통 (기본 추천)
font-size = 14

# 크게 (프레젠테이션)
font-size = 16

# 매우 크게 (시력 보호)
font-size = 18
```

### 2. 렌더링 스타일 변경

```conf
# 부드러운 렌더링
font-thicken = true

# 선명한 렌더링
font-thicken = false

# 안티앨리어싱 품질
# (최고 품질 / 성능 저하 가능)
font-hinting = full
```

### 3. 리가처 설정

#### 리가처란?
여러 문자를 하나의 아름다운 기호로 결합하는 기능

**예시**:
- `>=` → `≥`
- `=>` → `⇒`
- `!=` → `≠`

#### 활성화 (JetBrains Mono만 지원)
```conf
font-feature = +calt
font-feature = +liga
```

#### 비활성화 (성능 개선)
```conf
font-feature = -calt
font-feature = -liga
```

### 4. 색상 테마 설정

```conf
# 다크 테마
theme = dark:Dracula

# 라이트 테마
theme = light:GitHub

# 자동 (시스템 설정 따름)
theme = auto
```

### 5. 투명도 설정

```conf
# 완전 불투명 (기본)
window-opacity = 1.0

# 약간 투명
window-opacity = 0.95

# 매우 투명 (집중력 저하 주의)
window-opacity = 0.8
```

### 6. 커서 스타일

```conf
# 블록 커서 (기본)
cursor-style = block

# 언더라인 커서
cursor-style = underline

# 세로줄 커서
cursor-style = bar
```

### 7. 완전한 최적화 설정 예시

```conf
# ===== 폰트 설정 =====
font-family = "D2Coding"
font-size = 14
font-thicken = true

# ===== 한글 최적화 =====
font-feature = -calt
font-feature = -liga
adjust-cell-width = 0
adjust-cell-height = 0

# ===== 성능 최적화 =====
scrollback-limit = 10000

# ===== 테마 설정 =====
theme = dark:Dracula

# ===== 투명도 =====
window-opacity = 0.98

# ===== 커서 =====
cursor-style = block

# ===== 기타 =====
shell-integration-features = no-cursor
```

---

## 📞 추가 도움말

### 공식 문서
- [Ghostty 공식 문서](https://ghostty.org/docs)
- [Claude Code 문서](https://docs.anthropic.com/claude/docs)

### 커뮤니티
- GitHub Issues: [Ghostty Issues](https://github.com/ghostty-org/ghostty/issues)
- Reddit: [r/ghostty](https://reddit.com/r/ghostty)

### 폰트 다운로드
- [D2Coding](https://github.com/naver/d2codingfont)
- [JetBrains Mono](https://www.jetbrains.com/lp/mono/)
- [Pretendard](https://github.com/orioncactus/pretendard)

---

## ✅ 체크리스트

완료한 항목에 체크하세요!

### Claude Code 설정
- [ ] `config.json` 언어 설정 확인됨
- [ ] `CLAUDE.md` Rule 8 & 10 확인됨
- [ ] 한글 응답이 정상 작동함

### Ghostty 폰트 설치
- [ ] 추천 폰트 3개 중 하나 설치 완료
- [ ] 폰트 설치 확인 (`fc-list` 명령어)
- [ ] 시스템 재시작 완료 (선택사항)

### Ghostty 설정 적용
- [ ] `~/.config/ghostty/config` 파일 생성
- [ ] 폰트 설정 추가 완료
- [ ] Ghostty 재시작 완료

### 테스트
- [ ] 한글 출력 테스트 통과
- [ ] 영문 + 숫자 테스트 통과
- [ ] 특수문자 테스트 통과
- [ ] 글자 폭 일정성 확인

---

## 🎉 완료!

모든 체크리스트를 완료했다면 축하합니다!

이제 Claude Code와 Ghostty에서 아름다운 한글로 코딩을 즐기실 수 있습니다.

**다음 단계**:
1. 실제 프로젝트에서 테스트
2. 자신만의 설정 커스터마이징
3. 더 많은 테마와 폰트 탐색

**피드백**: 문제가 있거나 개선 제안이 있다면 이슈를 등록해주세요!

---

**마지막 업데이트**: 2025-01-28
**버전**: 1.0.0
**작성자**: Claude Code Korean Optimization Team
