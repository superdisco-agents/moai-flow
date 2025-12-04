# CRITICAL: Final Fix for 401 Authentication Error

**Date**: 2025-11-29
**Status**: ⚠️ ACTION REQUIRED

## The Real Problem

The invalid `ANTHROPIC_API_KEY=YOUR_ACTUAL_API_KEY_HERE` is being inherited from your **parent terminal session** (Ghostty or iTerm). This happens BEFORE your shell configuration runs, which is why our fixes haven't worked yet.

## IMMEDIATE FIX (Choose One)

### Option 1: Restart All Terminals (Recommended)
1. **Close ALL terminal windows** (Ghostty, iTerm, Terminal.app, etc.)
2. **Completely quit** the terminal application (Cmd+Q)
3. **Reopen** your terminal application
4. Test in moai-adk:
   ```bash
   cd ~/Documents/claydev-local/agent-os-v2/moai-adk
   claude
   ```

### Option 2: Manual Fix in Current Terminal
1. In your current terminal, run:
   ```bash
   unset ANTHROPIC_API_KEY
   ```
2. Verify it's gone:
   ```bash
   printenv | grep ANTHROPIC_API_KEY
   # Should return nothing
   ```
3. Test Claude Code:
   ```bash
   cd ~/Documents/claydev-local/agent-os-v2/moai-adk
   claude
   ```

## What We've Already Fixed

✅ **Added to .zshrc (line 15)**: `unset ANTHROPIC_API_KEY`
✅ **Commented out invalid key** (line 302 in .zshrc)
✅ **Created cy4 wrapper** to unset the key
✅ **GLM configuration** is correct in settings.local.json

## Why This Will Work Now

1. When you restart terminals, they won't have the invalid API key
2. Your .zshrc will prevent it from being set again
3. Claude Code will use your GLM proxy configuration
4. No more 401 errors!

## Verification Steps

After restarting terminals:

```bash
# 1. Check environment is clean
printenv | grep ANTHROPIC_API_KEY
# Should show nothing

# 2. Check GLM token is available
cd ~/Documents/claydev-local/agent-os-v2/moai-adk
cat .claude/settings.local.json | grep AUTH_TOKEN
# Should show your GLM token

# 3. Test Claude Code
claude
# Should work without 401 errors
```

## Important Note

The issue is that your terminal emulator (Ghostty) is passing the invalid API key to ALL child processes. This overrides any shell configuration. You MUST restart your terminals or manually unset the variable.

## Summary

**ACTION REQUIRED**: Close and restart ALL your terminal windows to clear the invalid API key from memory.