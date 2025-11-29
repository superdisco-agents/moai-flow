# 401 Authentication Error - Complete Root Cause Analysis

**Date**: 2025-11-29
**Status**: ✅ RESOLVED
**Issue Type**: LOCAL CONFIGURATION (Not a moai-adk bug)

---

## Executive Summary

The 401 authentication error that occurred in the moai-adk project was caused by **local configuration conflicts**, not a bug in the moai-adk framework. The issue arose from a combination of:
1. A locally-added GLM proxy configuration
2. An invalid placeholder API key in the shell environment
3. Claude Code's authentication hierarchy prioritizing these over your subscription

**Key Finding**: This was entirely a local configuration issue. The moai-adk repository itself does not contain any authentication configurations that would cause this error.

---

## What is MoAI-ADK?

[MoAI-ADK (Agentic Development Kit)](https://github.com/modu-ai/moai-adk/) is an open-source framework that provides:
- **SPEC-First Development**: Specification-driven approach
- **Test-Driven Development**: Built-in TDD methodology
- **AI Agent Orchestration**: "Mr. Alfred" super agent coordinating 26 specialized agents
- **5-Tier Architecture**: Organized agent hierarchy for systematic development

The framework itself does NOT include any Claude authentication configurations or API keys.

---

## The GLM Proxy Configuration Origin

### Evidence It Was Added Locally

1. **Custom Setup Script Found**:
   ```
   /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.moai/scripts/setup-glm.py
   ```
   This script was created locally to configure GLM proxy authentication.

2. **Local `.moai/` Directory**:
   - Contains customizations not present in the upstream repository
   - Includes GLM configuration scripts and settings
   - Multiple backup files showing iterative configuration attempts

3. **GLM Configuration Details**:
   ```json
   {
     "env": {
       "ANTHROPIC_AUTH_TOKEN": "c498ad03a310455b859c827fc795d633.vkDwIOdY9f7rLZGb",
       "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
       "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4.5-air",
       "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-4.6",
       "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-4.6"
     }
   }
   ```
   **GLM (智谱清言)** is a Chinese AI service providing Claude-compatible API endpoints.

---

## The 401 Error Timeline

### Phase 1: Initial Configuration
1. **moai-adk cloned** from GitHub (clean state)
2. **GLM proxy added locally** via custom scripts
3. **Configuration saved** in `.claude/settings.local.json`

### Phase 2: Environment Pollution
1. **Shell configuration**: `~/.zshrc` line 301 contained:
   ```bash
   export ANTHROPIC_API_KEY="YOUR_ACTUAL_API_KEY_HERE"
   ```
   This was a placeholder value, not a real API key.

2. **Environment inheritance**: Terminal sessions inherited this invalid key

### Phase 3: Authentication Conflicts
1. **Claude Code launched** in moai-adk directory
2. **Multiple auth methods competed**:
   - Environment variable (invalid API key) - HIGHEST PRIORITY
   - Local GLM proxy configuration - MEDIUM PRIORITY
   - Claude subscription - LOWEST PRIORITY (never reached)
3. **Result**: 401 "Invalid bearer token" error

---

## Authentication Hierarchy Explanation

Claude Code follows this strict priority order:

```
┌─────────────────────────────────────────────────────┐
│ Priority 1 (HIGHEST): Environment Variables         │
│ └── ANTHROPIC_API_KEY="YOUR_ACTUAL_API_KEY_HERE"   │ ← Invalid!
│                                                      │
│ Priority 2: Project-Level Settings                  │
│ └── .claude/settings.local.json                     │ ← GLM proxy
│     └── ANTHROPIC_AUTH_TOKEN (GLM token)           │
│                                                      │
│ Priority 3: Global Settings                         │
│ └── ~/.claude/settings.json                         │
│                                                      │
│ Priority 4 (LOWEST): Subscription Authentication    │
│ └── Claude Pro/Max OAuth (from /login)             │ ← Never reached!
└─────────────────────────────────────────────────────┘
```

### Why This Caused Problems
- The invalid API key at Priority 1 overrode everything
- When that was removed, GLM proxy at Priority 2 took over
- Your valid subscription auth at Priority 4 was never used

---

## Why /login Worked Elsewhere But Not in moai-adk

### Other Folders
- ✅ No `ANTHROPIC_API_KEY` in environment (after unsetting)
- ✅ No project-level `settings.local.json`
- ✅ Subscription authentication used successfully

### moai-adk Folder
- ❌ Had project-level `settings.local.json` with GLM config
- ❌ GLM proxy configuration overrode subscription auth
- ❌ Request format `req_011...` showed it was hitting Anthropic's API with invalid credentials

---

## Root Cause Analysis

### Primary Cause: LOCAL CONFIGURATION
- **Not a moai-adk bug**: The repository doesn't include authentication configs
- **Local customization**: GLM proxy was added for specific use case
- **Configuration conflict**: Multiple authentication methods competing

### Contributing Factors
1. **Invalid placeholder API key** in shell environment
2. **Project-level settings** overriding global authentication
3. **Authentication hierarchy** not well understood
4. **Multiple backup attempts** creating confusion

---

## The Fix Applied

### Step 1: Removed GLM Configuration
```bash
mv .claude/settings.local.json .claude/settings.local.json.glm-backup
```

### Step 2: Created Clean Settings
Kept only permissions, removed all authentication tokens:
```json
{
  "permissions": {
    "allow": [
      // ... permissions list ...
    ]
  }
}
```

### Step 3: Cleared Environment
```bash
unset ANTHROPIC_API_KEY
```

### Result
✅ Claude Code now uses subscription authentication
✅ No more 401 errors
✅ moai-adk behaves like other folders

---

## Lessons Learned

1. **Project-level settings override global settings** - Be careful with local configurations
2. **Environment variables have highest priority** - Check for stray API keys
3. **Authentication methods don't mix** - GLM proxy and Claude subscription are incompatible
4. **Placeholder values are dangerous** - Never leave "YOUR_KEY_HERE" in configs
5. **Local customizations need documentation** - Track what's added vs upstream

---

## Prevention Strategies

### Best Practices
1. **Document local customizations**: Keep a `LOCAL_CHANGES.md` file
2. **Use environment-specific configs**: Separate dev/prod authentication
3. **Avoid placeholder values**: Remove or comment out template configs
4. **Understand authentication hierarchy**: Know what overrides what
5. **Regular cleanup**: Remove old backup files and unused configs

### Configuration Management
```bash
# Check for authentication conflicts
env | grep ANTHROPIC
find . -name "settings*.json" -path "*/.claude/*"

# Document local changes
git status --ignored
git diff HEAD...origin/main
```

---

## Technical Deep Dive

### Request ID Analysis
- Format: `req_011CVbZcsZ4EpZeyAC26az9B`
- Pattern: Standard Anthropic API request ID
- Indicates: Direct API call, not proxy routing
- Problem: Using invalid credentials for direct API

### GLM Proxy Details
- **Service**: 智谱清言 (Zhipu Qingyan)
- **Endpoint**: `https://api.z.ai/api/anthropic`
- **Models**: Maps Claude models to GLM equivalents
- **Use Case**: Access Claude-like AI in regions with restrictions

### Authentication Token Formats
- **Anthropic API Key**: `sk-ant-api03-...`
- **GLM Token**: `[hash].[random]` format
- **Claude Subscription**: OAuth tokens (not visible to user)

---

## Recommendations

### For This Project
1. **Keep current configuration**: Subscription auth now working
2. **Document if GLM needed**: Create setup guide if proxy required
3. **Version control**: Add `.claude/` to `.gitignore`

### For Future Projects
1. **Check authentication first**: `env | grep ANTHROPIC`
2. **Start with global settings**: Avoid project-level configs unless necessary
3. **Test authentication**: Verify before extensive configuration
4. **Document everything**: Track all local modifications

### For Team Collaboration
1. **Share authentication strategy**: Document which auth method to use
2. **Use environment variables wisely**: `.env` files with proper examples
3. **Create setup scripts**: Automate configuration for team members

---

## Conclusion

The 401 authentication error was caused by **local configuration conflicts**, not a bug in the moai-adk framework. The issue has been completely resolved by:
1. Removing the GLM proxy configuration
2. Clearing invalid environment variables
3. Allowing Claude subscription authentication to work

**Status**: ✅ FULLY RESOLVED
**Root Cause**: Local configuration issue
**moai-adk Status**: Working correctly, no bugs found
**Future Risk**: Low (with proper configuration management)

---

## Appendix: File Locations

### Configuration Files
- **Removed**: `.claude/settings.local.json` (GLM config)
- **Backup**: `.claude/settings.local.json.glm-backup-20251129-135817`
- **Current**: `.claude/settings.local.json` (permissions only)

### Shell Configuration
- **File**: `~/.zshrc`
- **Line 15**: `unset ANTHROPIC_API_KEY` (added)
- **Line 302**: `# export ANTHROPIC_API_KEY=...` (commented out)

### Custom Scripts
- **GLM Setup**: `.moai/scripts/setup-glm.py` (local addition)
- **Configuration**: `.moai/config/` (local customizations)

---

*This document serves as a complete record of the 401 authentication error investigation and resolution.*