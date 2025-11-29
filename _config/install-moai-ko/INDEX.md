# MoAI-ADK Installation Documentation Index

Quick navigation and overview of all installation documentation.

**Version**: 1.0.0
**Last Updated**: 2025-11-29
**Documentation Status**: Complete ✓

---

## Quick Navigation

### For New Users

1. **Start Here**: [README.md](#readmemd) - Complete installation guide
2. **Install**: Choose your [installation approach](#installation-approaches)
3. **Verify**: Check [verification steps](#verification)
4. **Troubleshoot**: See [troubleshooting guide](#troubleshooting)

### For Migration

1. **Migrating**: [MIGRATION-GUIDE.md](#migration-guidemd) - From existing setups
2. **Team Rollout**: [Team rollout plan](#team-rollout)
3. **Rollback**: [Rollback procedures](#rollback)

### For Korean Support

1. **Korean Setup**: [KOREAN-FONTS-GUIDE.md](#korean-fonts-guidemd) - Complete font guide
2. **D2Coding**: [Font installation](#d2coding-font)
3. **Terminals**: [Terminal configuration](#terminal-configuration)

---

## Documentation Files

### README.md

**Main installation guide** (700 lines)

**What's Inside**:
- Beyond-MCP pattern explanation
- 3 installation approaches (UV, Bash, Skills)
- Korean language support
- Quick start guide
- Examples and troubleshooting

**Best For**:
- New installations
- Understanding the system
- Quick reference

**Key Sections**:
1. [Overview](#readmemd-overview)
2. [Beyond-MCP Pattern](#readmemd-beyond-mcp)
3. [Installation Approaches](#readmemd-approaches)
4. [Korean Support](#readmemd-korean)
5. [Quick Start](#readmemd-quickstart)
6. [Examples](#readmemd-examples)

**Jump to**: [README.md](./README.md)

---

### MIGRATION-GUIDE.md

**Complete migration guide** (750 lines)

**What's Inside**:
- 4 migration paths with step-by-step instructions
- Korean font migration procedures
- Team rollout plans (small, medium, large teams)
- Rollback procedures
- Comprehensive troubleshooting

**Best For**:
- Migrating from existing setups
- Team deployments
- Production migrations

**Migration Paths**:
1. [Path 1: UV CLI Migration](#migration-path-1) (Recommended)
2. [Path 2: Bash Installation](#migration-path-2)
3. [Path 3: Claude Skill](#migration-path-3)
4. [Path 4: Gradual Migration](#migration-path-4) (Existing projects)

**Key Sections**:
1. [Migration Paths](#migration-guidemd-paths)
2. [Korean Font Migration](#migration-guidemd-korean)
3. [Team Rollout](#migration-guidemd-team)
4. [Rollback Procedures](#migration-guidemd-rollback)
5. [Troubleshooting](#migration-guidemd-troubleshooting)
6. [Verification](#migration-guidemd-verification)

**Jump to**: [MIGRATION-GUIDE.md](./MIGRATION-GUIDE.md)

---

### KOREAN-FONTS-GUIDE.md

**Korean font configuration guide** (600 lines)

**What's Inside**:
- Complete D2Coding font installation
- Terminal-specific configurations (Ghostty, iTerm2, Warp)
- Troubleshooting Korean rendering
- Alternative font options
- CJK character support
- Comprehensive testing procedures

**Best For**:
- Setting up Korean language support
- Fixing Korean rendering issues
- Terminal configuration

**Covered Terminals**:
- Ghostty (Recommended) ⭐
- iTerm2
- Warp
- Terminal.app
- Alacritty
- Kitty

**Key Sections**:
1. [Why Korean Fonts Matter](#korean-fonts-guidemd-why)
2. [D2Coding Font](#korean-fonts-guidemd-d2coding)
3. [Installation Methods](#korean-fonts-guidemd-install)
4. [Ghostty Configuration](#korean-fonts-guidemd-ghostty)
5. [iTerm2 Configuration](#korean-fonts-guidemd-iterm2)
6. [Warp Configuration](#korean-fonts-guidemd-warp)
7. [Troubleshooting](#korean-fonts-guidemd-troubleshooting)
8. [Alternative Fonts](#korean-fonts-guidemd-alternatives)

**Jump to**: [KOREAN-FONTS-GUIDE.md](./KOREAN-FONTS-GUIDE.md)

---

### test-suite.sh

**Comprehensive test suite** (650 lines, 140+ tests)

**What's Inside**:
- 140+ individual tests across 8 categories
- Multiple output modes (standard, verbose, JSON)
- CI/CD ready with exit codes
- Color-coded output
- Korean-specific tests ⭐

**Test Categories**:
1. File Structure Tests (30 tests)
2. UV Script Tests (25 tests)
3. Bash App Tests (20 tests)
4. Skills/Commands Tests (15 tests)
5. Documentation Tests (20 tests)
6. Syntax Validation Tests (15 tests)
7. Integration Tests (10 tests)
8. **Korean Font Rendering Tests (8 tests)** ⭐

**Usage**:
```bash
# Standard output
./test-suite.sh

# Verbose output
./test-suite.sh --verbose

# JSON output (CI/CD)
./test-suite.sh --json

# Korean tests only
./test-suite.sh --korean

# Help
./test-suite.sh --help
```

**Jump to**: [test-suite.sh](./test-suite.sh)

---

## Installation Approaches

### Approach 1: UV CLI Scripts

**Command**:
```bash
uv run install-moai-adk.py --korean-fonts --yes
```

**Time**: 10-15 minutes

**Best For**:
- Automated deployments
- CI/CD pipelines
- Developers comfortable with CLI
- Clean installations

**Documentation**:
- [README.md - UV CLI Section](./README.md#approach-1-uv-cli-scripts)
- [MIGRATION-GUIDE.md - Path 1](./MIGRATION-GUIDE.md#path-1-uv-cli-migration-recommended)

---

### Approach 2: Bash Apps

**Command**:
```bash
./install-moai-adk.sh --interactive
```

**Time**: 15-20 minutes

**Best For**:
- Interactive setup
- Custom configuration
- Learning the process
- Step-by-step guidance

**Documentation**:
- [README.md - Bash App Section](./README.md#approach-2-bash-apps)
- [MIGRATION-GUIDE.md - Path 2](./MIGRATION-GUIDE.md#path-2-bash-installation-migration)

---

### Approach 3: Claude Skills

**Command**:
```bash
claude code /moai-adk-installer
```

**Time**: 20-30 minutes

**Best For**:
- AI-assisted installation
- Beginners
- Progressive learning
- Contextual help

**Documentation**:
- [README.md - Claude Skill Section](./README.md#approach-3-claude-skills)
- [MIGRATION-GUIDE.md - Path 3](./MIGRATION-GUIDE.md#path-3-claude-skill-migration)

---

## Feature Comparison

### Installation Features

| Feature | UV CLI | Bash App | Claude Skill |
|---------|--------|----------|--------------|
| **Speed** | ⚡⚡⚡ | ⚡⚡ | ⚡ |
| **Automation** | ✅ Full | ⚠️ Partial | ❌ No |
| **Customization** | ⚠️ Flags | ✅ Interactive | ✅ Conversational |
| **Learning Curve** | Steep | Moderate | Gentle |
| **CI/CD Ready** | ✅ Yes | ⚠️ Limited | ❌ No |
| **Offline** | ⚠️ Partial | ✅ Yes | ❌ No |
| **Korean Fonts** | ✅ Auto | ✅ Auto | ✅ Guided |

### Korean Support Features

| Feature | UV CLI | Bash App | Claude Skill |
|---------|--------|----------|--------------|
| **Font Install** | ✅ Auto | ✅ Auto | ✅ Auto |
| **Terminal Config** | ✅ Auto | ✅ Interactive | ✅ Guided |
| **Encoding** | ✅ Auto | ✅ Auto | ✅ Auto |
| **Testing** | ✅ Script | ✅ Script | ✅ AI-guided |
| **Troubleshooting** | 📖 Docs | 🔄 Interactive | 🤖 AI-assisted |

---

## Korean Font Support

### Why Korean Fonts Matter

**Without proper fonts**:
```
안녕하세요 → □□□□□
```

**With D2Coding**:
```
안녕하세요 → 안녕하세요 ✓
```

### D2Coding Font

**Features**:
- ✅ Monospace for coding
- ✅ Clear Hangul rendering
- ✅ Programming ligatures
- ✅ Free and open-source
- ✅ Terminal optimized

**Installation**:
```bash
# Automatic (via installer)
uv run install-moai-adk.py --korean-fonts

# Manual
curl -L -o ~/Library/Fonts/D2Coding.ttc \
  https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.ttc
fc-cache -fv
```

**Documentation**: [KOREAN-FONTS-GUIDE.md](./KOREAN-FONTS-GUIDE.md)

---

## Terminal Configuration

### Recommended: Ghostty

**Why Ghostty**:
- ⚡ Excellent Korean rendering
- ⚡ GPU-accelerated
- ⚡ Modern configuration
- ⚡ Fast and lightweight

**Configuration**:
```toml
# ~/.config/ghostty/config
font-family = "D2Coding"
font-size = 14
grapheme-width-method = legacy
```

**Full Guide**: [KOREAN-FONTS-GUIDE.md - Ghostty](./KOREAN-FONTS-GUIDE.md#ghostty-configuration)

### Also Supported

- **iTerm2**: [Configuration Guide](./KOREAN-FONTS-GUIDE.md#iterm2-configuration)
- **Warp**: [Configuration Guide](./KOREAN-FONTS-GUIDE.md#warp-configuration)
- **Alacritty**: Works with D2Coding font
- **Kitty**: Works with D2Coding font

---

## Quick Start

### 5-Minute Installation

```bash
# 1. Install UV (1 min)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Navigate to installer
cd /path/to/moai-adk/_config/install-moai-ko

# 3. Run installer (10-15 min)
uv run install-moai-adk.py --korean-fonts --yes

# 4. Verify (1 min)
./verify-installation.sh

# 5. Test Korean
echo "안녕하세요 MoAI-ADK"
```

**Full Guide**: [README.md - Quick Start](./README.md#quick-start)

---

## Testing

### Run Test Suite

```bash
# Standard tests
./test-suite.sh

# Verbose output
./test-suite.sh --verbose

# JSON output for CI/CD
./test-suite.sh --json

# Korean tests only
./test-suite.sh --korean
```

### Test Categories

1. **File Structure** (30 tests) - Verify all files exist
2. **UV Scripts** (25 tests) - UV installation and environment
3. **Bash Apps** (20 tests) - Shell scripts and apps
4. **Skills/Commands** (15 tests) - Claude integration
5. **Documentation** (20 tests) - Docs completeness
6. **Syntax** (15 tests) - Code validation
7. **Integration** (10 tests) - End-to-end workflows
8. **Korean Rendering** (8 tests) ⭐ - Font and encoding

**Documentation**: [test-suite.sh](./test-suite.sh)

---

## Verification

### Post-Installation Checklist

After installation, verify:

- [ ] UV installed (0.4.0+)
- [ ] Python 3.11+ configured
- [ ] D2Coding font installed
- [ ] Terminal configured
- [ ] Korean text renders correctly
- [ ] MCP servers registered
- [ ] Skills installed
- [ ] All tests pass

### Verification Commands

```bash
# UV version
uv --version

# Python version
python --version

# Korean fonts
fc-list | grep D2Coding

# Korean rendering
echo "한글 테스트: ✓"

# Test suite
./test-suite.sh
```

**Full Guide**: [MIGRATION-GUIDE.md - Verification](./MIGRATION-GUIDE.md#verification)

---

## Troubleshooting

### Common Issues

#### Korean Characters Show as Boxes

**Problem**: 안녕하세요 → □□□□□

**Solution**:
1. Install D2Coding font
2. Configure terminal
3. Restart terminal

**Guide**: [KOREAN-FONTS-GUIDE.md - Troubleshooting](./KOREAN-FONTS-GUIDE.md#troubleshooting-korean-rendering)

#### UV Installation Fails

**Problem**: `curl: (7) Failed to connect`

**Solution**:
```bash
# Alternative: Homebrew
brew install uv

# Or manual download
# See: MIGRATION-GUIDE.md - Troubleshooting
```

#### MCP Servers Not Connecting

**Problem**: `MCP server failed to start`

**Solution**:
```bash
# Restart server
claude mcp restart [server-name]

# Check logs
tail -f ~/.claude/logs/mcp-*.log
```

**Full Troubleshooting**:
- [MIGRATION-GUIDE.md - Troubleshooting](./MIGRATION-GUIDE.md#troubleshooting)
- [KOREAN-FONTS-GUIDE.md - Troubleshooting](./KOREAN-FONTS-GUIDE.md#troubleshooting-korean-rendering)

---

## Team Rollout

### Small Teams (2-5 developers)

**Timeline**: 1-2 weeks

**Plan**:
1. Week 1: Admin pilot, team demo
2. Week 2: Team installation, parallel usage

**Guide**: [MIGRATION-GUIDE.md - Team Rollout](./MIGRATION-GUIDE.md#team-rollout-plan)

### Medium Teams (6-20 developers)

**Timeline**: 3-4 weeks

**Plan**:
1. Week 1: Pilot (20%)
2. Week 2: Pilot rollout (20%)
3. Week 3: Broad rollout (80%)
4. Week 4: Completion (100%)

### Large Teams (20+ developers)

**Timeline**: 6-8 weeks

**Plan**:
1. Weeks 1-2: Pilot phase
2. Weeks 3-4: Wave 1 (25%)
3. Weeks 5-6: Wave 2 (50%)
4. Weeks 7-8: Wave 3 (100%)

**Full Guide**: [MIGRATION-GUIDE.md - Team Rollout](./MIGRATION-GUIDE.md#team-rollout-plan)

---

## Rollback

### When to Rollback

Rollback if:
- Critical bugs affecting productivity
- Data loss or corruption
- Incompatibility with critical tools
- Team unable to adapt

### Rollback Procedure

```bash
# Emergency rollback
BACKUP_DIR=$(ls -td ~/moai-adk-backup/* | head -1)
cd "$BACKUP_DIR"
./restore.sh

# Restart terminal
exec $SHELL -l
```

**Full Guide**: [MIGRATION-GUIDE.md - Rollback](./MIGRATION-GUIDE.md#rollback-procedures)

---

## Directory Structure

### Installation Files

```
install-moai-ko/
├── README.md                 # Main installation guide (700 lines)
├── MIGRATION-GUIDE.md        # Migration guide (750 lines)
├── KOREAN-FONTS-GUIDE.md     # Korean fonts guide (600 lines)
├── INDEX.md                  # This file (350 lines)
├── test-suite.sh             # Test suite (650 lines, 140+ tests)
│
├── install-moai-adk.py       # UV installer script
├── install-moai-adk.sh       # Bash installer app
├── verify-installation.sh    # Post-install verification
│
├── apps/                     # Bash apps
│   ├── interactive-installer.sh
│   ├── korean-font-setup.sh
│   └── terminal-config.sh
│
├── scripts/                  # UV scripts
│   ├── install-uv.py
│   ├── install-fonts.py
│   ├── configure-terminal.py
│   └── setup-mcp.py
│
└── skills/                   # Claude skills
    └── moai-adk-installer/
        ├── skill.yaml
        ├── README.md
        └── prompts/
            ├── main.md
            ├── install-uv.md
            ├── install-fonts.md
            └── verify.md
```

### Post-Installation

```
~/moai-adk/                   # Installation root
├── bin/                      # Executables
├── lib/                      # Libraries
├── share/                    # Shared resources
│   ├── fonts/                # Installed fonts
│   ├── templates/            # Project templates
│   └── docs/                 # Documentation
└── var/                      # Variable data
    ├── logs/                 # Log files
    └── cache/                # Cache
```

---

## Documentation Statistics

### File Metrics

| File | Lines | Tests | Status |
|------|-------|-------|--------|
| README.md | 700+ | N/A | ✅ Complete |
| MIGRATION-GUIDE.md | 750+ | N/A | ✅ Complete |
| KOREAN-FONTS-GUIDE.md | 600+ | N/A | ✅ Complete |
| INDEX.md | 350+ | N/A | ✅ Complete |
| test-suite.sh | 650+ | 140+ | ✅ Complete |

### Content Coverage

**Installation Approaches**:
- ✅ UV CLI Scripts (fully documented)
- ✅ Bash Apps (fully documented)
- ✅ Claude Skills (fully documented)

**Migration Paths**:
- ✅ Path 1: UV CLI (complete)
- ✅ Path 2: Bash App (complete)
- ✅ Path 3: Claude Skill (complete)
- ✅ Path 4: Gradual Migration (complete)

**Korean Support**:
- ✅ D2Coding font installation
- ✅ Terminal configuration (Ghostty, iTerm2, Warp)
- ✅ Troubleshooting guide
- ✅ Alternative fonts
- ✅ CJK character support
- ✅ Testing procedures

**Team Deployment**:
- ✅ Small team rollout (2-5 devs)
- ✅ Medium team rollout (6-20 devs)
- ✅ Large team rollout (20+ devs)
- ✅ Rollback procedures

**Testing**:
- ✅ 140+ tests across 8 categories
- ✅ Korean-specific tests (8 tests)
- ✅ CI/CD integration (JSON output)
- ✅ Multiple output modes

---

## Additional Resources

### GitHub Repository

**MoAI-ADK**: https://github.com/ruvnet/moai-adk

### Related Documentation

**Main Project Docs**:
- Quick Start: `~/moai-adk/docs/QUICKSTART.md`
- API Reference: `~/moai-adk/docs/API-REFERENCE.md`
- Architecture: `~/moai-adk/docs/ARCHITECTURE.md`
- Troubleshooting: `~/moai-adk/docs/TROUBLESHOOTING.md`

### Community

- **Issues**: https://github.com/ruvnet/moai-adk/issues
- **Discussions**: https://github.com/ruvnet/moai-adk/discussions
- **Releases**: https://github.com/ruvnet/moai-adk/releases

### External Resources

**UV Package Manager**:
- Website: https://astral.sh/uv
- Docs: https://docs.astral.sh/uv/

**D2Coding Font**:
- Repository: https://github.com/naver/d2codingfont
- Releases: https://github.com/naver/d2codingfont/releases

**Ghostty Terminal**:
- Website: https://ghostty.org
- Docs: https://ghostty.org/docs

**Claude Code**:
- Anthropic: https://anthropic.com
- Claude Code CLI: https://docs.anthropic.com/claude-code

---

## Getting Help

### Documentation

1. **Read the guides**:
   - [README.md](./README.md) for installation
   - [MIGRATION-GUIDE.md](./MIGRATION-GUIDE.md) for migration
   - [KOREAN-FONTS-GUIDE.md](./KOREAN-FONTS-GUIDE.md) for fonts

2. **Run tests**:
   ```bash
   ./test-suite.sh --verbose
   ```

3. **Check logs**:
   ```bash
   cat ~/.claude/logs/moai-install.log
   tail -f ~/.claude/logs/mcp-*.log
   ```

### Community Support

1. **Search existing issues**:
   https://github.com/ruvnet/moai-adk/issues

2. **Ask in discussions**:
   https://github.com/ruvnet/moai-adk/discussions

3. **Create new issue**:
   Include:
   - OS version
   - Installation method used
   - Error messages
   - Steps to reproduce

### Professional Support

For enterprise deployments:
- Contact: support@moai-adk.com
- Enterprise docs: Available on request
- Custom training: Available

---

## Version History

### v1.0.0 (2025-11-29)

**Initial Release**:
- ✅ Complete installation documentation (700 lines)
- ✅ Migration guide with 4 paths (750 lines)
- ✅ Korean fonts guide (600 lines)
- ✅ Comprehensive test suite (650 lines, 140+ tests)
- ✅ Documentation index (350 lines)

**Korean Support**:
- ✅ D2Coding font integration
- ✅ Terminal configurations (Ghostty, iTerm2, Warp)
- ✅ Korean-specific tests (8 tests)
- ✅ Troubleshooting guide

**Beyond-MCP Pattern**:
- ✅ UV CLI scripts
- ✅ Bash interactive apps
- ✅ Claude AI skills

**Team Features**:
- ✅ Rollout plans (small, medium, large teams)
- ✅ Rollback procedures
- ✅ CI/CD integration

---

## Quick Links

### Getting Started
- [Main Installation Guide](./README.md)
- [Quick Start (5 minutes)](./README.md#quick-start)
- [Choose Installation Approach](./README.md#installation-approaches)

### Migration
- [Migration Guide](./MIGRATION-GUIDE.md)
- [Path 1: UV CLI](./MIGRATION-GUIDE.md#path-1-uv-cli-migration-recommended)
- [Path 2: Bash App](./MIGRATION-GUIDE.md#path-2-bash-installation-migration)
- [Path 3: Claude Skill](./MIGRATION-GUIDE.md#path-3-claude-skill-migration)
- [Path 4: Gradual](./MIGRATION-GUIDE.md#path-4-gradual-migration-existing-projects)

### Korean Support
- [Korean Fonts Guide](./KOREAN-FONTS-GUIDE.md)
- [D2Coding Installation](./KOREAN-FONTS-GUIDE.md#d2coding-font)
- [Ghostty Configuration](./KOREAN-FONTS-GUIDE.md#ghostty-configuration)
- [Troubleshooting Korean](./KOREAN-FONTS-GUIDE.md#troubleshooting-korean-rendering)

### Testing & Verification
- [Test Suite](./test-suite.sh)
- [Verification Steps](./MIGRATION-GUIDE.md#verification)
- [Korean Tests](./test-suite.sh) (run with `--korean`)

### Support
- [Troubleshooting](./MIGRATION-GUIDE.md#troubleshooting)
- [Team Rollout](./MIGRATION-GUIDE.md#team-rollout-plan)
- [Rollback Procedures](./MIGRATION-GUIDE.md#rollback-procedures)

---

**Happy Installing! 🚀**

**한국어 지원과 함께 즐거운 설치 되세요!**
