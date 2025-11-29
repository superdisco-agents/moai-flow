#!/bin/bash
# Figma MCP Server - Project Installation Script
# Location: moai-adk/_config/mcp-figma/install.sh

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🎨 Installing Figma MCP Server for moai-adk project..."
echo ""

# Get project root (parent of _config)
PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
echo "📁 Project root: $PROJECT_ROOT"
echo ""

# Create .claude directory if it doesn't exist
if [ ! -d "$PROJECT_ROOT/.claude" ]; then
    echo "📂 Creating .claude directory..."
    mkdir -p "$PROJECT_ROOT/.claude"
    echo -e "${GREEN}✓${NC} Created $PROJECT_ROOT/.claude"
else
    echo -e "${GREEN}✓${NC} .claude directory already exists"
fi

# Check if settings.json already exists
if [ -f "$PROJECT_ROOT/.claude/settings.json" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Warning: $PROJECT_ROOT/.claude/settings.json already exists${NC}"
    echo ""
    echo "Choose an option:"
    echo "1) Backup existing and install fresh (recommended)"
    echo "2) Merge Figma MCP into existing config (manual)"
    echo "3) Skip installation"
    read -p "Enter choice (1-3): " choice

    case $choice in
        1)
            BACKUP_FILE="$PROJECT_ROOT/.claude/settings.json.backup-$(date +%Y%m%d-%H%M%S)"
            echo "📦 Backing up to: $BACKUP_FILE"
            cp "$PROJECT_ROOT/.claude/settings.json" "$BACKUP_FILE"
            echo -e "${GREEN}✓${NC} Backup created"

            echo "📝 Installing fresh Figma MCP config..."
            cp "$(dirname "$0")/settings.json" "$PROJECT_ROOT/.claude/settings.json"
            echo -e "${GREEN}✓${NC} Installed $PROJECT_ROOT/.claude/settings.json"
            ;;
        2)
            echo ""
            echo "Manual merge instructions:"
            echo "1. Open: $PROJECT_ROOT/.claude/settings.json"
            echo "2. Add this to mcpServers section:"
            echo ""
            cat "$(dirname "$0")/settings.json"
            echo ""
            echo "3. Save the file"
            echo ""
            read -p "Press Enter when done..."
            ;;
        3)
            echo "Skipping installation"
            exit 0
            ;;
        *)
            echo "Invalid choice. Exiting."
            exit 1
            ;;
    esac
else
    echo "📝 Installing Figma MCP configuration..."
    cp "$(dirname "$0")/settings.json" "$PROJECT_ROOT/.claude/settings.json"
    echo -e "${GREEN}✓${NC} Installed $PROJECT_ROOT/.claude/settings.json"
fi

echo ""
echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1️⃣  Enable Figma MCP Server:"
echo "   - Open Figma desktop app"
echo "   - Open a Design file"
echo "   - Press Shift + D (Dev Mode)"
echo "   - Click 'Enable desktop MCP server'"
echo ""
echo "2️⃣  Test the connection:"
echo "   curl -v http://127.0.0.1:3845/mcp"
echo ""
echo "3️⃣  Start Claude Code in project directory:"
echo "   cd $PROJECT_ROOT"
echo "   claude"
echo ""
echo "4️⃣  Test in Claude Code:"
echo "   \"Using Figma MCP, show me available tools\""
echo ""
echo "📚 Documentation:"
echo "   Setup Guide: $(dirname "$0")/FIGMA_MCP_SETUP_GUIDE.md"
echo "   README:      $(dirname "$0")/README.md"
echo ""
