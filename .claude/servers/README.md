# MoAI-ADK MCP Servers

> MCP (Model Context Protocol) servers configuration for MoAI-ADK agents.

## Overview

This directory contains configuration files for MCP servers used by MoAI-ADK agents. The main configuration is in `.mcp.json` at the project root.

## Installed Servers

| Server | Package | Status | Purpose |
|--------|---------|--------|---------|
| Context7 | `@upstash/context7-mcp@latest` | Required | Documentation research, API references |
| Playwright | `@playwright/mcp@latest` | Required | Browser automation, E2E testing |
| Sequential-Thinking | `@modelcontextprotocol/server-sequential-thinking@latest` | Required | Complex reasoning, architecture design |
| Figma Dev Mode | Local SSE (port 3845) | Optional | Design analysis, design-to-code |
| GitHub | `@modelcontextprotocol/server-github` | Optional | PR/Issue management |
| Notion | `@notionhq/notion-mcp-server` | Optional | Workspace management |

## Environment Variables

### Required

```bash
# GitHub MCP Server
export GITHUB_PAT_TOKEN="github_pat_xxx..."

# Notion MCP Server
export NOTION_API_KEY="secret_xxx..."
```

### Environment File Location

GitHub token is stored at:
```
/Users/rdmtv/Documents/claydev-local/Config/_config/github.env
```

## Server Details

### 1. Context7 (Required)

**Purpose**: Real-time documentation retrieval for 40+ agents.

**Used By**: All expert-*, manager-*, mcp-* agents

**Tools Provided**:
- `mcp__context7__resolve-library-id` - Resolve library names to IDs
- `mcp__context7__get-library-docs` - Fetch library documentation

**No environment variables required.**

### 2. Playwright (Required)

**Purpose**: Browser automation and E2E testing.

**Used By**: mcp-playwright, accessibility-expert, expert-uiux

**Tools Provided**:
- `mcp__playwright__browser_navigate`
- `mcp__playwright__browser_snapshot`
- `mcp__playwright__browser_click`
- `mcp__playwright__browser_type`
- And many more...

**No environment variables required.**

### 3. Sequential-Thinking (Required)

**Purpose**: Complex multi-step reasoning and architecture design.

**Used By**: mcp-sequential-thinking

**Tools Provided**:
- `mcp__sequential-thinking__sequentialthinking`

**No environment variables required.**

### 4. Figma Dev Mode (Optional)

**Purpose**: Design analysis, design-to-code conversion.

**Used By**: mcp-figma, mcp-figma-integrator, expert-uiux

**Requirements**:
- Figma Desktop app installed
- Dev Mode enabled in Figma
- Local server running on port 3845

**Tools Provided**:
- `mcp__figma-dev-mode-mcp-server__get_design_context`
- `mcp__figma-dev-mode-mcp-server__get_variable_defs`
- `mcp__figma-dev-mode-mcp-server__get_screenshot`
- `mcp__figma-dev-mode-mcp-server__get_metadata`

### 5. GitHub (Optional)

**Purpose**: GitHub PR/Issue management.

**Used By**: devops-expert, expert-devops

**Environment Variables**:
```bash
GITHUB_PAT_TOKEN=github_pat_xxx...
```

**Tools Provided**:
- `mcp__github__create-or-update-file`
- `mcp__github__push-files`

### 6. Notion (Optional)

**Purpose**: Notion workspace management.

**Used By**: mcp-notion, mcp-notion-integrator

**Environment Variables**:
```bash
NOTION_API_KEY=secret_xxx...
```

## Troubleshooting

### Server Not Loading

1. Check if `.mcp.json` exists at project root
2. Verify JSON syntax is valid
3. Restart Claude Code session
4. Check environment variables are set

### Context7 Not Working

```bash
# Test manually
npx -y @upstash/context7-mcp@latest
```

### Playwright Not Working

```bash
# Test manually
npx -y @playwright/mcp@latest

# May need to install browsers
npx playwright install
```

### Figma Connection Failed

1. Ensure Figma Desktop is running
2. Enable Dev Mode in Figma
3. Check if port 3845 is available
4. Verify SSE endpoint: `http://127.0.0.1:3845/sse`

## File Structure

```
.claude/servers/
├── README.md                    # This file
├── context7.json               # Context7 configuration
├── playwright.json             # Playwright configuration
├── sequential-thinking.json    # Sequential-Thinking configuration
├── figma.json                  # Figma Dev Mode configuration
├── github.json                 # GitHub configuration
└── notion.json                 # Notion configuration
```

## Related Documentation

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Context7 Documentation](https://context7.io/)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [Figma Dev Mode](https://www.figma.com/developers/api)

---

**Last Updated**: 2025-11-29
**Version**: 1.0.0
