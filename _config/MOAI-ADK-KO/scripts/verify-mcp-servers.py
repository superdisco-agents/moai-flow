#!/usr/bin/env python3
"""
MCP 서버 검증 스크립트
MCP 서버가 올바르게 구성되고 접근 가능한지 테스트합니다
독립 실행 및 Claude Agent SDK 모드를 모두 지원합니다
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 선택적 종속성 가져오기, 필요시 설치
try:
    import requests
except ImportError:
    print("📦 requests 설치 중...")
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "-q"], check=True)
    import requests


class Colors:
    """터미널 색상 코드"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class MCPServer:
    """MCP 서버 구성"""
    def __init__(self, name: str, config: dict):
        self.name = name
        self.type = config.get("type", "stdio")
        self.command = config.get("command", "")
        self.args = config.get("args", [])
        self.url = config.get("url", "")
        self.passed = False
        self.message = ""


def print_header():
    """서식이 지정된 헤더 출력"""
    print(f"\n{Colors.BOLD}🔌 MCP 서버 검증{Colors.END}")
    print("━" * 44)
    print()


def load_mcp_config() -> Optional[Dict]:
    """
    .mcp.json에서 MCP 구성 로드

    Returns:
        MCP 서버 구성 딕셔너리 또는 찾을 수 없는 경우 None
    """
    mcp_file = Path(".mcp.json")

    if not mcp_file.exists():
        print(f"{Colors.RED}❌ 오류: .mcp.json을 찾을 수 없습니다{Colors.END}")
        print("   먼저 설치 가이드를 실행하세요")
        return None

    try:
        with open(mcp_file, 'r') as f:
            config = json.load(f)
            return config.get("mcpServers", {})
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}❌ .mcp.json 파싱 오류: {e}{Colors.END}")
        return None


def check_command_available(command: str) -> bool:
    """
    PATH에서 명령어 사용 가능 여부 확인

    Args:
        command: 확인할 명령어 이름

    Returns:
        명령어가 존재하면 True, 그렇지 않으면 False
    """
    try:
        subprocess.run(
            ["which", command],
            capture_output=True,
            check=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def verify_npm_package(package: str) -> bool:
    """
    npm 패키지 존재 여부 확인

    Args:
        package: 패키지 이름 (예: "@upstash/context7-mcp@latest")

    Returns:
        패키지가 유효하면 True, 그렇지 않으면 False
    """
    try:
        # 버전 정보 없이 패키지 이름 추출
        pkg_name = package.split('@latest')[0].split('@canary')[0]

        result = subprocess.run(
            ["npm", "view", pkg_name, "version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def test_sse_server(url: str) -> bool:
    """
    SSE 서버 접근성 테스트

    Args:
        url: 테스트할 서버 URL

    Returns:
        접근 가능하면 True, 그렇지 않으면 False
    """
    try:
        response = requests.head(url, timeout=5)
        return response.status_code < 500
    except requests.RequestException:
        return False


def test_stdio_server(server: MCPServer) -> Tuple[bool, str]:
    """
    stdio 기반 MCP 서버 테스트

    Args:
        server: MCPServer 인스턴스

    Returns:
        (성공 여부, 메시지) 튜플
    """
    command = server.command
    args = server.args

    print(f"  유형: {Colors.BLUE}stdio{Colors.END}")
    print(f"  명령어: {command} {' '.join(args)}")

    # 명령어 존재 여부 확인
    if not check_command_available(command):
        return False, f"{command}을(를) 찾을 수 없습니다"

    print(f"  상태: {Colors.GREEN}✅ {command} 사용 가능{Colors.END}")

    # npx 명령어의 경우 패키지 확인
    if command == "npx" and args:
        package = args[-1] if args else ""

        if package:
            print(f"  패키지 테스트: {package}")

            if verify_npm_package(package):
                print(f"  패키지: {Colors.GREEN}✅ npm에서 사용 가능{Colors.END}")
                return True, "패키지 확인됨"
            else:
                print(f"  패키지: {Colors.YELLOW}⚠️  확인할 수 없습니다{Colors.END}")
                print(f"  참고: 첫 사용 시 다운로드됩니다")
                return True, "패키지 미확인이지만 작동할 수 있습니다"

    return True, "명령어 사용 가능"


def test_sse_server_instance(server: MCPServer) -> Tuple[bool, str]:
    """
    SSE 기반 MCP 서버 테스트

    Args:
        server: MCPServer 인스턴스

    Returns:
        (성공 여부, 메시지) 튜플
    """
    url = server.url

    print(f"  유형: {Colors.BLUE}SSE{Colors.END}")
    print(f"  URL: {url}")

    if test_sse_server(url):
        print(f"  상태: {Colors.GREEN}✅ 접근 가능{Colors.END}")
        return True, "서버 접근 가능"
    else:
        print(f"  상태: {Colors.YELLOW}⚠️  접근 불가{Colors.END}")
        print(f"  참고: 서버를 시작해야 할 수 있습니다")
        return False, "서버 접근 불가 (시작 필요할 수 있음)"


def verify_servers(servers: Dict[str, MCPServer]) -> Tuple[int, int, int]:
    """
    모든 MCP 서버 검증

    Args:
        servers: MCPServer 인스턴스 딕셔너리

    Returns:
        (전체, 성공, 실패) 개수 튜플
    """
    print(f"{Colors.BOLD}📋 구성된 MCP 서버{Colors.END}")
    print("━" * 44)
    print()

    total = len(servers)
    passed = 0
    failed = 0

    for name, server in servers.items():
        print(f"테스트 중: {Colors.BOLD}{name}{Colors.END}")

        if server.type == "sse":
            success, message = test_sse_server_instance(server)
        else:
            success, message = test_stdio_server(server)

        server.passed = success
        server.message = message

        if success:
            passed += 1
        else:
            failed += 1

        print()

    return total, passed, failed


def print_summary(total: int, passed: int, failed: int):
    """검증 요약 출력"""
    print("━" * 44)
    print(f"{Colors.BOLD}📊 요약{Colors.END}")
    print("━" * 44)
    print()
    print(f"전체 서버:  {total}")
    print(f"성공:       {passed} {Colors.GREEN}✅{Colors.END}")
    print(f"실패:       {failed} {Colors.RED}❌{Colors.END}")
    print()


def print_server_details():
    """상세 서버 정보 출력"""
    print(f"{Colors.BOLD}🔍 서버 상세 정보{Colors.END}")
    print("━" * 44)
    print()

    servers_info = [
        {
            "name": "context7",
            "title": "문서 검색",
            "purpose": "실시간 라이브러리 문서 조회",
            "package": "@upstash/context7-mcp@latest",
            "critical": "⭐⭐⭐",
            "note": "API 환각 방지"
        },
        {
            "name": "sequential-thinking",
            "title": "복잡한 추론",
            "purpose": "다단계 문제 분석",
            "package": "@modelcontextprotocol/server-sequential-thinking@latest",
            "critical": "⭐⭐",
            "note": "복잡한 아키텍처 결정용"
        },
        {
            "name": "playwright",
            "title": "브라우저 자동화",
            "purpose": "웹 테스트 및 자동화",
            "package": "@playwright/mcp@latest",
            "critical": "⭐",
            "note": "대부분의 워크플로에서 선택사항"
        },
        {
            "name": "figma-dev-mode-mcp-server",
            "title": "디자인 통합",
            "purpose": "Figma 디자인 접근",
            "type": "SSE (로컬 서버 필요)",
            "critical": "⭐",
            "note": "디자인 워크플로에서 선택사항"
        }
    ]

    for idx, info in enumerate(servers_info, 1):
        print(f"{idx}. {info['name']} ({info['title']})")
        print(f"   목적: {info['purpose']}")

        if 'package' in info:
            print(f"   패키지: {info['package']}")
        if 'type' in info:
            print(f"   유형: {info['type']}")

        print(f"   중요도: {info['critical']} ({info['note']})")
        print()


def print_recommendations(failed: int):
    """결과에 따른 권장 사항 출력"""
    print("━" * 44)
    print(f"{Colors.BOLD}💡 권장 사항{Colors.END}")
    print("━" * 44)
    print()

    if failed > 0:
        print(f"{Colors.YELLOW}⚠️  일부 서버에 접근할 수 없습니다{Colors.END}")
        print()
        print("해결 방법:")
        print("  1. Node.js 설치: https://nodejs.org/")
        print("  2. npm 패키지를 위한 인터넷 연결 확인")
        print("  3. Figma의 경우: 필요시 로컬 서버 시작")
        print()
        print("Claude Code는 첫 사용 시 누락된 패키지를 다운로드합니다")
        print()
    else:
        print(f"{Colors.GREEN}✅ 모든 MCP 서버가 올바르게 구성되었습니다!{Colors.END}")
        print()
        print("다음 단계:")
        print("  1. Claude Code 실행: claude")
        print("  2. 메시지가 표시되면 모든 MCP 권한 부여")
        print("  3. MoAI 명령어 사용: /moai:1-plan, /moai:2-run 등")
        print()


async def agent_mode(servers: Dict[str, MCPServer], total: int, passed: int, failed: int):
    """
    AI 향상 진단을 위한 Claude Agent SDK 모드

    Args:
        servers: MCPServer 인스턴스 딕셔너리
        total: 전체 서버 개수
        passed: 성공한 서버 개수
        failed: 실패한 서버 개수
    """
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions
    except ImportError:
        print(f"{Colors.YELLOW}⚠️  Claude Agent SDK가 설치되지 않았습니다{Colors.END}")
        print("설치 명령어: pip install claude-agent-sdk")
        print()
        print("표준 결과를 표시합니다...")
        return

    print()
    print(f"{Colors.BOLD}🤖 Claude Agent SDK 모드{Colors.END}")
    print("━" * 44)
    print()

    # Claude용 서버 상태 준비
    server_status = []
    for name, server in servers.items():
        status = {
            "name": name,
            "type": server.type,
            "passed": server.passed,
            "message": server.message
        }
        server_status.append(status)

    prompt = f"""MoAI-ADK 설치를 위한 MCP 서버를 검증했습니다:

전체 서버: {total}
성공: {passed}
실패: {failed}

서버 상세 정보:
{json.dumps(server_status, indent=2)}

다음을 제공해 주세요:
1. MCP 서버 설정 평가
2. 실패에 대한 구체적인 문제 해결 단계
3. 최적화 권장 사항
4. 잠재적 문제 또는 충돌

간결하고 실행 가능하게 작성해 주세요."""

    options = ClaudeAgentOptions(
        system_prompt="당신은 MCP 서버 구성 및 문제 해결에 도움을 주는 도우미입니다.",
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
        description="MoAI-ADK용 MCP 서버 검증",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  %(prog)s                # 독립 실행 모드 (빠름)
  %(prog)s --agent        # AI 향상 모드 (claude-agent-sdk 필요)
        """
    )
    parser.add_argument(
        "--agent",
        action="store_true",
        help="AI 향상 진단을 위해 Claude Agent SDK 사용"
    )

    args = parser.parse_args()

    print_header()

    # MCP 구성 로드
    mcp_config = load_mcp_config()
    if mcp_config is None:
        return 1

    print(f"{Colors.GREEN}✅ .mcp.json 구성 파일을 찾았습니다{Colors.END}")
    print()

    # 서버 인스턴스 생성
    servers = {
        name: MCPServer(name, config)
        for name, config in mcp_config.items()
    }

    # 서버 검증
    total, passed, failed = verify_servers(servers)

    # 결과 출력
    print_summary(total, passed, failed)
    print_server_details()
    print_recommendations(failed)

    # 요청된 경우 에이전트 모드
    if args.agent:
        import anyio
        anyio.run(agent_mode, servers, total, passed, failed)

    # 종료 코드
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
