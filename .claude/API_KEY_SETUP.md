# API Key Setup Instructions

## 🚨 ACTION REQUIRED: Set Your Anthropic API Key

The 401 "Invalid bearer token" error occurs because no valid Anthropic API key is configured.

## Quick Setup (2 minutes)

### Step 1: Get Your API Key

1. Visit: https://console.anthropic.com
2. Sign in or create an account
3. Go to **Settings** → **API Keys**
4. Click **"Create Key"**
5. Name it: "Claude Code - MoAI-ADK"
6. Copy the key (starts with `sk-ant-api03-`)

### Step 2: Set The API Key

Choose **ONE** of these methods:

#### Option A: Run the Fix Script (Recommended)
```bash
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk
./fix-401-auth.sh
```
Enter your API key when prompted. The script will handle everything.

#### Option B: Manual Setup
1. Edit `.env` file:
   ```bash
   cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk
   nano .env
   ```
   Replace `YOUR_ACTUAL_API_KEY_HERE` with your actual key.

2. Update shell environment:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-api03-your-actual-key"
   ```

3. Make it permanent in `.zshrc`:
   ```bash
   echo 'export ANTHROPIC_API_KEY="sk-ant-api03-your-actual-key"' >> ~/.zshrc
   source ~/.zshrc
   ```

### Step 3: Verify It Works

```bash
# Test API connection
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

If successful, you'll see a JSON response with Claude's reply.

## Configuration Files Updated

✅ **`.claude/settings.local.json`** - Now uses environment variable reference
✅ **`.env`** - Created with placeholder for API key
✅ **Backups created** - Original files saved with timestamp

## What Was Fixed

### Before (Invalid GLM Token)
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

### After (Proper Anthropic Configuration)
```json
{
  "env": {
    "ANTHROPIC_API_KEY": "${env:ANTHROPIC_API_KEY}"
  }
}
```

## Troubleshooting

### Still Getting 401 Errors?

1. **Verify key format**: Must start with `sk-ant-api03-`
2. **Check environment**: Run `echo $ANTHROPIC_API_KEY`
3. **Restart Claude Code**: Close and reopen after setting key
4. **Test directly**: Use the curl command above

### Common Issues

- **"Invalid API key"** - Key doesn't start with `sk-ant-`
- **"Unauthorized"** - Key may be revoked or incorrect
- **"Rate limited"** - Too many requests, wait a moment

## Security Notes

- ✅ API key is stored in `.env` (gitignored)
- ✅ Settings reference environment variable, not hardcoded
- ✅ Original GLM token has been removed
- ⚠️ Never commit API keys to git

## Next Steps

After setting your API key:

1. Test claude-flow swarm:
   ```bash
   npx claude-flow@alpha swarm init --topology mesh --max-agents 3
   ```

2. Verify MCP tools work:
   - Try spawning agents
   - Test task orchestration
   - Check swarm status

---

**Need Help?** The fix script at `./fix-401-auth.sh` automates this entire process.