#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MoAI-ADK 스마트 버전 검사기
설치된 버전과 최신 GitHub 릴리스를 비교합니다
독립 실행 모드와 Claude Agent SDK 모드를 모두 지원합니다
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

# 선택적 종속성을 가져오고, 필요시 설치합니다
try:
    import requests
except ImportError:
    print("📦 requests 설치 중...")
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "-q"], check=True)
    import requests

try:
    from packaging import version as pkg_version
except ImportError:
    print("📦 packaging 설치 중...")
    subprocess.run([sys.executable, "-m", "pip", "install", "packaging", "-q"], check=True)
    from packaging import version as pkg_version


class Colors:
    """터미널 색상 코드"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header():
    """포맷된 헤더 출력"""
    print(f"\n{Colors.BOLD}🔍 MoAI-ADK 버전 검사기{Colors.END}")
    print("━" * 44)
    print()


def get_installed_version() -> Optional[str]:
    """
    현재 설치된 MoAI-ADK 버전 가져오기

    Returns:
        버전 문자열 (예: "0.30.2") 또는 설치되지 않은 경우 None
    """
    # CLI 명령 먼저 시도
    try:
        result = subprocess.run(
            ["moai-adk", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # 출력에서 버전 번호 추출
            import re
            match = re.search(r'\d+\.\d+\.\d+', result.stdout)
            if match:
                return match.group(0)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Python import로 폴백
    try:
        import moai_adk
        return moai_adk.__version__
    except ImportError:
        pass

    return None


def get_latest_version() -> Optional[str]:
    """
    GitHub에서 최신 MoAI-ADK 버전 가져오기

    여러 폴백을 사용하는 GitHub API:
    1. Releases API (최신 릴리스)
    2. Tags API (릴리스가 없는 경우)
    3. Git ls-remote (API 실패 시)

    Returns:
        최신 버전 문자열 또는 가져오기 실패 시 None
    """
    print("📡 GitHub에서 최신 릴리스 가져오는 중...", end=" ")

    # GitHub releases API 시도
    try:
        response = requests.get(
            "https://api.github.com/repos/modu-ai/moai-adk/releases/latest",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            tag = data.get("tag_name", "")
            if tag:
                version = tag.lstrip("v")
                print(f"{Colors.GREEN}✓{Colors.END}")
                return version

        # Tags API로 폴백
        response = requests.get(
            "https://api.github.com/repos/modu-ai/moai-adk/tags",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                tag = data[0].get("name", "")
                version = tag.lstrip("v")
                print(f"{Colors.GREEN}✓{Colors.END}")
                return version

    except requests.RequestException as e:
        print(f"{Colors.YELLOW}⚠{Colors.END}")
        print(f"   API 요청 실패: {e}")

    # git ls-remote로 최종 폴백
    try:
        print("   git ls-remote 시도 중...", end=" ")
        result = subprocess.run(
            ["git", "ls-remote", "--tags", "https://github.com/modu-ai/moai-adk.git"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            import re
            # 모든 버전 태그 찾기
            tags = re.findall(r'refs/tags/v(\d+\.\d+\.\d+)$', result.stdout, re.MULTILINE)
            if tags:
                # 버전을 정렬하고 최신 버전 가져오기
                sorted_tags = sorted(tags, key=pkg_version.parse, reverse=True)
                print(f"{Colors.GREEN}✓{Colors.END}")
                return sorted_tags[0]

    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"{Colors.RED}✗{Colors.END}")
        print(f"   Git 명령 실패: {e}")

    return None


def compare_versions(installed: Optional[str], latest: Optional[str]) -> int:
    """
    버전 비교 및 결과 표시

    Args:
        installed: 설치된 버전 문자열
        latest: 사용 가능한 최신 버전 문자열

    Returns:
        종료 코드: 0 (최신), 1 (가져오기 실패), 2 (미설치), 3 (업데이트 가능)
    """
    print()
    print(f"{Colors.BOLD}📦 버전 정보{Colors.END}")
    print("━" * 44)

    # 미설치 처리
    if installed is None:
        print(f"설치됨: {Colors.RED}❌ 설치되지 않음{Colors.END}")
        installed = "0.0.0"
    else:
        print(f"설치됨: {Colors.GREEN}✅ v{installed}{Colors.END}")

    # 가져오기 실패 처리
    if latest is None:
        print(f"최신:    {Colors.YELLOW}⚠️  가져올 수 없음{Colors.END}")
        print()
        print("━" * 44)
        print()
        print(f"{Colors.RED}❌ GitHub API 실패{Colors.END}")
        print("   인터넷 연결을 확인해주세요")
        print()
        return 1

    print(f"최신:    {Colors.BLUE}🌟 v{latest}{Colors.END}")
    print()
    print("━" * 44)
    print()

    # 버전 비교
    if installed == "0.0.0":
        print(f"{Colors.BLUE}💡 권장사항: MoAI-ADK 설치{Colors.END}")
        print()
        print("설치 가이드 실행:")
        print("  cat _config/INSTALL-MOAI-ADK.md")
        print()
        return 2

    installed_ver = pkg_version.parse(installed)
    latest_ver = pkg_version.parse(latest)

    if installed_ver == latest_ver:
        print(f"{Colors.GREEN}✅ 최신 버전이 설치되어 있습니다!{Colors.END}")
        print()
        return 0

    elif installed_ver < latest_ver:
        print(f"{Colors.YELLOW}⬆️  업데이트 가능: v{installed} → v{latest}{Colors.END}")
        print()
        print("업데이트하려면 다음을 실행하세요:")
        print("━" * 44)
        print()
        print("# 1. 최신 릴리스 가져오기")
        print("cd moai-adk-source/moai-adk")
        print("git fetch --tags")
        print(f"git checkout v{latest}")
        print("cd ../..")
        print()
        print("# 2. 재설치")
        print("source .venv/bin/activate")
        print("pip install -e './moai-adk-source/moai-adk[dev]' --upgrade")
        print()
        print("# 3. 구성 업데이트")
        print("cp -r moai-adk-source/moai-adk/.moai .")
        print("cp -r moai-adk-source/moai-adk/.claude/commands/moai .claude/commands/")
        print("cp moai-adk-source/moai-adk/.mcp.json .")
        print("cp moai-adk-source/moai-adk/CLAUDE.md .")
        print()
        print("# 4. 확인")
        print("moai-adk --version")
        print("moai-adk doctor")
        print()
        return 3

    else:
        print(f"{Colors.YELLOW}⚠️  설치된 버전이 최신 릴리스보다 최신입니다{Colors.END}")
        print("   개발 버전을 사용 중일 수 있습니다")
        print()
        return 0


async def agent_mode(installed: Optional[str], latest: Optional[str]):
    """
    AI 강화 버전 검사를 위한 Claude Agent SDK 모드

    Args:
        installed: 설치된 버전 문자열
        latest: 최신 버전 문자열
    """
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions
    except ImportError:
        print(f"{Colors.YELLOW}⚠️  Claude Agent SDK가 설치되지 않음{Colors.END}")
        print("설치: pip install claude-agent-sdk")
        print()
        print("독립 실행 모드로 전환 중...")
        return compare_versions(installed, latest)

    print()
    print(f"{Colors.BOLD}🤖 Claude Agent SDK 모드{Colors.END}")
    print("━" * 44)
    print()

    # Claude를 위한 컨텍스트 준비
    context = {
        "installed": installed or "설치되지 않음",
        "latest": latest or "알 수 없음",
        "recommendation": "analyze"
    }

    prompt = f"""MoAI-ADK 버전 상태를 확인하고 있습니다:

설치된 버전: {context['installed']}
최신 버전: {context['latest']}

다음을 분석해주세요:
1. 명확한 상태 평가
2. 사용자를 위한 구체적인 권장사항
3. 업그레이드 시 발생할 수 있는 중요 변경사항
4. 필요한 경우 단계별 업데이트 지침

간결하고 실행 가능하게 작성해주세요."""

    options = ClaudeAgentOptions(
        system_prompt="당신은 MoAI-ADK 버전 관리를 돕는 유용한 어시스턴트입니다.",
        permission_mode='default'
    )

    print("🤖 Claude로 분석 중...\n")

    async for message in query(prompt=prompt, options=options):
        if hasattr(message, 'content'):
            for block in message.content:
                if hasattr(block, 'text'):
                    print(block.text)

    print()


def main():
    """메인 진입점"""
    parser = argparse.ArgumentParser(
        description="스마트 MoAI-ADK 버전 검사기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  %(prog)s                # 독립 실행 모드 (빠름)
  %(prog)s --agent        # AI 강화 모드 (claude-agent-sdk 필요)
        """
    )
    parser.add_argument(
        "--agent",
        action="store_true",
        help="AI 강화 분석을 위한 Claude Agent SDK 사용"
    )

    args = parser.parse_args()

    print_header()

    # 버전 가져오기
    installed = get_installed_version()
    latest = get_latest_version()

    # 모드 선택
    if args.agent:
        import anyio
        anyio.run(agent_mode, installed, latest)
        return 0
    else:
        return compare_versions(installed, latest)


if __name__ == "__main__":
    sys.exit(main())
