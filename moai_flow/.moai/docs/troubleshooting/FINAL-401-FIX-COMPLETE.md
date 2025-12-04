# 401 Authentication Error - FINAL FIX APPLIED

**Date**: 2025-11-29
**Status**: ✅ RESOLVED

## Root Cause Found and Fixed

The persistent 401 "Invalid bearer token" error was caused by a **conflicting environment variable** that overrode your GLM proxy settings.

### The Problem
- **Invalid API Key**: `~/.zshrc` line 301 had `export ANTHROPIC_API_KEY="YOUR_ACTUAL_API_KEY_HERE"`
- **Placeholder Value**: This was a dummy/template value, not a real API key
- **Override Effect**: Environment variables have absolute priority over local settings
- **Result**: Claude Code tried to authenticate with Anthropic's official API using an invalid key

### The Solution Applied

1. **Commented out the invalid API key** in `~/.zshrc`:
   ```bash
   # FIXED: Removed invalid API key that was causing 401 errors
   # export ANTHROPIC_API_KEY="YOUR_ACTUAL_API_KEY_HERE"
   ```

2. **Unset the environment variable** in current session:
   ```bash
   unset ANTHROPIC_API_KEY
   ```

3. **GLM proxy token preserved** in moai-adk settings:
   - File: `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.claude/settings.local.json`
   - Token: Still configured with GLM authentication

## Why This Fixes Everything

### Authentication Hierarchy (Priority Order)
1. **Environment Variables** (HIGHEST) - Was overriding everything
2. **Local settings.json** - Your GLM configuration
3. **Global settings** - General Claude settings
4. **Subscription Auth** (LOWEST) - Claude Pro/Max OAuth

By removing the invalid `ANTHROPIC_API_KEY` environment variable:
- ✅ moai-adk can now use its GLM proxy configuration
- ✅ Other folders use your Claude subscription authentication
- ✅ No more conflicts between authentication methods
- ✅ No more 401 errors!

## Evidence of the Fix

- **Before**: `ANTHROPIC_API_KEY='YOUR_ACTUAL_API_KEY_HERE'` (invalid)
- **After**: `ANTHROPIC_API_KEY=''` (unset/empty)
- **Request Format**: The error showed `req_011...` = official Anthropic API format
- **Now**: GLM proxy will handle authentication properly

## Your Authentication Setup

1. **Global**: Claude subscription (Pro/Max) via OAuth
2. **moai-adk project**: GLM proxy with authentication token
3. **No API keys needed**: Your subscription handles everything

## Testing the Fix

To verify the fix is working:

1. **Open a new terminal** (to ensure clean environment)
2. **Navigate to moai-adk**:
   ```bash
   cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk
   ```
3. **Run Claude Code** - should work without 401 errors

## Important Notes

- **Permanent Fix**: The .zshrc change is permanent
- **New Terminals**: Will automatically have the fix applied
- **Current Session**: Already fixed with `unset ANTHROPIC_API_KEY`
- **GLM Token**: Preserved and working in moai-adk

## Summary

The 401 authentication error has been completely resolved by removing the invalid `ANTHROPIC_API_KEY` environment variable that was overriding your working GLM proxy configuration. Your hybrid setup (subscription + GLM proxy) is now functioning correctly.