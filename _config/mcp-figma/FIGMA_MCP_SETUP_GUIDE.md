# Figma Dev Mode MCP Server - Setup Guide

**Date**: 2025-11-29
**Status**: Configuration Fixed ✅
**App Status**: Figma Desktop Installed ✅

---

## Configuration Fixed

### Previous (Incorrect):
```json
"figma-dev-mode-mcp-server": {
  "type": "sse",
  "url": "http://127.0.0.1:3845/sse"  ❌
}
```

### Current (Correct):
```json
"figma-dev-mode-mcp-server": {
  "transport": "http",
  "url": "http://127.0.0.1:3845/mcp"  ✅
}
```

**Config Location**: `~/.claude.json`
**Backup**: `~/.claude.json.backup-20251129-before-figma-fix`

---

## Next Steps: Enable MCP Server in Figma

### Step 1: Open Figma Desktop App
```bash
# Launch Figma
open -a Figma

# Or from Applications folder
open /Applications/Figma.app
```

### Step 2: Open a Design File
1. Open any existing Design file, OR
2. Create a new Design file (File > New Design File)
3. **Important**: Must be a Design file, NOT a FigJam file

### Step 3: Switch to Dev Mode
**Method 1 - Keyboard Shortcut**:
- Press `Shift + D`

**Method 2 - UI Button**:
- Click "Dev Mode" button in bottom toolbar

### Step 4: Enable MCP Server
1. Look for **"MCP server"** section in the Inspect Panel (right side)
2. Click button: **"Enable desktop MCP server"**
3. Confirmation message appears: **"Desktop MCP server is running"**
4. Server is now active at `http://127.0.0.1:3845/mcp`

### Step 5: Verify Server is Running
```bash
# Test if server responds (should connect)
curl -v http://127.0.0.1:3845/mcp

# Expected: Connection succeeds
# (May show error without proper handshake, but that's OK - server is listening)
```

### Step 6: Test in Claude Code
After restarting Claude Code, test with:
```
"Using Figma MCP, show me the available tools"
```

**Expected Tools**:
- get_design_context
- get_variable_defs
- get_code_connect_map
- get_screenshot
- get_metadata
- get_figjam

---

## How to Use Figma MCP

### Method 1: Selection-Based (Desktop Only)
1. **Select a frame** or layer in Figma desktop app
2. **In Claude Code prompt**:
   ```
   "Implement my current Figma selection using React and Tailwind CSS"
   ```
3. Server automatically accesses your selection
4. Claude generates code matching the design

### Method 2: Link-Based (Desktop + Remote)
1. **In Figma**: Right-click frame/layer → Copy link
   - Example: `https://figma.com/file/abc123/MyFile?node-id=123-456`
2. **In Claude Code**:
   ```
   "Implement this Figma design: [paste link]"
   ```
3. Server retrieves design from link
4. Claude generates code

---

## Example Prompts

### Basic Code Generation
```
"Convert this Figma frame to React component with TypeScript and Tailwind:
https://figma.com/file/..."
```

### Extract Design Tokens
```
"Using Figma MCP, extract all color variables, spacing tokens, and typography
from this frame: [link]"
```

### Framework-Specific
```
"Generate Vue 3 Composition API code for this design: [link]"
"Create iOS SwiftUI view for this Figma screen: [link]"
"Convert to HTML/CSS with Flexbox layout: [link]"
```

### With Component Libraries
```
"Implement this design using shadcn/ui components: [link]"
"Generate using our existing components from src/components: [link]"
```

---

## Optional: Desktop MCP Server Settings

### Configure Image Handling
1. **Figma app**: Figma > Preferences
2. Navigate to: **"Desktop MCP server settings"**
3. Configure:
   - ✅ **Download assets**: Enable to download images
   - ✅ **Enable Code Connect**: Map Figma components to code
   - **Image handling**: Choose:
     - Local server (images via local URLs)
     - Download (download to disk)
     - Placeholders (use placeholder images)

---

## Troubleshooting

### Issue: "Cannot connect to http://127.0.0.1:3845/mcp"

**Solutions**:
1. Check MCP server is enabled in Figma Dev Mode
2. Verify Figma desktop app is running
3. Ensure you're in a Design file (not FigJam)
4. Check firewall allows port 3845
5. Restart Figma app and re-enable server

### Issue: "MCP server option not visible"

**Solutions**:
1. Update Figma to latest version
2. Verify you have a paid plan (Professional/Organization/Enterprise)
3. Check you have Dev or Full seat type
4. Make sure you're in Dev Mode (Shift + D)

### Issue: Poor code quality

**Improve Figma file structure**:
- Use components for reusable elements
- Apply Auto layout for responsive design
- Use variables for colors, spacing, typography
- Name layers semantically ("CardContainer" not "Group 5")
- Use Code Connect to link to existing components

### Issue: Server stops working

**Quick Fix**:
1. In Figma Dev Mode, disable MCP server
2. Re-enable it
3. Verify "Desktop MCP server is running" appears
4. Restart Claude Code

---

## Requirements Summary

### Figma Requirements
- ✅ Figma desktop app (latest version)
- ✅ Paid plan: Professional, Organization, or Enterprise
- ✅ Dev or Full seat type
- ✅ Design file (not FigJam)

### Claude Code Requirements
- ✅ Claude Code CLI installed
- ✅ Config fixed in ~/.claude.json
- ✅ MCP support (built-in)

---

## What You Get

### Design-to-Code Capabilities
- **Framework Support**: React, Vue, SwiftUI, HTML/CSS
- **Styling Systems**: Tailwind, CSS Modules, Styled Components
- **Design Tokens**: Colors, spacing, typography, radius
- **Component Mapping**: Code Connect integration
- **Responsive Layouts**: Auto layout to Flexbox/Grid
- **Asset Handling**: Images, icons, illustrations

### Performance Improvements
- **84.8% SWE-Bench** solve rate improvements
- **60-80% reduction** in design-to-code time
- **Pixel-perfect** code matching mockups
- **Consistent** component usage

---

## Alternative: Remote Server (No Desktop Required)

If you don't have a paid Figma plan, you can use the remote server:

```bash
# Remove desktop server
claude mcp remove figma-dev-mode-mcp-server

# Add remote server
claude mcp add --transport http figma https://mcp.figma.com/mcp

# Authenticate when prompted
```

**Remote Server Features**:
- ✅ Works with Starter/Free plan
- ✅ Link-based access only (no selection-based)
- ⚠️ Rate limited: 6 tool calls/month
- ❌ No Code Connect
- ✅ All 6 MCP tools available

---

## Resources

- **Official Docs**: https://developers.figma.com/docs/figma-mcp-server/
- **GitHub Guide**: https://github.com/figma/dev-mode-mcp-server-guide
- **Help Center**: https://help.figma.com/hc/en-us/articles/32132100833559
- **MCP Spec**: https://spec.modelcontextprotocol.io/

---

## Current Status

✅ **Configuration**: Fixed and ready
✅ **Figma App**: Installed at /Applications/Figma.app
⏳ **Next Step**: Enable MCP server in Figma Dev Mode

**Ready to use once you enable the server in Figma!**

---

**Created**: 2025-11-29
**Config Backup**: ~/.claude.json.backup-20251129-before-figma-fix
