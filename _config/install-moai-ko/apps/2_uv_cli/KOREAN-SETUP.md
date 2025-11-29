# Korean Language Setup Guide (한국어 설정 가이드)

Complete guide for setting up MoAI-ADK with Korean language support using the UV CLI installer.

## English Version

### Overview

The UV CLI installer provides comprehensive Korean language support with:

- **Automatic locale detection**
- **Platform-specific font installation**
- **Korean NLP feature configuration**
- **Bilingual documentation**

### Auto-Detection

The installer automatically detects Korean locale settings:

```bash
$ uv run installer.py install

╭────────────── System Information ──────────────╮
│ Locale           ko_KR.UTF-8                   │
│ Korean Detected  Yes                           │
╰────────────────────────────────────────────────╯

Korean locale detected. Install Korean support? [Y/n]:
```

**Detection Logic:**

1. Checks `LANG` environment variable
2. Checks `LC_ALL` environment variable
3. Detects patterns: `ko_`, `KR`, `Korea`

### Installation Methods

#### Method 1: During Initial Installation (Recommended)

```bash
# Auto-detection will prompt
uv run installer.py install

# Output:
Korean locale detected. Install Korean support? [Y/n]: y
```

#### Method 2: Explicit Flag

```bash
# Force Korean installation
uv run installer.py install --korean
```

#### Method 3: Post-Installation

```bash
# Add Korean support after installation
uv run installer.py setup-korean
```

### What Gets Installed

#### 1. Korean Fonts

**macOS:**
```bash
# Via Homebrew
brew install --cask font-nanum
brew install --cask font-nanum-gothic-coding
```

**Ubuntu/Debian:**
```bash
sudo apt-get install fonts-nanum fonts-nanum-coding
```

**Fedora/RHEL:**
```bash
sudo yum install google-noto-sans-cjk-ttc-fonts
```

**Arch Linux:**
```bash
sudo pacman -S noto-fonts-cjk
```

#### 2. Locale Configuration

File: `~/.moai/config/settings.json`

```json
{
  "language": "ko_KR",
  "locale": "ko_KR.UTF-8",
  "encoding": "UTF-8",
  "ui": {
    "font_family": "Nanum Gothic",
    "font_size": 14
  },
  "features": {
    "korean_nlp": true,
    "korean_tokenizer": true
  }
}
```

#### 3. Korean NLP Features

- **Korean tokenizer**: Sentence and word segmentation
- **Korean morphological analyzer**: Part-of-speech tagging
- **Korean stopwords**: Common word filtering
- **Korean stemming**: Word normalization

### Verification

#### Check Installed Fonts

**macOS/Linux:**
```bash
fc-list | grep -i nanum
```

**Expected output:**
```
/usr/share/fonts/truetype/nanum/NanumGothic.ttf: NanumGothic:style=Regular
/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf: NanumGothic:style=Bold
/usr/share/fonts/truetype/nanum/NanumGothicCoding.ttf: NanumGothicCoding:style=Regular
```

#### Check Configuration

```bash
# View settings
cat ~/.moai/config/settings.json

# Check status
uv run installer.py status
```

#### Test Korean NLP

```python
import moai_adk
from moai_adk import config

# Load settings
settings = config.load_settings()

print(f"Language: {settings['language']}")
print(f"Korean NLP enabled: {settings['features']['korean_nlp']}")

# Test Korean text processing
text = "안녕하세요, MoAI-ADK를 설치해 주셔서 감사합니다."
result = moai_adk.process_korean_text(text)
print(result)
```

### Troubleshooting

#### Issue: Fonts Not Displaying

**macOS:**
```bash
# Check Homebrew
brew list | grep font-nanum

# Reinstall if needed
brew reinstall --cask font-nanum
```

**Linux:**
```bash
# Rebuild font cache
sudo fc-cache -fv

# Verify
fc-list | grep -i nanum
```

#### Issue: Korean Characters Show as Boxes

1. **Check terminal font settings**
2. **Restart terminal application**
3. **Verify locale settings:**
   ```bash
   locale
   echo $LANG
   ```

#### Issue: Korean NLP Not Working

```bash
# Check configuration
cat ~/.moai/config/settings.json

# Verify korean_nlp is true
# If false, run:
uv run installer.py setup-korean
```

### Manual Font Installation

If automatic installation fails:

**macOS:**
1. Download fonts from [Nanum Font](https://hangeul.naver.com/2017/nanum)
2. Open .ttf files
3. Click "Install Font"

**Linux:**
1. Download fonts
2. Copy to `~/.local/share/fonts/`
3. Run `fc-cache -fv`

---

## 한국어 버전 (Korean Version)

### 개요

UV CLI 설치 프로그램은 다음과 같은 포괄적인 한국어 지원을 제공합니다:

- **자동 로케일 감지**
- **플랫폼별 폰트 설치**
- **한국어 NLP 기능 구성**
- **이중 언어 문서**

### 자동 감지

설치 프로그램이 한국어 로케일 설정을 자동으로 감지합니다:

```bash
$ uv run installer.py install

╭────────────── 시스템 정보 ──────────────╮
│ 로케일          ko_KR.UTF-8             │
│ 한국어 감지     예                       │
╰─────────────────────────────────────────╯

한국어 로케일이 감지되었습니다. 한국어 지원을 설치하시겠습니까? [Y/n]:
```

**감지 로직:**

1. `LANG` 환경 변수 확인
2. `LC_ALL` 환경 변수 확인
3. 패턴 감지: `ko_`, `KR`, `Korea`

### 설치 방법

#### 방법 1: 초기 설치 시 (권장)

```bash
# 자동 감지가 프롬프트를 표시합니다
uv run installer.py install

# 출력:
한국어 로케일이 감지되었습니다. 한국어 지원을 설치하시겠습니까? [Y/n]: y
```

#### 방법 2: 명시적 플래그 사용

```bash
# 한국어 설치 강제
uv run installer.py install --korean
```

#### 방법 3: 설치 후 추가

```bash
# 설치 후 한국어 지원 추가
uv run installer.py setup-korean
```

### 설치되는 항목

#### 1. 한국어 폰트

**macOS:**
```bash
# Homebrew를 통해
brew install --cask font-nanum
brew install --cask font-nanum-gothic-coding
```

**Ubuntu/Debian:**
```bash
sudo apt-get install fonts-nanum fonts-nanum-coding
```

**Fedora/RHEL:**
```bash
sudo yum install google-noto-sans-cjk-ttc-fonts
```

**Arch Linux:**
```bash
sudo pacman -S noto-fonts-cjk
```

#### 2. 로케일 구성

파일: `~/.moai/config/settings.json`

```json
{
  "language": "ko_KR",
  "locale": "ko_KR.UTF-8",
  "encoding": "UTF-8",
  "ui": {
    "font_family": "Nanum Gothic",
    "font_size": 14
  },
  "features": {
    "korean_nlp": true,
    "korean_tokenizer": true
  }
}
```

#### 3. 한국어 NLP 기능

- **한국어 토크나이저**: 문장 및 단어 분할
- **한국어 형태소 분석기**: 품사 태깅
- **한국어 불용어**: 일반 단어 필터링
- **한국어 어간 추출**: 단어 정규화

### 검증

#### 설치된 폰트 확인

**macOS/Linux:**
```bash
fc-list | grep -i nanum
```

**예상 출력:**
```
/usr/share/fonts/truetype/nanum/NanumGothic.ttf: NanumGothic:style=Regular
/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf: NanumGothic:style=Bold
/usr/share/fonts/truetype/nanum/NanumGothicCoding.ttf: NanumGothicCoding:style=Regular
```

#### 구성 확인

```bash
# 설정 보기
cat ~/.moai/config/settings.json

# 상태 확인
uv run installer.py status
```

#### 한국어 NLP 테스트

```python
import moai_adk
from moai_adk import config

# 설정 로드
settings = config.load_settings()

print(f"언어: {settings['language']}")
print(f"한국어 NLP 활성화: {settings['features']['korean_nlp']}")

# 한국어 텍스트 처리 테스트
text = "안녕하세요, MoAI-ADK를 설치해 주셔서 감사합니다."
result = moai_adk.process_korean_text(text)
print(result)
```

### 문제 해결

#### 문제: 폰트가 표시되지 않음

**macOS:**
```bash
# Homebrew 확인
brew list | grep font-nanum

# 필요시 재설치
brew reinstall --cask font-nanum
```

**Linux:**
```bash
# 폰트 캐시 재구축
sudo fc-cache -fv

# 확인
fc-list | grep -i nanum
```

#### 문제: 한국어 문자가 네모로 표시됨

1. **터미널 폰트 설정 확인**
2. **터미널 애플리케이션 재시작**
3. **로케일 설정 확인:**
   ```bash
   locale
   echo $LANG
   ```

#### 문제: 한국어 NLP가 작동하지 않음

```bash
# 구성 확인
cat ~/.moai/config/settings.json

# korean_nlp가 true인지 확인
# false인 경우 실행:
uv run installer.py setup-korean
```

### 수동 폰트 설치

자동 설치가 실패한 경우:

**macOS:**
1. [나눔폰트](https://hangeul.naver.com/2017/nanum)에서 폰트 다운로드
2. .ttf 파일 열기
3. "폰트 설치" 클릭

**Linux:**
1. 폰트 다운로드
2. `~/.local/share/fonts/`에 복사
3. `fc-cache -fv` 실행

### 한국어 환경 설정

#### 시스템 로케일 설정

**macOS:**
```bash
# .zshrc 또는 .bashrc에 추가
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8
```

**Linux:**
```bash
# 로케일 생성
sudo locale-gen ko_KR.UTF-8

# 시스템 기본 설정
sudo update-locale LANG=ko_KR.UTF-8

# .bashrc에 추가
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8
```

#### 터미널 인코딩 설정

대부분의 현대 터미널은 UTF-8을 기본으로 지원하지만, 확인하려면:

```bash
# 현재 인코딩 확인
echo $LANG

# UTF-8로 설정되어 있어야 함
# 예: ko_KR.UTF-8, en_US.UTF-8
```

### 한국어 문서 생성

MoAI-ADK로 한국어 문서를 생성할 때:

```python
import moai_adk

# 한국어 설정 로드
moai_adk.set_language('ko_KR')

# 한국어 텍스트 처리
text = """
MoAI-ADK는 여러 AI 에이전트를 조합하여
더 나은 결과를 생성하는 프레임워크입니다.
"""

result = moai_adk.process(text)
print(result)
```

### 추가 리소스

- **나눔폰트 다운로드**: https://hangeul.naver.com/2017/nanum
- **한국어 형태소 분석기**: https://github.com/konlpy/konlpy
- **한국어 NLP 도구**: https://github.com/ratsgo

### 자주 묻는 질문 (FAQ)

#### Q: 영어와 한국어를 함께 사용할 수 있나요?

A: 네, MoAI-ADK는 다국어를 지원합니다. 설정에서 언어를 전환할 수 있습니다.

```python
# 언어 전환
moai_adk.set_language('ko_KR')  # 한국어
moai_adk.set_language('en_US')  # 영어
```

#### Q: 다른 한국어 폰트를 사용할 수 있나요?

A: 네, `~/.moai/config/settings.json`에서 폰트를 변경할 수 있습니다:

```json
{
  "ui": {
    "font_family": "Malgun Gothic",  # 또는 다른 폰트
    "font_size": 14
  }
}
```

#### Q: 한국어 NLP 기능은 무엇을 포함하나요?

A: 다음을 포함합니다:
- 형태소 분석
- 품사 태깅
- 개체명 인식
- 감성 분석
- 텍스트 분류

#### Q: 한국어 지원을 제거하려면?

```bash
# 한국어 폰트 제거 (macOS)
brew uninstall --cask font-nanum font-nanum-gothic-coding

# 한국어 폰트 제거 (Linux)
sudo apt-get remove fonts-nanum fonts-nanum-coding

# 설정 파일에서 한국어 비활성화
# ~/.moai/config/settings.json 편집:
{
  "language": "en_US",
  "features": {
    "korean_nlp": false
  }
}
```

### 지원

한국어 설정 관련 문제가 있으면:

1. **로그 확인**: `~/.moai/logs/installer.log`
2. **상태 확인**: `uv run installer.py status`
3. **재설치**: `uv run installer.py setup-korean`

### 라이선스

MIT 라이선스 - 자세한 내용은 MoAI-ADK 저장소를 참조하세요.
