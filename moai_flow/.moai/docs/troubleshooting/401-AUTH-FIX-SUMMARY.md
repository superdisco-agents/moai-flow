# 401 Authentication Error - Fix Summary

**Date**: 2025-11-29 12:30 KST
**Status**: ✅ Configuration Updated - **Awaiting API Key**

---

## What Was Fixed

### 1. ✅ Removed Invalid GLM Configuration

**Before (Invalid):**
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

**After (Correct):**
```json
{
  "env": {
    "ANTHROPIC_API_KEY": "${env:ANTHROPIC_API_KEY}"
  }
}
```

### 2. ✅ Created Environment Configuration

- Created `.env` file with placeholder for API key
- Settings now reference environment variable instead of hardcoded token
- Removed all GLM model references

### 3. ✅ Created Fix Script

- Location: `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/fix-401-auth.sh`
- Automates API key setup and validation
- Tests connection before saving

---

## 🚨 ACTION REQUIRED: Set Your API Key

You need to obtain and set an Anthropic API key to resolve the 401 error.

### Option 1: Use Fix Script (Easiest)
```bash
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk
./fix-401-auth.sh
```

### Option 2: Manual Setup

1. **Get API Key** from https://console.anthropic.com/settings/keys
2. **Update .env file:**
   ```bash
   cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk
   nano .env
   # Replace YOUR_ACTUAL_API_KEY_HERE with your key
   ```
3. **Update .zshrc line 301:**
   ```bash
   nano ~/.zshrc
   # Change line 301 from:
   export ANTHROPIC_API_KEY="YOUR_ACTUAL_API_KEY_HERE"
   # To:
   export ANTHROPIC_API_KEY="sk-ant-api03-your-actual-key"
   ```
4. **Reload shell:**
   ```bash
   source ~/.zshrc
   ```

---

## Files Modified

1. ✅ `.claude/settings.local.json` - Removed GLM token, uses env variable
2. ✅ `.env` - Created with placeholder
3. ✅ `fix-401-auth.sh` - Created setup script
4. ⏳ `.zshrc` line 301 - Needs your API key

## Backups Created

- `settings.local.json.backup-401-fix-20251129-122922`
- `settings.json.backup-401-fix-20251129-122922`

---

## Previous Issues Also Fixed

1. ✅ SpecStory removed completely (Homebrew, aliases, 400+ folders archived)
2. ✅ SuperMemory removed completely (caches, logs, source code)
3. ✅ Invalid proxy URL removed (`https://api.z.ai/api/anthropic`)
4. ✅ Now configured for official Anthropic API

---

Once you set your API key, all 401 errors should be resolved!