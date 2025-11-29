#!/usr/bin/env python3
"""
MoAI-ADK Smart Version Checker
Compares installed version with latest GitHub release
Supports both standalone and Claude Agent SDK modes
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

# Try importing optional dependencies, install if needed
try:
    import requests
except ImportError:
    print("📦 Installing requests...")
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "-q"], check=True)
    import requests

try:
    from packaging import version as pkg_version
except ImportError:
    print("📦 Installing packaging...")
    subprocess.run([sys.executable, "-m", "pip", "install", "packaging", "-q"], check=True)
    from packaging import version as pkg_version


class Colors:
    """Terminal color codes"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header():
    """Print formatted header"""
    print(f"\n{Colors.BOLD}🔍 MoAI-ADK Version Checker{Colors.END}")
    print("━" * 44)
    print()


def get_installed_version() -> Optional[str]:
    """
    Get currently installed MoAI-ADK version

    Returns:
        Version string (e.g., "0.30.2") or None if not installed
    """
    # Try CLI command first
    try:
        result = subprocess.run(
            ["moai-adk", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Extract version number from output
            import re
            match = re.search(r'\d+\.\d+\.\d+', result.stdout)
            if match:
                return match.group(0)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Fallback to Python import
    try:
        import moai_adk
        return moai_adk.__version__
    except ImportError:
        pass

    return None


def get_latest_version() -> Optional[str]:
    """
    Fetch latest MoAI-ADK version from GitHub

    Uses GitHub API with multiple fallbacks:
    1. Releases API (latest release)
    2. Tags API (if no releases)
    3. Git ls-remote (if API fails)

    Returns:
        Latest version string or None if fetch fails
    """
    print("📡 Fetching latest release from GitHub...", end=" ")

    # Try GitHub releases API
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

        # Fallback to tags API
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
        print(f"   API request failed: {e}")

    # Final fallback to git ls-remote
    try:
        print("   Trying git ls-remote...", end=" ")
        result = subprocess.run(
            ["git", "ls-remote", "--tags", "https://github.com/modu-ai/moai-adk.git"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            import re
            # Find all version tags
            tags = re.findall(r'refs/tags/v(\d+\.\d+\.\d+)$', result.stdout, re.MULTILINE)
            if tags:
                # Sort versions and get latest
                sorted_tags = sorted(tags, key=pkg_version.parse, reverse=True)
                print(f"{Colors.GREEN}✓{Colors.END}")
                return sorted_tags[0]

    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"{Colors.RED}✗{Colors.END}")
        print(f"   Git command failed: {e}")

    return None


def compare_versions(installed: Optional[str], latest: Optional[str]) -> int:
    """
    Compare versions and display results

    Args:
        installed: Installed version string
        latest: Latest available version string

    Returns:
        Exit code: 0 (up-to-date), 1 (fetch failed), 2 (not installed), 3 (update available)
    """
    print()
    print(f"{Colors.BOLD}📦 Version Information{Colors.END}")
    print("━" * 44)

    # Handle not installed
    if installed is None:
        print(f"Installed: {Colors.RED}❌ Not installed{Colors.END}")
        installed = "0.0.0"
    else:
        print(f"Installed: {Colors.GREEN}✅ v{installed}{Colors.END}")

    # Handle fetch failure
    if latest is None:
        print(f"Latest:    {Colors.YELLOW}⚠️  Could not fetch{Colors.END}")
        print()
        print("━" * 44)
        print()
        print(f"{Colors.RED}❌ GitHub API failed{Colors.END}")
        print("   Please check your internet connection")
        print()
        return 1

    print(f"Latest:    {Colors.BLUE}🌟 v{latest}{Colors.END}")
    print()
    print("━" * 44)
    print()

    # Compare versions
    if installed == "0.0.0":
        print(f"{Colors.BLUE}💡 Recommendation: Install MoAI-ADK{Colors.END}")
        print()
        print("Run the installation guide:")
        print("  cat _config/INSTALL-MOAI-ADK.md")
        print()
        return 2

    installed_ver = pkg_version.parse(installed)
    latest_ver = pkg_version.parse(latest)

    if installed_ver == latest_ver:
        print(f"{Colors.GREEN}✅ You have the latest version installed!{Colors.END}")
        print()
        return 0

    elif installed_ver < latest_ver:
        print(f"{Colors.YELLOW}⬆️  Update available: v{installed} → v{latest}{Colors.END}")
        print()
        print("To update, run:")
        print("━" * 44)
        print()
        print("# 1. Fetch latest release")
        print("cd moai-adk-source/moai-adk")
        print("git fetch --tags")
        print(f"git checkout v{latest}")
        print("cd ../..")
        print()
        print("# 2. Reinstall")
        print("source .venv/bin/activate")
        print("pip install -e './moai-adk-source/moai-adk[dev]' --upgrade")
        print()
        print("# 3. Update configuration")
        print("cp -r moai-adk-source/moai-adk/.moai .")
        print("cp -r moai-adk-source/moai-adk/.claude/commands/moai .claude/commands/")
        print("cp moai-adk-source/moai-adk/.mcp.json .")
        print("cp moai-adk-source/moai-adk/CLAUDE.md .")
        print()
        print("# 4. Verify")
        print("moai-adk --version")
        print("moai-adk doctor")
        print()
        return 3

    else:
        print(f"{Colors.YELLOW}⚠️  Installed version is newer than latest release{Colors.END}")
        print("   You may be using a development version")
        print()
        return 0


async def agent_mode(installed: Optional[str], latest: Optional[str]):
    """
    Claude Agent SDK mode for AI-enhanced version checking

    Args:
        installed: Installed version string
        latest: Latest available version string
    """
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions
    except ImportError:
        print(f"{Colors.YELLOW}⚠️  Claude Agent SDK not installed{Colors.END}")
        print("Install with: pip install claude-agent-sdk")
        print()
        print("Falling back to standalone mode...")
        return compare_versions(installed, latest)

    print()
    print(f"{Colors.BOLD}🤖 Claude Agent SDK Mode{Colors.END}")
    print("━" * 44)
    print()

    # Prepare context for Claude
    context = {
        "installed": installed or "Not installed",
        "latest": latest or "Unknown",
        "recommendation": "analyze"
    }

    prompt = f"""I'm checking the MoAI-ADK version status:

Installed version: {context['installed']}
Latest version: {context['latest']}

Please analyze this situation and provide:
1. A clear status assessment
2. Specific recommendations for the user
3. Any potential breaking changes if upgrading
4. Step-by-step update instructions if needed

Be concise and actionable."""

    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant for MoAI-ADK version management.",
        permission_mode='default'
    )

    print("🤖 Analyzing with Claude...\n")

    async for message in query(prompt=prompt, options=options):
        if hasattr(message, 'content'):
            for block in message.content:
                if hasattr(block, 'text'):
                    print(block.text)

    print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Smart MoAI-ADK version checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                # Standalone mode (fast)
  %(prog)s --agent        # AI-enhanced mode (requires claude-agent-sdk)
        """
    )
    parser.add_argument(
        "--agent",
        action="store_true",
        help="Use Claude Agent SDK for AI-enhanced analysis"
    )

    args = parser.parse_args()

    print_header()

    # Get versions
    installed = get_installed_version()
    latest = get_latest_version()

    # Choose mode
    if args.agent:
        import anyio
        anyio.run(agent_mode, installed, latest)
        return 0
    else:
        return compare_versions(installed, latest)


if __name__ == "__main__":
    sys.exit(main())
