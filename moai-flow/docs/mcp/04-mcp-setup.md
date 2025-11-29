# MCP Server Setup

> Quick setup guide for MoAI-Flow (native) servers

## Overview

MoAI-Flow uses several MCP servers for different capabilities. This guide covers installation and configuration.

---

## Quick Setup Commands

### Required: MoAI-Flow (native)

```bash
claude mcp add moai-flow npx moai-flow@alpha mcp start
```

### Optional: Enhanced Swarm

```bash
claude mcp add ruv-swarm npx ruv-swarm mcp start
```

### Optional: Cloud Features

```bash
claude mcp add flow-nexus npx flow-nexus@latest mcp start
```

---

## Configuration File

Add to `.mcp.json`:

```json
{
  "mcpServers": {
    "moai-flow": {
      "command": "npx",
      "args": ["moai-flow@alpha", "mcp", "start"]
    },
    "ruv-swarm": {
      "command": "npx",
      "args": ["ruv-swarm", "mcp", "start"]
    },
    "flow-nexus": {
      "command": "npx",
      "args": ["flow-nexus@latest", "mcp", "start"]
    }
  }
}
```

---

## Server Descriptions

### moai-flow (Required)

**Purpose**: Core swarm coordination

**Tools Provided**:
- Swarm initialization
- Agent coordination
- Task orchestration
- Memory management

**No authentication required.**

### ruv-swarm (Optional)

**Purpose**: Enhanced coordination patterns

**Tools Provided**:
- Additional topology options
- Enhanced consensus
- Performance optimization

**No authentication required.**

### flow-nexus (Optional)

**Purpose**: Cloud-based features

**Tools Provided**:
- Cloud execution
- Sandboxes
- Templates
- Storage

**Requires registration.**

---

## MoAI Current MCP Setup

MoAI's `.mcp.json`:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking@latest"]
    },
    "figma-dev-mode-mcp-server": {
      "type": "sse",
      "url": "http://127.0.0.1:3845/sse"
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "..."
      }
    },
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "NOTION_API_KEY": "..."
      }
    }
  }
}
```

---

## Adding MoAI-Flow to MoAI

### Step 1: Add to .mcp.json

```json
{
  "mcpServers": {
    // ... existing servers ...

    "moai-flow": {
      "command": "npx",
      "args": ["-y", "moai-flow@alpha", "mcp", "start"]
    }
  }
}
```

### Step 2: Update settings.json

Add permissions:
```json
{
  "permissions": {
    "allow": [
      "mcp__moai-flow__*"
    ]
  }
}
```

### Step 3: Restart Claude Code

```bash
# Restart to load new MCP server
```

---

## Verification

### Check Server Status

```javascript
// Test MoAI-Flow server
mcp__moai-flow__swarm_status {}

// Should return swarm state
```

### Check Available Tools

After adding, these tools become available:
- `mcp__moai-flow__swarm_init`
- `mcp__moai-flow__agent_spawn`
- `mcp__moai-flow__task_orchestrate`
- `mcp__moai-flow__swarm_status`
- `mcp__moai-flow__memory_*`
- `mcp__moai-flow__neural_*`

---

## Comparison

| Server | MoAI-Flow | MoAI |
|--------|-------------|------|
| Core MCP | moai-flow | - |
| Documentation | - | context7 |
| Browser | - | playwright |
| Reasoning | - | sequential-thinking |
| Design | - | figma |
| GitHub | (in moai-flow) | github |
| Workspace | - | notion |

---

## Recommendation

### Minimal Addition

Add only `moai-flow` for swarm coordination:

```json
"moai-flow": {
  "command": "npx",
  "args": ["-y", "moai-flow@alpha", "mcp", "start"]
}
```

### Full Integration

Add all MoAI-Flow servers for complete feature parity (if needed).

---

## Troubleshooting

### Server Not Loading

1. Check `.mcp.json` syntax
2. Verify npx works: `npx moai-flow@alpha --version`
3. Restart Claude Code
4. Check permissions in settings.json

### Connection Errors

```bash
# Test manually
npx moai-flow@alpha mcp start
```

### Permission Denied

Add to `.claude/settings.json`:
```json
{
  "permissions": {
    "allow": ["mcp__moai-flow__*"]
  }
}
```
