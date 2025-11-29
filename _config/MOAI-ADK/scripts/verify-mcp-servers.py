#!/usr/bin/env python3
"""
MCP Server Verification Script
Tests if MCP servers are properly configured and accessible
Supports both standalone and Claude Agent SDK modes
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Try importing optional dependencies, install if needed
try:
    import requests
except ImportError:
    print("📦 Installing requests...")
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "-q"], check=True)
    import requests


class Colors:
    """Terminal color codes"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class MCPServer:
    """MCP Server configuration"""
    def __init__(self, name: str, config: dict):
        self.name = name
        self.type = config.get("type", "stdio")
        self.command = config.get("command", "")
        self.args = config.get("args", [])
        self.url = config.get("url", "")
        self.passed = False
        self.message = ""


def print_header():
    """Print formatted header"""
    print(f"\n{Colors.BOLD}🔌 MCP Server Verification{Colors.END}")
    print("━" * 44)
    print()


def load_mcp_config() -> Optional[Dict]:
    """
    Load MCP configuration from .mcp.json

    Returns:
        Dictionary of MCP server configurations or None if not found
    """
    mcp_file = Path(".mcp.json")

    if not mcp_file.exists():
        print(f"{Colors.RED}❌ Error: .mcp.json not found{Colors.END}")
        print("   Run the installation guide first")
        return None

    try:
        with open(mcp_file, 'r') as f:
            config = json.load(f)
            return config.get("mcpServers", {})
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}❌ Error parsing .mcp.json: {e}{Colors.END}")
        return None


def check_command_available(command: str) -> bool:
    """
    Check if a command is available in PATH

    Args:
        command: Command name to check

    Returns:
        True if command exists, False otherwise
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
    Verify npm package exists

    Args:
        package: Package name (e.g., "@upstash/context7-mcp@latest")

    Returns:
        True if package is valid, False otherwise
    """
    try:
        # Extract package name without version
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
    Test SSE server accessibility

    Args:
        url: Server URL to test

    Returns:
        True if accessible, False otherwise
    """
    try:
        response = requests.head(url, timeout=5)
        return response.status_code < 500
    except requests.RequestException:
        return False


def test_stdio_server(server: MCPServer) -> Tuple[bool, str]:
    """
    Test stdio-based MCP server

    Args:
        server: MCPServer instance

    Returns:
        Tuple of (success, message)
    """
    command = server.command
    args = server.args

    print(f"  Type: {Colors.BLUE}stdio{Colors.END}")
    print(f"  Command: {command} {' '.join(args)}")

    # Check if command exists
    if not check_command_available(command):
        return False, f"{command} not found"

    print(f"  Status: {Colors.GREEN}✅ {command} available{Colors.END}")

    # For npx commands, verify package
    if command == "npx" and args:
        package = args[-1] if args else ""

        if package:
            print(f"  Testing package: {package}")

            if verify_npm_package(package):
                print(f"  Package: {Colors.GREEN}✅ Available on npm{Colors.END}")
                return True, "Package verified"
            else:
                print(f"  Package: {Colors.YELLOW}⚠️  Could not verify{Colors.END}")
                print(f"  Note: Will be downloaded on first use")
                return True, "Package unverified but may work"

    return True, "Command available"


def test_sse_server_instance(server: MCPServer) -> Tuple[bool, str]:
    """
    Test SSE-based MCP server

    Args:
        server: MCPServer instance

    Returns:
        Tuple of (success, message)
    """
    url = server.url

    print(f"  Type: {Colors.BLUE}SSE{Colors.END}")
    print(f"  URL: {url}")

    if test_sse_server(url):
        print(f"  Status: {Colors.GREEN}✅ Accessible{Colors.END}")
        return True, "Server accessible"
    else:
        print(f"  Status: {Colors.YELLOW}⚠️  Not accessible{Colors.END}")
        print(f"  Note: Server may need to be started")
        return False, "Server not accessible (may need to start)"


def verify_servers(servers: Dict[str, MCPServer]) -> Tuple[int, int, int]:
    """
    Verify all MCP servers

    Args:
        servers: Dictionary of MCPServer instances

    Returns:
        Tuple of (total, passed, failed) counts
    """
    print(f"{Colors.BOLD}📋 Configured MCP Servers{Colors.END}")
    print("━" * 44)
    print()

    total = len(servers)
    passed = 0
    failed = 0

    for name, server in servers.items():
        print(f"Testing: {Colors.BOLD}{name}{Colors.END}")

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
    """Print verification summary"""
    print("━" * 44)
    print(f"{Colors.BOLD}📊 Summary{Colors.END}")
    print("━" * 44)
    print()
    print(f"Total servers:  {total}")
    print(f"Passed:         {passed} {Colors.GREEN}✅{Colors.END}")
    print(f"Failed:         {failed} {Colors.RED}❌{Colors.END}")
    print()


def print_server_details():
    """Print detailed server information"""
    print(f"{Colors.BOLD}🔍 Server Details{Colors.END}")
    print("━" * 44)
    print()

    servers_info = [
        {
            "name": "context7",
            "title": "Documentation Retrieval",
            "purpose": "Real-time library documentation lookup",
            "package": "@upstash/context7-mcp@latest",
            "critical": "⭐⭐⭐",
            "note": "Prevents API hallucination"
        },
        {
            "name": "sequential-thinking",
            "title": "Complex Reasoning",
            "purpose": "Multi-step problem analysis",
            "package": "@modelcontextprotocol/server-sequential-thinking@latest",
            "critical": "⭐⭐",
            "note": "For complex architecture decisions"
        },
        {
            "name": "playwright",
            "title": "Browser Automation",
            "purpose": "Web testing and automation",
            "package": "@playwright/mcp@latest",
            "critical": "⭐",
            "note": "Optional for most workflows"
        },
        {
            "name": "figma-dev-mode-mcp-server",
            "title": "Design Integration",
            "purpose": "Figma design access",
            "type": "SSE (requires local server)",
            "critical": "⭐",
            "note": "Optional for design workflows"
        }
    ]

    for idx, info in enumerate(servers_info, 1):
        print(f"{idx}. {info['name']} ({info['title']})")
        print(f"   Purpose: {info['purpose']}")

        if 'package' in info:
            print(f"   Package: {info['package']}")
        if 'type' in info:
            print(f"   Type: {info['type']}")

        print(f"   Critical: {info['critical']} ({info['note']})")
        print()


def print_recommendations(failed: int):
    """Print recommendations based on results"""
    print("━" * 44)
    print(f"{Colors.BOLD}💡 Recommendations{Colors.END}")
    print("━" * 44)
    print()

    if failed > 0:
        print(f"{Colors.YELLOW}⚠️  Some servers are not accessible{Colors.END}")
        print()
        print("To fix:")
        print("  1. Install Node.js: https://nodejs.org/")
        print("  2. Ensure internet connection for npm packages")
        print("  3. For Figma: Start local server if needed")
        print()
        print("Claude Code will download missing packages on first use")
        print()
    else:
        print(f"{Colors.GREEN}✅ All MCP servers are configured correctly!{Colors.END}")
        print()
        print("Next steps:")
        print("  1. Launch Claude Code: claude")
        print("  2. Grant all MCP permissions when prompted")
        print("  3. Use MoAI commands: /moai:1-plan, /moai:2-run, etc.")
        print()


async def agent_mode(servers: Dict[str, MCPServer], total: int, passed: int, failed: int):
    """
    Claude Agent SDK mode for AI-enhanced diagnostics

    Args:
        servers: Dictionary of MCPServer instances
        total: Total server count
        passed: Passed server count
        failed: Failed server count
    """
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions
    except ImportError:
        print(f"{Colors.YELLOW}⚠️  Claude Agent SDK not installed{Colors.END}")
        print("Install with: pip install claude-agent-sdk")
        print()
        print("Showing standard results...")
        return

    print()
    print(f"{Colors.BOLD}🤖 Claude Agent SDK Mode{Colors.END}")
    print("━" * 44)
    print()

    # Prepare server status for Claude
    server_status = []
    for name, server in servers.items():
        status = {
            "name": name,
            "type": server.type,
            "passed": server.passed,
            "message": server.message
        }
        server_status.append(status)

    prompt = f"""I've verified the MCP servers for MoAI-ADK installation:

Total servers: {total}
Passed: {passed}
Failed: {failed}

Server details:
{json.dumps(server_status, indent=2)}

Please analyze this configuration and provide:
1. Assessment of the MCP server setup
2. Specific troubleshooting steps for any failures
3. Recommendations for optimization
4. Any potential issues or conflicts

Be concise and actionable."""

    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant for MCP server configuration and troubleshooting.",
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
        description="MCP Server verification for MoAI-ADK",
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
        help="Use Claude Agent SDK for AI-enhanced diagnostics"
    )

    args = parser.parse_args()

    print_header()

    # Load MCP configuration
    mcp_config = load_mcp_config()
    if mcp_config is None:
        return 1

    print(f"{Colors.GREEN}✅ Found .mcp.json configuration{Colors.END}")
    print()

    # Create server instances
    servers = {
        name: MCPServer(name, config)
        for name, config in mcp_config.items()
    }

    # Verify servers
    total, passed, failed = verify_servers(servers)

    # Print results
    print_summary(total, passed, failed)
    print_server_details()
    print_recommendations(failed)

    # Agent mode if requested
    if args.agent:
        import anyio
        anyio.run(agent_mode, servers, total, passed, failed)

    # Exit code
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
