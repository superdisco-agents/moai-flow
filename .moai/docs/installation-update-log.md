# MoAI-ADK Installation & Update Log

## Update to v0.30.2

**Date**: November 28, 2025
**Workspace**: `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/`
**Source**: `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai-adk/`
**Status**: ✅ Completed Successfully

### Environment

- **Python Version**: 3.13.6
- **Python Path**: `/opt/homebrew/bin/python3`
- **Virtual Environment**: `.venv` (created at workspace root)
- **Installation Type**: Development/Editable (`pip install -e`)

### Version Changes

- **Previous Version**: 0.27.2
- **Updated Version**: 0.30.2
- **Git Tag**: `v0.30.2` (detached HEAD state)
- **GitHub Release**: https://github.com/modu-ai/moai-adk/releases/tag/v0.30.2

### Installation Steps Performed

1. ✅ Created Python virtual environment at workspace root
2. ✅ Installed MoAI-ADK in development mode with dev dependencies
3. ✅ Fetched latest git tags from GitHub
4. ✅ Checked out v0.30.2 tag
5. ✅ Reinstalled in development mode to link v0.30.2 source
6. ✅ Copied fresh v0.30.2 configuration files to workspace
7. ✅ Verified installation and version

### New Dependencies (v0.30.2)

The following dependencies were added in v0.30.2:

- **google-genai** (1.52.0) - Gemini 3 Pro integration for image generation
- **pillow** (12.0.0) - Image processing for nano-banana skill
- **pydantic** (2.11.2) - Data validation
- **httpx** (0.29.3) - Async HTTP client
- **websockets** (15.1) - WebSocket support
- **aiohttp** (3.13.2) - Async HTTP server

### Configuration Updates (v0.30.2)

#### New Git Strategy System

Three workflow presets added:

1. **manual-local.json** - Local Git only, manual branch creation
2. **personal-github.json** - GitHub individual project with automation
3. **team-github.json** - GitHub team project with full governance

Configuration location: `.moai/config/presets/`

#### Updated Config Structure

- **Version field**: Now tracks `0.30.2`
- **Version check**: Enabled with 24-hour cache TTL
- **Git strategy**: Mode-based presets (manual/personal/team)
- **Branch creation**: New prompt_always and auto_enabled flags

### Verification Results

```bash
# Version check
$ moai-adk --version
MoAI-ADK, version 0.30.2

# Package details
$ pip show moai-adk
Version: 0.30.2
Location: /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.venv/lib/python3.13/site-packages

# Python import verification
>>> import moai_adk
>>> moai_adk.__version__
'0.30.2'
>>> moai_adk.__file__
'/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai-adk/src/moai_adk/__init__.py'

# Configuration files
$ ls -la .moai/config/presets/
-rw-r--r--  manual-local.json (5460 bytes)
-rw-r--r--  personal-github.json (6028 bytes)
-rw-r--r--  team-github.json (8367 bytes)
```

### Files Installed/Updated

#### Configuration Directories
- `.moai/` - MoAI configuration root
  - `config/config.json` - Main configuration (v0.30.2)
  - `config/presets/` - Git workflow presets (NEW)
  - `config/statusline-config.yaml` - Status line config
  - `memory/` - Agent memory system (7 files)
  - `skills/` - Unified skills directory (3 core skills)

#### Claude Code Integration
- `.claude/commands/moai/` - 7 MoAI commands
  - `0-project.md` - Project initialization
  - `1-plan.md` - SPEC generation
  - `2-run.md` - TDD implementation
  - `3-sync.md` - Documentation sync
  - `9-feedback.md` - Feedback submission
  - `99-release.md` - Release management (local-only)
  - `cleanup.md` - Cleanup utilities

#### MCP Configuration
- `.mcp.json` - MCP server configuration
  - context7 (latest)
  - playwright (latest)
  - figma-dev-mode-mcp-server (SSE)
  - sequential-thinking (latest)

### Installation Mode

**Editable Installation** (Development Mode):
- Source code changes are immediately reflected
- No reinstallation needed after modifications
- Ideal for contributing to MoAI-ADK development

Location mapping:
```
Package: /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.venv/lib/python3.13/site-packages/moai_adk
Source:  /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/moai-adk/src/moai_adk
```

### Next Steps

The workspace is now fully configured with MoAI-ADK v0.30.2. To begin using:

1. **Activate virtual environment**:
   ```bash
   cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk
   source .venv/bin/activate
   ```

2. **Launch Claude Code**:
   ```bash
   claude
   ```

3. **Initialize a project** (optional):
   ```bash
   moai-adk init <project-directory>
   ```

4. **Configure git strategy** (edit `.moai/config/config.json`):
   - Set `git_strategy.mode` to `"manual"`, `"personal"`, or `"team"`
   - Preset files are auto-loaded from `.moai/config/presets/`

5. **Use MoAI commands** within Claude Code:
   - `/moai:0-project` - Initialize project
   - `/moai:1-plan` - Generate SPEC
   - `/moai:2-run` - Implement with TDD
   - `/moai:3-sync` - Sync documentation

### Known Issues

None. Installation completed successfully with all verification checks passing.

### Maintenance Notes

- **Virtual environment**: Located at `.venv`, activate before use
- **Source updates**: Run `git pull` in `moai-adk/` subdirectory, then reinstall with `pip install -e './moai-adk[dev]'`
- **Configuration backup**: Configuration files are version-controlled
- **Dependency updates**: Use `pip install -e './moai-adk[dev]' --upgrade` to update dependencies

---

**Installation completed**: November 28, 2025
**MoAI-ADK version**: 0.30.2
**Installation type**: Development (editable)
**Verification**: ✅ All checks passed
