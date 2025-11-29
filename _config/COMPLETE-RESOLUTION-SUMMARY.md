# 401 Authentication Error - Complete Resolution Summary

**Date**: November 29, 2025
**Final Status**: ✅ FULLY RESOLVED
**Issue Type**: LOCAL CONFIGURATION (Not a moai-adk bug)

---

## Quick Summary

The persistent 401 authentication errors in the moai-adk project have been completely resolved. The issue was caused by local configuration conflicts - specifically an invalid placeholder API key in the shell environment combined with a locally-added GLM proxy configuration that was overriding Claude subscription authentication.

**Key Finding**: This was NOT a bug in the moai-adk framework - it was entirely a local configuration issue.

---

## What Was Fixed

### 1. Root Causes Identified and Resolved

#### Primary Issue: Invalid API Key in Environment
- **Location**: `~/.zshrc` line 301
- **Problem**: `export ANTHROPIC_API_KEY="YOUR_ACTUAL_API_KEY_HERE"`
- **Fix**: Commented out the line and added `unset ANTHROPIC_API_KEY` at line 15

#### Secondary Issue: GLM Proxy Configuration Override
- **Location**: `.claude/settings.local.json`
- **Problem**: GLM proxy tokens overriding subscription auth
- **Fix**: Removed GLM configuration, kept only permissions

### 2. Services Removed

#### SpecStory Complete Removal
- ✅ Uninstalled via Homebrew
- ✅ Removed all aliases from .zshrc
- ✅ Archived 400+ .specstory folders to organized hierarchy
- ✅ Killed background daemon processes
- ✅ Created archive at `/Users/rdmtv/Documents/claydev-local/projects-v2/specstory-backup`

#### SuperMemory Cleanup
- ✅ Killed 22+ zombie MCP processes
- ✅ Removed all SuperMemory files and caches
- ✅ Cleaned up MCP server configurations

### 3. cy4/cy5 Fixes Applied

#### Shell Function Updates
- Updated cy4 function (lines 531-545 in .zshrc)
- Updated cy5 function (lines 547-561 in .zshrc)
- Both now unset ANTHROPIC_API_KEY before execution

#### Wrapper Script Created
- Created `/Users/rdmtv/.local/bin/cy4-wrapper`
- Symlinked cy4 to use wrapper
- Ensures clean environment for Claude Code

---

## Documentation Created

### In `.claude/` Directory
1. `401-AUTH-FIX-SUMMARY.md` - Initial fix summary
2. `401-ERROR-FIXES-APPLIED.md` - Applied fixes documentation
3. `API_KEY_SETUP.md` - API key configuration guide
4. `AUDIT-REPORT-401-FIXES.md` - Complete audit report
5. `COMPLETE-REMOVAL-REPORT.md` - SpecStory/SuperMemory removal
6. `CY4-FIX-COMPLETE.md` - cy4/cy5 wrapper documentation
7. `FINAL-401-ERROR-RESOLUTION.md` - Final resolution details
8. `FINAL-401-FIX-COMPLETE.md` - Final fix confirmation
9. `FINAL-FIX-INSTRUCTIONS.md` - User instructions
10. `GLM-TOKEN-RESTORED-FIX.md` - GLM restoration documentation
11. `PATH-FIXED-SUMMARY.md` - Path correction summary
12. `SUBSCRIPTION_AUTH_SETUP.md` - Subscription auth guide

### In `_config/` Directory
1. **`401-AUTHENTICATION-ERROR-ROOT-CAUSE-ANALYSIS.md`** - Comprehensive 280-line root cause analysis with:
   - Complete timeline of events
   - Technical deep dive
   - Authentication hierarchy explanation
   - Prevention strategies
   - Lessons learned

---

## Authentication Hierarchy Explained

Claude Code follows this priority order (highest to lowest):

1. **Environment Variables** (e.g., ANTHROPIC_API_KEY)
2. **Project-Level Settings** (.claude/settings.local.json)
3. **Global Settings** (~/.claude/settings.json)
4. **Subscription Authentication** (Claude Pro/Max OAuth)

The issue occurred because invalid credentials at levels 1 and 2 prevented level 4 (subscription) from being used.

---

## Backup Files Created

All original configurations have been safely backed up:

1. `settings.local.json.glm-backup-20251129-135817` - GLM configuration
2. `settings.local.json.backup-20251128-223505` - Earlier backup
3. `settings.json.backup-401-fix-20251129-122922` - Settings backup
4. `/Users/rdmtv/.local/bin/cy4-original` - Original cy4 binary

---

## Current Working Configuration

### settings.local.json (Cleaned)
```json
{
  "permissions": {
    "allow": [
      "mcp__claude-flow__swarm_init",
      "mcp__claude-flow__agents_spawn_parallel",
      // ... other permissions only, no auth tokens
    ]
  }
}
```

### Environment
- ✅ No ANTHROPIC_API_KEY in environment
- ✅ Claude subscription authentication active
- ✅ cy4/cy5 commands working correctly

---

## Verification Steps

To verify everything is working:

```bash
# 1. Check environment is clean
printenv | grep ANTHROPIC_API_KEY
# Should return nothing

# 2. Navigate to moai-adk
cd ~/Documents/claydev-local/agent-os-v2/moai-adk

# 3. Launch Claude Code
claude
# Should work without 401 errors

# 4. Test cy4 command
cy4
# Should launch project selector without issues
```

---

## Prevention Strategies

1. **Never use placeholder API keys** - Remove or comment them immediately
2. **Document local customizations** - Track changes from upstream
3. **Understand auth hierarchy** - Know what overrides what
4. **Use proper .gitignore** - Keep .claude/ folder out of version control
5. **Regular cleanup** - Remove old backups and unused configs

---

## Key Lessons Learned

1. **Project-level settings override global settings** - Be careful with local configurations
2. **Environment variables have highest priority** - Always check for stray API keys
3. **Authentication methods don't mix** - GLM proxy and Claude subscription are incompatible
4. **Local customizations need documentation** - Always track what's been modified
5. **MoAI-ADK was innocent** - The framework itself had no bugs; issues were local

---

## Final Status

- ✅ All 401 errors resolved
- ✅ Authentication working correctly
- ✅ All services cleaned up
- ✅ Documentation complete
- ✅ Backups preserved
- ✅ Prevention strategies documented

**The moai-adk project is now fully functional with Claude subscription authentication.**

---

*This document serves as the final summary of the 401 authentication error investigation, resolution, and documentation effort.*