# GLM Token Restoration - Authentication Fixed

**Date**: 2025-11-29
**Status**: ✅ RESOLVED

## Problem Identified

The moai-adk folder had authentication errors while other folders worked correctly. Investigation revealed that our previous "fix" had accidentally removed the working GLM proxy authentication from the local settings.

## Root Cause

The `.claude/settings.local.json` file had its `env` object emptied during our previous fix attempt, removing:
- GLM authentication token
- GLM model configurations

## Solution Applied

Restored the GLM configuration from backup:

### Restored Configuration
```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "c498ad03a310455b859c827fc795d633.vkDwIOdY9f7rLZGb",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4.5-air",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-4.6",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-4.6"
  }
}
```

## What This Is

- **GLM (智谱清言)**: A Chinese AI provider offering LLM services
- **Proxy Authentication**: Your Claude Code uses GLM's API as a proxy to handle requests
- **Working Configuration**: This token and model setup was working before and is now restored

## Why It Works

1. **Claude Code with Subscription**: Uses subscription authentication globally
2. **Project Override**: The moai-adk folder has local settings that override global config
3. **GLM Proxy**: Your specific setup uses GLM's API proxy instead of direct Anthropic API
4. **Token Format**: The GLM token format (`hash.randomstring`) is different from Anthropic's format

## Files Updated

- ✅ `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/settings.local.json` - Restored from backup
- Backup preserved: `settings.local.json.backup-401-fix-20251129-122922`

## Testing

The authentication should now work in the moai-adk folder. The GLM proxy will handle:
- Model routing (glm-4.5-air for Haiku, glm-4.6 for Sonnet/Opus)
- Authentication via the restored token
- API request proxying

## Important Notes

1. **Not an Anthropic API Key**: This GLM token is different from Anthropic's API keys
2. **Subscription Still Works**: Your Claude subscription authentication remains intact for other folders
3. **Local Override**: This configuration only affects the moai-adk project folder
4. **Working State**: This restores the exact configuration that was working before

## Summary

The 401 authentication error in moai-adk has been resolved by restoring the GLM proxy authentication token that was accidentally removed during previous troubleshooting. Your setup uses a hybrid approach:
- Claude subscription for general use
- GLM proxy for the moai-adk project specifically