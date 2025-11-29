# Project-Specific Figma MCP Server Configuration

**Project**: moai-adk
**Location**: `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/mcp-figma/`
**Purpose**: Project-specific Figma MCP configuration (not global)

---

## Overview

This directory contains project-specific configuration for the Figma Dev Mode MCP Server, allowing you to use Figma design-to-code capabilities in this project without affecting global Claude Code settings.

---

## Installation

### Option 1: Use Project Settings (Recommended)

Create a `.claude/settings.json` in your project root:

```bash
# From project root
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk

# Create .claude directory
mkdir -p .claude

# Copy the MCP configuration
cp _config/mcp-figma/settings.json .claude/settings.json
```

### Option 2: Symlink Configuration

```bash
# From project root
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk

# Create .claude directory
mkdir -p .claude

# Symlink the configuration
ln -s $(pwd)/_config/mcp-figma/settings.json .claude/settings.json
```

### Option 3: Merge with Existing Project Config

If you already have a `.claude/settings.json`:

```bash
# Manually merge the mcpServers section from:
_config/mcp-figma/settings.json
# Into your existing:
.claude/settings.json
```

---

## Files in This Directory

### 1. `settings.json`
Project-specific MCP server configuration:
```json
{
  "mcpServers": {
    "figma-dev-mode-mcp-server": {
      "transport": "http",
      "url": "http://127.0.0.1:3845/mcp"
    }
  }
}
```

### 2. `FIGMA_MCP_SETUP_GUIDE.md`
Complete installation and usage guide including:
- How Figma MCP works
- Desktop vs Remote server options
- Step-by-step setup instructions
- Usage examples and prompts
- Troubleshooting tips

### 3. `README.md` (this file)
Project-specific installation instructions

---

## How Project-Specific MCP Works

### Configuration Hierarchy (Highest to Lowest Precedence)

According to https://claudelog.com/configuration/#mcp-configuration:

```
1. Project local settings      → <project>/.claude/settings.json
2. Project shared settings      → <project>/.claude/settings.json
3. Global user settings         → ~/.claude/settings.json
4. Global CLI config            → ~/.claude.json
```

**This means**:
- Project `.claude/settings.json` **overrides** global `~/.claude.json`
- You can have different MCP servers per project
- Global servers still available unless overridden

---

## Enable Figma MCP Server

**Important**: The configuration only tells Claude Code where to connect. You still need to enable the server in Figma.

### Quick Setup:

1. **Enable in Figma Desktop**:
   - Open Figma app
   - Open a Design file
   - Press `Shift + D` (Dev Mode)
   - Find "MCP server" section
   - Click "Enable desktop MCP server"
   - Verify: "Desktop MCP server is running"

2. **Install Project Config**:
   ```bash
   cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk
   mkdir -p .claude
   cp _config/mcp-figma/settings.json .claude/settings.json
   ```

3. **Restart Claude Code** in this project directory

4. **Test**:
   ```
   "Using Figma MCP, show me available tools"
   ```

---

## Usage in This Project

### Design-to-Code for moai-adk

**Example: Convert Figma mockup to React component**
```
"Using Figma MCP, convert this design to a React component with TypeScript and Tailwind:
https://figma.com/file/..."
```

**Example: Extract design tokens**
```
"Using Figma MCP, extract all color variables, spacing tokens, and typography
from this frame and create a tokens.ts file for moai-adk"
```

**Example: Generate with project structure**
```
"Using Figma MCP, implement this component following moai-adk's structure:
- Use components from src/components/
- Use design tokens from src/tokens.ts
- Follow naming conventions in this project

Design link: [paste link]"
```

---

## Project-Specific Benefits

### Why Project-Specific?

1. **Different MCP servers per project**
   - moai-adk might use Figma MCP
   - Other projects might use different MCPs
   - No conflicts between projects

2. **Team sharing**
   - Commit `.claude/settings.json` to git
   - Team members get same MCP setup
   - Consistent development experience

3. **Version control**
   - Track MCP configuration changes
   - Rollback if needed
   - Document server requirements

4. **Isolation**
   - Changes don't affect global config
   - Test new MCP servers safely
   - Easy to remove (delete `.claude/` folder)

---

## Verify Installation

```bash
# From project root
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk

# Check if .claude/settings.json exists
ls -la .claude/settings.json

# View configuration
cat .claude/settings.json

# Start Claude Code in this directory
claude

# Test Figma MCP
# "Using Figma MCP, show me available tools"
```

---

## Troubleshooting

### Issue: MCP server not detected

**Check**:
1. Are you in the project directory?
   ```bash
   pwd
   # Should be: /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk
   ```

2. Does `.claude/settings.json` exist?
   ```bash
   cat .claude/settings.json
   ```

3. Is Figma MCP server running?
   ```bash
   curl -v http://127.0.0.1:3845/mcp
   ```

### Issue: Global MCP conflicts

**Solution**: Project config overrides global, so no conflicts. But if you want to disable global Figma MCP:

```bash
# Edit global config
code ~/.claude.json

# Remove figma-dev-mode-mcp-server from mcpServers section
```

---

## Migration from Global to Project-Specific

If you previously had Figma MCP in global `~/.claude.json`:

```bash
# 1. Copy project config
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk
mkdir -p .claude
cp _config/mcp-figma/settings.json .claude/settings.json

# 2. (Optional) Remove from global config
# Edit ~/.claude.json and remove figma-dev-mode-mcp-server

# 3. Restart Claude Code in project directory
```

---

## Related Resources

- **Setup Guide**: `./FIGMA_MCP_SETUP_GUIDE.md`
- **Configuration Docs**: https://claudelog.com/configuration/#mcp-configuration
- **Figma MCP Docs**: https://developers.figma.com/docs/figma-mcp-server/
- **MCP Spec**: https://spec.modelcontextprotocol.io/

---

## Summary

✅ **Project-specific** Figma MCP configuration
✅ **Isolated** from global settings
✅ **Shareable** with team via git
✅ **Easy to install** with provided files

**Next Steps**:
1. Copy `settings.json` to project `.claude/` directory
2. Enable Figma MCP server in Figma Dev Mode
3. Restart Claude Code in project directory
4. Start converting Figma designs to code!

---

**Created**: 2025-11-29
**Project**: moai-adk
**Purpose**: Project-specific Figma design-to-code integration
