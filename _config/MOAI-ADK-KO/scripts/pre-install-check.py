#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MoAI ADK 사전 설치 점검 스크립트
======================================

MoAI ADK 설치 전 종합 시스템 점검.

기능:
- 전제 조건 검증 (Python, Git, Node.js, 디스크 공간, 네트워크)
- 충돌 감지 (claude-flow, .dot 폴더, 기존 MoAI)
- 자동 수정 모드
- CI 친화적 JSON 출력
- AI 에이전트 가이던스
- 색상 코딩 보고서
- 스마트 종료 코드

사용법:
    python pre-install-check.py                    # 대화형 모드
    python pre-install-check.py --auto-fix         # 자동 충돌 수정
    python pre-install-check.py --ci               # CI 모드 (JSON 출력)
    python pre-install-check.py --agent            # AI 가이던스 모드
    python pre-install-check.py --verbose          # 상세 출력

종료 코드:
    0 - 설치 준비 완료
    1 - 일반 오류
    2 - 전제 조건 실패
    3 - 충돌 감지됨 (수동/자동 해결 필요)
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import re


# ============================================================================
# ANSI 색상 코드
# ============================================================================

class Colors:
    """터미널 출력용 ANSI 색상 코드"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # 전경색
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # 배경색
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"

    # 밝은 색상
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"

    @staticmethod
    def disable():
        """색상 비활성화 (CI 모드용)"""
        for attr in dir(Colors):
            if not attr.startswith('_') and attr.isupper() and attr != 'RESET':
                setattr(Colors, attr, '')
        Colors.RESET = ''


# ============================================================================
# 상태 열거형
# ============================================================================

class CheckStatus(Enum):
    """개별 검사 상태"""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIP = "SKIP"
    FIXED = "FIXED"

    def icon(self) -> str:
        """상태 아이콘 가져오기"""
        icons = {
            CheckStatus.PASS: f"{Colors.GREEN}✓{Colors.RESET}",
            CheckStatus.FAIL: f"{Colors.RED}✗{Colors.RESET}",
            CheckStatus.WARNING: f"{Colors.YELLOW}⚠{Colors.RESET}",
            CheckStatus.SKIP: f"{Colors.DIM}○{Colors.RESET}",
            CheckStatus.FIXED: f"{Colors.CYAN}🔧{Colors.RESET}",
        }
        return icons.get(self, "?")


# ============================================================================
# 데이터 클래스
# ============================================================================

@dataclass
class CheckResult:
    """단일 검사 결과"""
    name: str
    status: CheckStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    can_auto_fix: bool = False
    fix_command: Optional[str] = None

    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            'name': self.name,
            'status': self.status.value,
            'message': self.message,
            'details': self.details,
            'can_auto_fix': self.can_auto_fix,
            'fix_command': self.fix_command
        }


@dataclass
class SystemReport:
    """전체 시스템 점검 보고서"""
    prerequisites: List[CheckResult] = field(default_factory=list)
    conflicts: List[CheckResult] = field(default_factory=list)
    disk_space: Optional[CheckResult] = None
    network: Optional[CheckResult] = None
    overall_status: CheckStatus = CheckStatus.PASS
    ready_for_install: bool = False
    timestamp: str = ""

    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            'prerequisites': [r.to_dict() for r in self.prerequisites],
            'conflicts': [r.to_dict() for r in self.conflicts],
            'disk_space': self.disk_space.to_dict() if self.disk_space else None,
            'network': self.network.to_dict() if self.network else None,
            'overall_status': self.overall_status.value,
            'ready_for_install': self.ready_for_install,
            'timestamp': self.timestamp
        }


# ============================================================================
# 사전 설치 검사기
# ============================================================================

class PreInstallChecker:
    """메인 사전 설치 검사 클래스"""

    MIN_PYTHON_VERSION = (3, 11)
    MAX_PYTHON_VERSION = (3, 14)
    MIN_DISK_SPACE_MB = 500
    GITHUB_API_URL = "https://api.github.com"

    def __init__(self, verbose: bool = False, ci_mode: bool = False, agent_mode: bool = False):
        self.verbose = verbose
        self.ci_mode = ci_mode
        self.agent_mode = agent_mode
        self.report = SystemReport()

        if ci_mode:
            Colors.disable()

    # ========================================================================
    # 유틸리티 메서드
    # ========================================================================

    def log(self, message: str, level: str = "INFO"):
        """상세 모드가 활성화된 경우 메시지 기록"""
        if self.verbose or level == "ERROR":
            prefix = {
                "INFO": f"{Colors.BLUE}[정보]{Colors.RESET}",
                "SUCCESS": f"{Colors.GREEN}[성공]{Colors.RESET}",
                "WARNING": f"{Colors.YELLOW}[경고]{Colors.RESET}",
                "ERROR": f"{Colors.RED}[오류]{Colors.RESET}",
            }
            print(f"{prefix.get(level, '[정보]')} {message}")

    def run_command(self, cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
        """셸 명령 실행 및 종료 코드, stdout, stderr 반환"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return 1, "", "명령 시간 초과"
        except FileNotFoundError:
            return 127, "", f"명령을 찾을 수 없음: {cmd[0]}"
        except Exception as e:
            return 1, "", str(e)

    def parse_version(self, version_string: str) -> Optional[Tuple[int, ...]]:
        """버전 문자열을 정수 튜플로 파싱"""
        match = re.search(r'(\d+)\.(\d+)(?:\.(\d+))?', version_string)
        if match:
            parts = [int(p) for p in match.groups() if p is not None]
            return tuple(parts)
        return None

    # ========================================================================
    # 전제 조건 검사
    # ========================================================================

    def check_python_version(self) -> CheckResult:
        """Python 버전 확인 (3.11-3.14)"""
        current_version = sys.version_info[:2]
        version_str = f"{current_version[0]}.{current_version[1]}"

        if self.MIN_PYTHON_VERSION <= current_version <= self.MAX_PYTHON_VERSION:
            return CheckResult(
                name="Python 버전",
                status=CheckStatus.PASS,
                message=f"Python {version_str} 감지됨",
                details={
                    'version': version_str,
                    'required': f"{self.MIN_PYTHON_VERSION[0]}.{self.MIN_PYTHON_VERSION[1]}-{self.MAX_PYTHON_VERSION[0]}.{self.MAX_PYTHON_VERSION[1]}"
                }
            )
        else:
            return CheckResult(
                name="Python 버전",
                status=CheckStatus.FAIL,
                message=f"Python {version_str}는 지원되지 않음 (3.11-3.14 필요)",
                details={
                    'version': version_str,
                    'required': f"{self.MIN_PYTHON_VERSION[0]}.{self.MIN_PYTHON_VERSION[1]}-{self.MAX_PYTHON_VERSION[0]}.{self.MAX_PYTHON_VERSION[1]}"
                },
                can_auto_fix=False,
                fix_command="python.org에서 Python 3.11-3.14를 설치하세요"
            )

    def check_git(self) -> CheckResult:
        """Git 사용 가능 여부 확인"""
        code, stdout, stderr = self.run_command(['git', '--version'])

        if code == 0:
            version = self.parse_version(stdout)
            return CheckResult(
                name="Git",
                status=CheckStatus.PASS,
                message=f"Git 설치됨: {stdout}",
                details={'version': stdout, 'path': shutil.which('git')}
            )
        else:
            return CheckResult(
                name="Git",
                status=CheckStatus.FAIL,
                message="Git을 찾을 수 없음",
                details={'error': stderr or 'git 명령을 사용할 수 없음'},
                can_auto_fix=False,
                fix_command="https://git-scm.com에서 Git을 설치하세요"
            )

    def check_nodejs(self) -> CheckResult:
        """Node.js/npx 사용 가능 여부 확인"""
        node_code, node_out, node_err = self.run_command(['node', '--version'])
        npx_code, npx_out, npx_err = self.run_command(['npx', '--version'])

        if node_code == 0 and npx_code == 0:
            return CheckResult(
                name="Node.js/npx",
                status=CheckStatus.PASS,
                message=f"Node.js {node_out}, npx {npx_out}",
                details={
                    'node_version': node_out,
                    'npx_version': npx_out,
                    'node_path': shutil.which('node'),
                    'npx_path': shutil.which('npx')
                }
            )
        elif node_code == 0:
            return CheckResult(
                name="Node.js/npx",
                status=CheckStatus.WARNING,
                message="Node.js를 찾았지만 npx가 누락됨",
                details={'node_version': node_out, 'error': npx_err},
                can_auto_fix=False,
                fix_command="npx 설치: npm install -g npx"
            )
        else:
            return CheckResult(
                name="Node.js/npx",
                status=CheckStatus.FAIL,
                message="Node.js/npx를 찾을 수 없음",
                details={'error': node_err or 'node 명령을 사용할 수 없음'},
                can_auto_fix=False,
                fix_command="https://nodejs.org에서 Node.js를 설치하세요"
            )

    def check_disk_space(self) -> CheckResult:
        """사용 가능한 디스크 공간 확인"""
        try:
            stat = shutil.disk_usage(os.getcwd())
            free_mb = stat.free / (1024 * 1024)
            total_mb = stat.total / (1024 * 1024)
            used_mb = stat.used / (1024 * 1024)

            if free_mb >= self.MIN_DISK_SPACE_MB:
                return CheckResult(
                    name="디스크 공간",
                    status=CheckStatus.PASS,
                    message=f"{free_mb:.0f} MB 사용 가능 ({self.MIN_DISK_SPACE_MB} MB 필요)",
                    details={
                        'free_mb': round(free_mb, 2),
                        'total_mb': round(total_mb, 2),
                        'used_mb': round(used_mb, 2),
                        'required_mb': self.MIN_DISK_SPACE_MB
                    }
                )
            else:
                return CheckResult(
                    name="디스크 공간",
                    status=CheckStatus.FAIL,
                    message=f"{free_mb:.0f} MB만 사용 가능 ({self.MIN_DISK_SPACE_MB} MB 필요)",
                    details={
                        'free_mb': round(free_mb, 2),
                        'total_mb': round(total_mb, 2),
                        'required_mb': self.MIN_DISK_SPACE_MB
                    },
                    can_auto_fix=False,
                    fix_command="설치 전에 디스크 공간을 확보하세요"
                )
        except Exception as e:
            return CheckResult(
                name="디스크 공간",
                status=CheckStatus.WARNING,
                message=f"디스크 공간을 확인할 수 없음: {e}",
                details={'error': str(e)}
            )

    def check_network(self) -> CheckResult:
        """GitHub API 네트워크 연결 확인"""
        try:
            req = urllib.request.Request(
                self.GITHUB_API_URL,
                headers={'User-Agent': 'MoAI-ADK-PreInstallCheck'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return CheckResult(
                        name="네트워크 연결",
                        status=CheckStatus.PASS,
                        message="GitHub API 접근 가능",
                        details={
                            'url': self.GITHUB_API_URL,
                            'status_code': response.status
                        }
                    )
                else:
                    return CheckResult(
                        name="네트워크 연결",
                        status=CheckStatus.WARNING,
                        message=f"GitHub API가 상태 {response.status}를 반환함",
                        details={
                            'url': self.GITHUB_API_URL,
                            'status_code': response.status
                        }
                    )
        except urllib.error.URLError as e:
            return CheckResult(
                name="네트워크 연결",
                status=CheckStatus.FAIL,
                message=f"GitHub API에 접근할 수 없음: {e.reason}",
                details={'url': self.GITHUB_API_URL, 'error': str(e)},
                can_auto_fix=False,
                fix_command="인터넷 연결 및 방화벽 설정을 확인하세요"
            )
        except Exception as e:
            return CheckResult(
                name="네트워크 연결",
                status=CheckStatus.FAIL,
                message=f"네트워크 확인 실패: {e}",
                details={'error': str(e)}
            )

    # ========================================================================
    # 충돌 감지
    # ========================================================================

    def check_claude_flow(self) -> CheckResult:
        """claude-flow 설치 확인"""
        code, stdout, stderr = self.run_command(['npx', 'claude-flow', '--version'])

        if code == 0:
            return CheckResult(
                name="claude-flow 설치",
                status=CheckStatus.WARNING,
                message=f"claude-flow 감지됨: {stdout}",
                details={'version': stdout, 'conflict': True},
                can_auto_fix=True,
                fix_command="python _config/MOAI-ADK/scripts/uninstall-claude-flow.py"
            )
        else:
            return CheckResult(
                name="claude-flow 설치",
                status=CheckStatus.PASS,
                message="claude-flow 설치가 감지되지 않음",
                details={'conflict': False}
            )

    def check_dot_folders(self) -> CheckResult:
        """충돌하는 .dot 폴더 확인"""
        home = Path.home()
        conflicting_folders = []

        dot_folders_to_check = [
            '.claude-flow',
            '.flow-nexus',
            '.ruv-swarm',
            '.moai-adk-old'
        ]

        for folder in dot_folders_to_check:
            folder_path = home / folder
            if folder_path.exists():
                # 폴더 크기 가져오기
                size = sum(f.stat().st_size for f in folder_path.rglob('*') if f.is_file())
                conflicting_folders.append({
                    'path': str(folder_path),
                    'size_mb': round(size / (1024 * 1024), 2)
                })

        if conflicting_folders:
            total_size = sum(f['size_mb'] for f in conflicting_folders)
            return CheckResult(
                name="충돌하는 .dot 폴더",
                status=CheckStatus.WARNING,
                message=f"{len(conflicting_folders)}개의 충돌 폴더 발견 ({total_size:.2f} MB)",
                details={
                    'folders': conflicting_folders,
                    'count': len(conflicting_folders),
                    'total_size_mb': total_size
                },
                can_auto_fix=True,
                fix_command="python _config/MOAI-ADK/scripts/clean-dot-folders.py"
            )
        else:
            return CheckResult(
                name="충돌하는 .dot 폴더",
                status=CheckStatus.PASS,
                message="충돌하는 .dot 폴더가 발견되지 않음",
                details={'folders': [], 'count': 0}
            )

    def check_moai_installation(self) -> CheckResult:
        """MoAI ADK가 이미 설치되어 있는지 확인"""
        moai_indicators = [
            Path.home() / '.moai-adk',
            Path.cwd() / 'moai-adk.json',
            Path.cwd() / '_config' / 'MOAI-ADK',
        ]

        found = []
        for path in moai_indicators:
            if path.exists():
                found.append(str(path))

        if found:
            return CheckResult(
                name="기존 MoAI 설치",
                status=CheckStatus.WARNING,
                message=f"MoAI ADK가 이미 설치되어 있을 수 있음 ({len(found)}개 표시)",
                details={'paths': found, 'count': len(found)},
                can_auto_fix=False,
                fix_command="필요한 경우 기존 설치를 수동으로 검토하고 제거하세요"
            )
        else:
            return CheckResult(
                name="기존 MoAI 설치",
                status=CheckStatus.PASS,
                message="기존 MoAI 설치가 감지되지 않음",
                details={'paths': [], 'count': 0}
            )

    # ========================================================================
    # 자동 수정
    # ========================================================================

    def auto_fix_conflicts(self) -> List[CheckResult]:
        """감지된 충돌 자동 수정"""
        fixed_results = []
        scripts_dir = Path(__file__).parent

        self.log("자동 수정 프로세스 시작 중...", "INFO")

        # claude-flow 수정
        claude_flow_check = self.check_claude_flow()
        if claude_flow_check.status == CheckStatus.WARNING and claude_flow_check.can_auto_fix:
            self.log("claude-flow 제거 중...", "INFO")
            script_path = scripts_dir / "uninstall-claude-flow.py"
            if script_path.exists():
                code, stdout, stderr = self.run_command([sys.executable, str(script_path)])
                if code == 0:
                    fixed_results.append(CheckResult(
                        name="claude-flow 제거",
                        status=CheckStatus.FIXED,
                        message="claude-flow를 성공적으로 제거함",
                        details={'output': stdout}
                    ))
                else:
                    fixed_results.append(CheckResult(
                        name="claude-flow 제거",
                        status=CheckStatus.FAIL,
                        message=f"claude-flow 제거 실패: {stderr}",
                        details={'error': stderr}
                    ))
            else:
                self.log(f"제거 스크립트를 찾을 수 없음: {script_path}", "WARNING")

        # .dot 폴더 수정
        dot_folders_check = self.check_dot_folders()
        if dot_folders_check.status == CheckStatus.WARNING and dot_folders_check.can_auto_fix:
            self.log(".dot 폴더 정리 중...", "INFO")
            script_path = scripts_dir / "clean-dot-folders.py"
            if script_path.exists():
                code, stdout, stderr = self.run_command([sys.executable, str(script_path), '--auto'])
                if code == 0:
                    fixed_results.append(CheckResult(
                        name=".dot 폴더 정리",
                        status=CheckStatus.FIXED,
                        message=".dot 폴더를 성공적으로 정리함",
                        details={'output': stdout}
                    ))
                else:
                    fixed_results.append(CheckResult(
                        name=".dot 폴더 정리",
                        status=CheckStatus.FAIL,
                        message=f".dot 폴더 정리 실패: {stderr}",
                        details={'error': stderr}
                    ))
            else:
                self.log(f"정리 스크립트를 찾을 수 없음: {script_path}", "WARNING")

        return fixed_results

    # ========================================================================
    # 주요 검사 조정
    # ========================================================================

    def run_all_checks(self) -> SystemReport:
        """모든 전제 조건 및 충돌 검사 실행"""
        from datetime import datetime

        self.log("사전 설치 검사 시작 중...", "INFO")

        # 전제 조건
        self.report.prerequisites = [
            self.check_python_version(),
            self.check_git(),
            self.check_nodejs(),
        ]

        # 디스크 및 네트워크
        self.report.disk_space = self.check_disk_space()
        self.report.network = self.check_network()

        # 충돌
        self.report.conflicts = [
            self.check_claude_flow(),
            self.check_dot_folders(),
            self.check_moai_installation(),
        ]

        # 전체 상태 결정
        has_failures = any(r.status == CheckStatus.FAIL for r in self.report.prerequisites)
        has_failures |= self.report.disk_space.status == CheckStatus.FAIL if self.report.disk_space else False
        has_failures |= self.report.network.status == CheckStatus.FAIL if self.report.network else False

        has_conflicts = any(r.status == CheckStatus.WARNING for r in self.report.conflicts)

        if has_failures:
            self.report.overall_status = CheckStatus.FAIL
            self.report.ready_for_install = False
        elif has_conflicts:
            self.report.overall_status = CheckStatus.WARNING
            self.report.ready_for_install = False
        else:
            self.report.overall_status = CheckStatus.PASS
            self.report.ready_for_install = True

        self.report.timestamp = datetime.now().isoformat()

        return self.report

    # ========================================================================
    # 보고서 생성
    # ========================================================================

    def print_report(self):
        """콘솔에 색상 코딩된 보고서 출력"""
        print()
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}MoAI ADK 사전 설치 검사 보고서{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
        print()

        # 전제 조건
        print(f"{Colors.BOLD}전제 조건:{Colors.RESET}")
        for result in self.report.prerequisites:
            print(f"  {result.status.icon()} {result.name}: {result.message}")
        print()

        # 디스크 공간
        if self.report.disk_space:
            print(f"{Colors.BOLD}디스크 공간:{Colors.RESET}")
            print(f"  {self.report.disk_space.status.icon()} {self.report.disk_space.message}")
            print()

        # 네트워크
        if self.report.network:
            print(f"{Colors.BOLD}네트워크 연결:{Colors.RESET}")
            print(f"  {self.report.network.status.icon()} {self.report.network.message}")
            print()

        # 충돌
        print(f"{Colors.BOLD}충돌 감지:{Colors.RESET}")
        for result in self.report.conflicts:
            print(f"  {result.status.icon()} {result.name}: {result.message}")
            if result.can_auto_fix and result.fix_command:
                print(f"    {Colors.DIM}수정: {result.fix_command}{Colors.RESET}")
        print()

        # 전체 상태
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
        if self.report.overall_status == CheckStatus.PASS:
            status_msg = f"{Colors.BOLD}{Colors.GREEN}✓ 설치 준비 완료{Colors.RESET}"
        elif self.report.overall_status == CheckStatus.WARNING:
            status_msg = f"{Colors.BOLD}{Colors.YELLOW}⚠ 충돌 감지됨 - 수정 필요{Colors.RESET}"
        else:
            status_msg = f"{Colors.BOLD}{Colors.RED}✗ 전제 조건 실패{Colors.RESET}"

        print(f"전체 상태: {status_msg}")
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
        print()

        # AI 에이전트 가이던스
        if self.agent_mode:
            self.print_ai_guidance()

    def print_ai_guidance(self):
        """검사 결과에 따른 AI 에이전트 가이던스 출력"""
        print(f"{Colors.BOLD}{Colors.MAGENTA}🤖 AI 에이전트 가이던스:{Colors.RESET}")
        print()

        if self.report.ready_for_install:
            print(f"{Colors.GREEN}시스템이 MoAI ADK 설치 준비가 되었습니다!{Colors.RESET}")
            print()
            print("다음 단계:")
            print("  1. MoAI ADK 설치 프로그램 실행")
            print("  2. 설치 마법사 따라가기")
            print("  3. AI 에이전트 구성")
        else:
            print(f"{Colors.YELLOW}설치 전에 시스템 점검이 필요합니다:{Colors.RESET}")
            print()

            # 전제 조건 문제
            failed_prereqs = [r for r in self.report.prerequisites if r.status == CheckStatus.FAIL]
            if failed_prereqs:
                print(f"{Colors.RED}중요 문제:{Colors.RESET}")
                for result in failed_prereqs:
                    print(f"  • {result.name}: {result.message}")
                    if result.fix_command:
                        print(f"    → {result.fix_command}")
                print()

            # 충돌
            conflicts = [r for r in self.report.conflicts if r.status == CheckStatus.WARNING]
            if conflicts:
                print(f"{Colors.YELLOW}해결할 충돌:{Colors.RESET}")
                for result in conflicts:
                    print(f"  • {result.name}: {result.message}")
                    if result.can_auto_fix:
                        print(f"    → --auto-fix로 실행하여 자동으로 해결")
                    elif result.fix_command:
                        print(f"    → {result.fix_command}")
                print()

            print(f"{Colors.CYAN}권장 조치:{Colors.RESET}")
            if any(r.can_auto_fix for r in conflicts):
                print(f"  실행: {Colors.BOLD}python pre-install-check.py --auto-fix{Colors.RESET}")
            else:
                print("  위의 문제를 수동으로 해결한 후 이 검사를 다시 실행하세요")

        print()

    def print_json_report(self):
        """CI 모드용 JSON 보고서 출력"""
        print(json.dumps(self.report.to_dict(), indent=2, ensure_ascii=False))

    # ========================================================================
    # 종료 코드 결정
    # ========================================================================

    def get_exit_code(self) -> int:
        """적절한 종료 코드 결정"""
        if self.report.overall_status == CheckStatus.PASS:
            return 0
        elif self.report.overall_status == CheckStatus.WARNING:
            return 3  # 충돌 감지됨
        else:
            return 2  # 전제 조건 실패


# ============================================================================
# 메인 진입점
# ============================================================================

def main():
    """메인 진입점"""
    parser = argparse.ArgumentParser(
        description="MoAI ADK 사전 설치 검사",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  python pre-install-check.py                    # 대화형 검사
  python pre-install-check.py --auto-fix         # 자동 충돌 수정
  python pre-install-check.py --ci               # CI 모드 (JSON 출력)
  python pre-install-check.py --agent            # AI 가이던스
  python pre-install-check.py --verbose          # 상세 출력

종료 코드:
  0 - 설치 준비 완료
  1 - 일반 오류
  2 - 전제 조건 실패
  3 - 충돌 감지됨
        """
    )

    parser.add_argument(
        '--auto-fix',
        action='store_true',
        help='감지된 충돌을 자동으로 수정'
    )

    parser.add_argument(
        '--ci',
        action='store_true',
        help='CI 모드: JSON 출력으로 비대화형'
    )

    parser.add_argument(
        '--agent',
        action='store_true',
        help='AI 에이전트 가이던스 활성화'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='상세 출력'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='MoAI ADK 사전 설치 검사 v1.0.0'
    )

    args = parser.parse_args()

    try:
        # 검사기 생성
        checker = PreInstallChecker(
            verbose=args.verbose,
            ci_mode=args.ci,
            agent_mode=args.agent
        )

        # 검사 실행
        report = checker.run_all_checks()

        # 요청 시 자동 수정
        if args.auto_fix and report.overall_status == CheckStatus.WARNING:
            fixed = checker.auto_fix_conflicts()
            if fixed:
                # 수정 후 검사 재실행
                checker.log("자동 수정 후 검사 재실행 중...", "INFO")
                report = checker.run_all_checks()

        # 보고서 출력
        if args.ci:
            checker.print_json_report()
        else:
            checker.print_report()

        # 적절한 코드로 종료
        exit_code = checker.get_exit_code()
        sys.exit(exit_code)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}사용자에 의해 검사가 중단됨{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}오류: {e}{Colors.RESET}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
