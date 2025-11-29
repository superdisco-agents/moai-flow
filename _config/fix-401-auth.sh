#!/bin/bash

# Fix 401 Authentication Error Script
# Created: 2025-11-29
# Purpose: Help user set up Anthropic API key to fix authentication errors

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}${BOLD}    Fix 401 Authentication Error - Anthropic API Setup${NC}"
echo -e "${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Check current API key status
echo -e "${YELLOW}Checking current API key configuration...${NC}"
CURRENT_KEY="${ANTHROPIC_API_KEY:-}"

if [[ -n "$CURRENT_KEY" ]] && [[ "$CURRENT_KEY" != "YOUR_ACTUAL_API_KEY_HERE" ]]; then
    # Mask the key for display
    MASKED_KEY="${CURRENT_KEY:0:10}...${CURRENT_KEY: -4}"
    echo -e "${GREEN}✓${NC} Found existing API key: ${MASKED_KEY}"
    echo
    read -p "Do you want to keep this key? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        API_KEY="$CURRENT_KEY"
    else
        API_KEY=""
    fi
else
    echo -e "${RED}✗${NC} No valid API key found (placeholder or empty)"
    API_KEY=""
fi

# Prompt for API key if needed
if [[ -z "$API_KEY" ]]; then
    echo
    echo -e "${YELLOW}${BOLD}Get your API key from:${NC} https://console.anthropic.com/settings/keys"
    echo -e "${YELLOW}The key should start with:${NC} sk-ant-api03-"
    echo
    read -p "Enter your Anthropic API key: " API_KEY

    # Basic validation
    if [[ ! "$API_KEY" =~ ^sk-ant- ]]; then
        echo -e "${RED}✗ Error: API key should start with 'sk-ant-'${NC}"
        echo "Please get a valid key from https://console.anthropic.com"
        exit 1
    fi

    if [[ ${#API_KEY} -lt 95 ]]; then
        echo -e "${RED}✗ Error: API key seems too short${NC}"
        echo "Valid keys are typically 95+ characters long"
        exit 1
    fi
fi

# Test the API key
echo
echo -e "${YELLOW}Testing API connection...${NC}"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    https://api.anthropic.com/v1/messages \
    -H "x-api-key: $API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":10,"messages":[{"role":"user","content":"test"}]}' 2>/dev/null || echo "000")

if [[ "$RESPONSE" == "200" ]]; then
    echo -e "${GREEN}✓ API key is valid and working!${NC}"
elif [[ "$RESPONSE" == "401" ]]; then
    echo -e "${RED}✗ API key is invalid (401 Unauthorized)${NC}"
    exit 1
elif [[ "$RESPONSE" == "000" ]]; then
    echo -e "${RED}✗ Network error - could not reach API${NC}"
    exit 1
else
    echo -e "${YELLOW}⚠ Unexpected response code: $RESPONSE${NC}"
    echo "The key might still work. Continuing..."
fi

# Update .env file
echo
echo -e "${YELLOW}Updating configuration files...${NC}"

# Update project .env
ENV_FILE="/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/.env"
cat > "$ENV_FILE" << EOF
# Anthropic API Configuration
# Updated: $(date)
ANTHROPIC_API_KEY=$API_KEY
EOF
chmod 600 "$ENV_FILE"
echo -e "${GREEN}✓${NC} Updated $ENV_FILE"

# Update .zshrc if needed
if grep -q "YOUR_ACTUAL_API_KEY_HERE" ~/.zshrc 2>/dev/null; then
    echo -e "${YELLOW}Updating .zshrc...${NC}"
    cp ~/.zshrc ~/.zshrc.backup-$(date +%Y%m%d-%H%M%S)
    sed -i '' "s/export ANTHROPIC_API_KEY=\"YOUR_ACTUAL_API_KEY_HERE\"/export ANTHROPIC_API_KEY=\"$API_KEY\"/" ~/.zshrc
    echo -e "${GREEN}✓${NC} Updated ~/.zshrc (backup created)"
fi

# Export to current session
export ANTHROPIC_API_KEY="$API_KEY"

# Final test with claude-flow
echo
echo -e "${YELLOW}Testing claude-flow swarm initialization...${NC}"
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk

if npx claude-flow@alpha swarm status 2>&1 | grep -q "swarm"; then
    echo -e "${GREEN}✓ Claude-flow is working!${NC}"
else
    echo -e "${YELLOW}⚠ Claude-flow test inconclusive. Try manually:${NC}"
    echo "  npx claude-flow@alpha swarm init --topology mesh --max-agents 3"
fi

echo
echo -e "${GREEN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}${BOLD}                    ✅ Setup Complete!${NC}"
echo -e "${GREEN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo -e "${BLUE}Your API key has been configured in:${NC}"
echo "  • $ENV_FILE"
echo "  • ~/.zshrc (if it had placeholder)"
echo "  • Current shell session"
echo
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Restart Claude Code or reload shell: source ~/.zshrc"
echo "  2. Test swarm: npx claude-flow@alpha swarm init --topology mesh"
echo "  3. The 401 errors should now be resolved!"
echo