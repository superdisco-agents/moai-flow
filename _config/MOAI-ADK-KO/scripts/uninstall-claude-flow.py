#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude-Flow 종합 제거 도구
모든 claude-flow 디렉토리와 패키지를 안전하게 제거합니다
테스트 모드, 백업, AI 가이드 모드를 지원합니다
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 선택적 의존성 가져오기 시도
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
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ClaudeFlowUninstaller:
    """메인 제거 도구 클래스"""

    # 제거할 디렉토리
    DIRECTORIES = [
        '.claude-flow',
        '.swarm',
        '.hive-mind',
        '.specstory',
        'node_modules/.cache/claude-flow'
    ]

    # 제거할 NPM 패키지
    NPM_PACKAGES = [
        'claude-flow',
        '@claude-flow/core',
        '@claude-flow/cli'
    ]

    def __init__(self, dry_run: bool = False, backup: bool = False, verbose: bool = False):
        """
        제거 도구 초기화

        Args:
            dry_run: True인 경우, 수행될 작업만 표시
            backup: True인 경우, 삭제 전 디렉토리 백업
            verbose: True인 경우, 상세 출력 표시
        """
        self.dry_run = dry_run
        self.backup = backup
        self.verbose = verbose
        self.base_dir = Path.cwd()
        self.removed_items: List[Dict] = []
        self.errors: List[Dict] = []
        self.total_size = 0

    def print_header(self):
        """형식화된 헤더 출력"""
        mode = "테스트 모드" if self.dry_run else "제거"
        backup_indicator = " + 백업" if self.backup else ""

        print(f"\n{Colors.BOLD}{Colors.RED}🗑️  Claude-Flow 제거 도구 [{mode}{backup_indicator}]{Colors.END}")
        print("━" * 60)
        print()

    def get_directory_size(self, path: Path) -> int:
        """
        디렉토리의 전체 크기 계산

        Args:
            path: 디렉토리 경로

        Returns:
            바이트 단위 크기
        """
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except (OSError, PermissionError) as e:
            if self.verbose:
                print(f"   {Colors.YELLOW}⚠ 크기를 계산할 수 없음: {e}{Colors.END}")
        return total_size

    def format_size(self, size_bytes: int) -> str:
        """
        바이트를 읽기 쉬운 크기로 형식화

        Args:
            size_bytes: 바이트 단위 크기

        Returns:
            형식화된 문자열 (예: "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def scan_directories(self) -> List[Dict]:
        """
        claude-flow 디렉토리 검색

        Returns:
            디렉토리 정보가 담긴 딕셔너리 리스트
        """
        print(f"{Colors.BOLD}📂 claude-flow 디렉토리 검색 중...{Colors.END}")
        print()

        found_dirs = []

        for dir_name in self.DIRECTORIES:
            dir_path = self.base_dir / dir_name

            if dir_path.exists():
                size = self.get_directory_size(dir_path)
                self.total_size += size

                dir_info = {
                    'name': dir_name,
                    'path': str(dir_path),
                    'size': size,
                    'size_formatted': self.format_size(size),
                    'type': 'directory'
                }
                found_dirs.append(dir_info)

                status = f"{Colors.GREEN}✓ 발견{Colors.END}"
                print(f"  {status} {Colors.CYAN}{dir_name:<35}{Colors.END} ({dir_info['size_formatted']})")

        if not found_dirs:
            print(f"  {Colors.YELLOW}⚠ claude-flow 디렉토리를 찾을 수 없음{Colors.END}")

        print()
        return found_dirs

    def check_npm_packages(self) -> List[Dict]:
        """
        전역 설치된 npm 패키지 확인

        Returns:
            패키지 정보가 담긴 딕셔너리 리스트
        """
        print(f"{Colors.BOLD}📦 npm 패키지 확인 중...{Colors.END}")
        print()

        found_packages = []

        try:
            # 전역 npm 패키지 가져오기
            result = subprocess.run(
                ['npm', 'list', '-g', '--json', '--depth=0'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                dependencies = data.get('dependencies', {})

                for package_name in self.NPM_PACKAGES:
                    if package_name in dependencies:
                        version = dependencies[package_name].get('version', 'unknown')
                        package_info = {
                            'name': package_name,
                            'version': version,
                            'type': 'npm-global'
                        }
                        found_packages.append(package_info)

                        status = f"{Colors.GREEN}✓ 발견{Colors.END}"
                        print(f"  {status} {Colors.CYAN}{package_name:<35}{Colors.END} (v{version})")

        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError) as e:
            if self.verbose:
                print(f"  {Colors.YELLOW}⚠ npm 패키지를 확인할 수 없음: {e}{Colors.END}")

        if not found_packages:
            print(f"  {Colors.YELLOW}⚠ claude-flow npm 패키지를 찾을 수 없음{Colors.END}")

        print()
        return found_packages

    def backup_directory(self, dir_path: Path) -> Optional[str]:
        """
        디렉토리 백업 생성

        Args:
            dir_path: 백업할 디렉토리 경로

        Returns:
            백업 아카이브 경로 또는 실패 시 None
        """
        if not self.backup or self.dry_run:
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.base_dir / '_backups' / 'claude-flow-uninstall'
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_name = f"{dir_path.name}_{timestamp}"
        backup_path = backup_dir / backup_name

        try:
            print(f"  {Colors.BLUE}📦 백업 생성 중: {backup_name}{Colors.END}")
            shutil.copytree(dir_path, backup_path)
            return str(backup_path)
        except Exception as e:
            error_msg = f"{dir_path.name} 백업 실패: {e}"
            self.errors.append({
                'operation': 'backup',
                'target': str(dir_path),
                'error': str(e)
            })
            print(f"  {Colors.RED}✗ 백업 실패: {e}{Colors.END}")
            return None

    def remove_directory(self, dir_info: Dict) -> bool:
        """
        디렉토리 제거

        Args:
            dir_info: 디렉토리 정보 딕셔너리

        Returns:
            성공 시 True, 실패 시 False
        """
        dir_path = Path(dir_info['path'])

        print(f"  {Colors.YELLOW}🗑️  제거 중: {dir_info['name']}{Colors.END}")

        # 요청 시 백업
        if self.backup:
            backup_path = self.backup_directory(dir_path)
            if backup_path:
                dir_info['backup_path'] = backup_path

        # 디렉토리 제거
        if not self.dry_run:
            try:
                shutil.rmtree(dir_path)
                print(f"     {Colors.GREEN}✓ 성공적으로 제거됨{Colors.END}")
                dir_info['removed'] = True
                self.removed_items.append(dir_info)
                return True
            except Exception as e:
                error_msg = f"{dir_info['name']} 제거 실패: {e}"
                self.errors.append({
                    'operation': 'remove',
                    'target': dir_info['path'],
                    'error': str(e)
                })
                print(f"     {Colors.RED}✗ 제거 실패: {e}{Colors.END}")
                dir_info['removed'] = False
                return False
        else:
            print(f"     {Colors.BLUE}ℹ 제거될 예정 (테스트 모드){Colors.END}")
            dir_info['removed'] = None  # 테스트 모드에서는 해당 없음
            return True

    def uninstall_npm_package(self, package_info: Dict) -> bool:
        """
        npm 패키지 제거

        Args:
            package_info: 패키지 정보 딕셔너리

        Returns:
            성공 시 True, 실패 시 False
        """
        package_name = package_info['name']

        print(f"  {Colors.YELLOW}🗑️  제거 중: {package_name}{Colors.END}")

        if not self.dry_run:
            try:
                result = subprocess.run(
                    ['npm', 'uninstall', '-g', package_name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    print(f"     {Colors.GREEN}✓ 성공적으로 제거됨{Colors.END}")
                    package_info['removed'] = True
                    self.removed_items.append(package_info)
                    return True
                else:
                    error_msg = result.stderr or "알 수 없는 오류"
                    self.errors.append({
                        'operation': 'npm-uninstall',
                        'target': package_name,
                        'error': error_msg
                    })
                    print(f"     {Colors.RED}✗ 제거 실패: {error_msg}{Colors.END}")
                    package_info['removed'] = False
                    return False

            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                self.errors.append({
                    'operation': 'npm-uninstall',
                    'target': package_name,
                    'error': str(e)
                })
                print(f"     {Colors.RED}✗ 제거 실패: {e}{Colors.END}")
                package_info['removed'] = False
                return False
        else:
            print(f"     {Colors.BLUE}ℹ 제거될 예정 (테스트 모드){Colors.END}")
            package_info['removed'] = None
            return True

    def clean_npm_cache(self) -> bool:
        """
        npm 캐시 정리

        Returns:
            성공 시 True, 실패 시 False
        """
        print(f"  {Colors.YELLOW}🧹 npm 캐시 정리 중...{Colors.END}")

        if not self.dry_run:
            try:
                result = subprocess.run(
                    ['npm', 'cache', 'clean', '--force'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    print(f"     {Colors.GREEN}✓ 캐시 정리됨{Colors.END}")
                    return True
                else:
                    print(f"     {Colors.YELLOW}⚠ 캐시 정리가 0이 아닌 값 반환{Colors.END}")
                    return False

            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                print(f"     {Colors.RED}✗ 캐시 정리 실패: {e}{Colors.END}")
                return False
        else:
            print(f"     {Colors.BLUE}ℹ 캐시 정리될 예정 (테스트 모드){Colors.END}")
            return True

    def verify_removal(self) -> Tuple[int, int]:
        """
        항목이 실제로 제거되었는지 확인

        Returns:
            (성공적으로_제거됨, 여전히_존재함) 튜플
        """
        if self.dry_run:
            return (0, 0)

        print(f"\n{Colors.BOLD}🔍 제거 확인 중...{Colors.END}")
        print()

        removed_count = 0
        still_exists = 0

        for item in self.removed_items:
            if item['type'] == 'directory':
                path = Path(item['path'])
                if not path.exists():
                    removed_count += 1
                    print(f"  {Colors.GREEN}✓{Colors.END} {item['name']} - 제거됨")
                else:
                    still_exists += 1
                    print(f"  {Colors.RED}✗{Colors.END} {item['name']} - 여전히 존재함")

        print()
        return (removed_count, still_exists)

    def show_summary(self, dirs: List[Dict], packages: List[Dict]):
        """
        수행되거나 수행될 작업의 요약 표시

        Args:
            dirs: 디렉토리 리스트
            packages: 패키지 리스트
        """
        print(f"{Colors.BOLD}📊 요약{Colors.END}")
        print("━" * 60)
        print()

        # 디렉토리
        if dirs:
            print(f"{Colors.BOLD}디렉토리:{Colors.END}")
            for dir_info in dirs:
                status = "제거될 예정" if self.dry_run else (
                    "✓ 제거됨" if dir_info.get('removed') else "✗ 실패"
                )
                print(f"  {status:<15} {dir_info['name']:<35} ({dir_info['size_formatted']})")
                if dir_info.get('backup_path'):
                    print(f"                  ↳ 백업 위치: {dir_info['backup_path']}")
            print()

        # 패키지
        if packages:
            print(f"{Colors.BOLD}NPM 패키지:{Colors.END}")
            for pkg_info in packages:
                status = "제거될 예정" if self.dry_run else (
                    "✓ 제거됨" if pkg_info.get('removed') else "✗ 실패"
                )
                print(f"  {status:<15} {pkg_info['name']:<35} (v{pkg_info['version']})")
            print()

        # 전체 크기
        print(f"{Colors.BOLD}확보될 공간:{Colors.END} {Colors.CYAN}{self.format_size(self.total_size)}{Colors.END}")
        print()

        # 오류
        if self.errors:
            print(f"{Colors.BOLD}{Colors.RED}발생한 오류:{Colors.END}")
            for error in self.errors:
                print(f"  ✗ {error['operation']}: {error['target']}")
                print(f"    {error['error']}")
            print()

    def generate_report(self, dirs: List[Dict], packages: List[Dict]) -> Dict:
        """
        JSON 보고서 생성

        Args:
            dirs: 디렉토리 리스트
            packages: 패키지 리스트

        Returns:
            보고서 딕셔너리
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'mode': '테스트 모드' if self.dry_run else '제거',
            'backup_enabled': self.backup,
            'base_directory': str(self.base_dir),
            'directories': dirs,
            'packages': packages,
            'total_size_bytes': self.total_size,
            'total_size_formatted': self.format_size(self.total_size),
            'errors': self.errors,
            'summary': {
                'directories_found': len(dirs),
                'packages_found': len(packages),
                'items_removed': len(self.removed_items),
                'errors_count': len(self.errors)
            }
        }

    def save_report(self, report: Dict, report_path: Path):
        """
        JSON 보고서를 파일에 저장

        Args:
            report: 보고서 딕셔너리
            report_path: 보고서 저장 경로
        """
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"{Colors.GREEN}✓ 보고서 저장됨: {report_path}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}✗ 보고서 저장 실패: {e}{Colors.END}")

    def run(self) -> int:
        """
        제거 도구 실행

        Returns:
            종료 코드: 0 (성공), 1 (오류), 4 (정리 실패)
        """
        self.print_header()

        # 검색
        dirs = self.scan_directories()
        packages = self.check_npm_packages()

        # 작업이 있는지 확인
        if not dirs and not packages:
            print(f"{Colors.GREEN}✓ claude-flow 설치를 찾을 수 없음{Colors.END}")
            print()
            return 0

        # 요약 표시
        self.show_summary(dirs, packages)

        # 테스트 모드가 아니면 확인
        if not self.dry_run:
            print(f"{Colors.BOLD}{Colors.RED}⚠️  경고: claude-flow가 영구적으로 제거됩니다{Colors.END}")
            if self.backup:
                print(f"{Colors.BLUE}ℹ  백업은 _backups/claude-flow-uninstall/에 저장됩니다{Colors.END}")
            print()

            response = input(f"{Colors.BOLD}제거를 진행하시겠습니까? (yes/no): {Colors.END}")
            print()

            if response.lower() not in ['yes', 'y']:
                print(f"{Colors.YELLOW}✗ 제거가 취소되었습니다{Colors.END}")
                print()
                return 0

        # 디렉토리 제거
        print(f"{Colors.BOLD}🗑️  디렉토리 제거 중...{Colors.END}")
        print()
        for dir_info in dirs:
            self.remove_directory(dir_info)
        print()

        # 패키지 제거
        if packages:
            print(f"{Colors.BOLD}🗑️  npm 패키지 제거 중...{Colors.END}")
            print()
            for pkg_info in packages:
                self.uninstall_npm_package(pkg_info)
            print()

            # npm 캐시 정리
            self.clean_npm_cache()
            print()

        # 확인
        if not self.dry_run and (dirs or packages):
            removed, still_exists = self.verify_removal()

            if still_exists > 0:
                print(f"{Colors.RED}⚠️  일부 항목을 제거할 수 없습니다{Colors.END}")
                print()
                return 4

        # 보고서 생성
        report = self.generate_report(dirs, packages)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.base_dir / '_config' / 'MOAI-ADK-KO' / 'reports' / f'claude-flow-uninstall_{timestamp}.json'
        self.save_report(report, report_path)
        print()

        # 최종 상태
        if self.dry_run:
            print(f"{Colors.BLUE}ℹ  테스트 모드 완료 - 변경 사항 없음{Colors.END}")
            print()
            return 0
        elif self.errors:
            print(f"{Colors.YELLOW}⚠️  제거가 오류와 함께 완료되었습니다{Colors.END}")
            print()
            return 1
        else:
            print(f"{Colors.GREEN}✅ Claude-Flow가 성공적으로 제거되었습니다!{Colors.END}")
            print()
            return 0


async def agent_mode(uninstaller: ClaudeFlowUninstaller):
    """
    AI 가이드 제거를 위한 Claude Agent SDK 모드

    Args:
        uninstaller: ClaudeFlowUninstaller 인스턴스
    """
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions
    except ImportError:
        print(f"{Colors.YELLOW}⚠️  Claude Agent SDK가 설치되지 않았습니다{Colors.END}")
        print("설치 방법: pip install claude-agent-sdk")
        print()
        print("독립 실행 모드로 전환 중...")
        return uninstaller.run()

    print()
    print(f"{Colors.BOLD}🤖 Claude Agent SDK 모드{Colors.END}")
    print("━" * 60)
    print()

    # 먼저 검색
    dirs = uninstaller.scan_directories()
    packages = uninstaller.check_npm_packages()

    # Claude를 위한 컨텍스트 준비
    context = {
        'directories': [d['name'] for d in dirs],
        'packages': [p['name'] for p in packages],
        'total_size': uninstaller.format_size(uninstaller.total_size),
        'dry_run': uninstaller.dry_run,
        'backup': uninstaller.backup
    }

    prompt = f"""claude-flow 제거를 계획 중입니다. 발견된 항목은 다음과 같습니다:

제거할 디렉토리:
{chr(10).join('- ' + d for d in context['directories']) if context['directories'] else '- 발견된 항목 없음'}

제거할 NPM 패키지:
{chr(10).join('- ' + p for p in context['packages']) if context['packages'] else '- 발견된 항목 없음'}

확보될 공간: {context['total_size']}
모드: {'테스트 모드 (미리보기만)' if context['dry_run'] else '전체 제거'}
백업 활성화: {'예' if context['backup'] else '아니오'}

다음을 제공해주세요:
1. 제거될 항목 평가
2. 잠재적인 문제나 경고 사항
3. 안전하게 진행하기 위한 권장 사항
4. 완전한 제거인지 여부

구체적이고 실행 가능한 내용으로 작성해주세요."""

    options = ClaudeAgentOptions(
        system_prompt="당신은 claude-flow 제거를 돕는 유용한 도우미입니다.",
        permission_mode='default'
    )

    print("🤖 Claude로 분석 중...\n")

    async for message in query(prompt=prompt, options=options):
        if hasattr(message, 'content'):
            for block in message.content:
                if hasattr(block, 'text'):
                    print(block.text)

    print()
    print("━" * 60)
    print()

    # 사용자에게 진행 여부 확인
    if not uninstaller.dry_run:
        response = input(f"{Colors.BOLD}AI 분석 결과를 바탕으로 제거를 진행하시겠습니까? (yes/no): {Colors.END}")
        print()

        if response.lower() not in ['yes', 'y']:
            print(f"{Colors.YELLOW}✗ 제거가 취소되었습니다{Colors.END}")
            print()
            return 0

    return uninstaller.run()


def main():
    """메인 진입점"""
    parser = argparse.ArgumentParser(
        description="종합 claude-flow 제거 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  %(prog)s                        # 제거될 항목 미리보기
  %(prog)s --dry-run              # 위와 동일 (명시적)
  %(prog)s --yes                  # 확인 없이 제거
  %(prog)s --backup               # 제거 전 백업
  %(prog)s --agent                # AI 가이드 제거
  %(prog)s --backup --yes         # 백업 후 제거

종료 코드:
  0 - 성공 또는 작업 없음
  1 - 제거 중 오류 발생
  4 - 정리 확인 실패
        """
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="제거될 항목 미리보기 (변경 없음)"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="디렉토리 제거 전 백업 생성"
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="확인 프롬프트 건너뛰기"
    )
    parser.add_argument(
        "--agent",
        action="store_true",
        help="AI 가이드 제거를 위해 Claude Agent SDK 사용"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="상세 출력 표시"
    )

    args = parser.parse_args()

    # 작업이 지정되지 않은 경우 기본적으로 테스트 모드
    if not args.yes and not args.agent:
        args.dry_run = True

    # 제거 도구 생성
    uninstaller = ClaudeFlowUninstaller(
        dry_run=args.dry_run,
        backup=args.backup,
        verbose=args.verbose
    )

    # 모드 선택
    if args.agent:
        import anyio
        return anyio.run(agent_mode, uninstaller)
    else:
        return uninstaller.run()


if __name__ == "__main__":
    sys.exit(main())
