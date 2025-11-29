# Claude-Flow Uninstaller Documentation

## Overview

Comprehensive Python script for safely removing claude-flow directories and packages with multiple safety features and operation modes.

## Location

```
_config/MOAI-ADK/scripts/uninstall-claude-flow.py
```

## Features

### 🗑️ Removal Capabilities
- **Directories**: `.claude-flow`, `.swarm`, `.hive-mind`, `.specstory`, `node_modules/.cache/claude-flow`
- **NPM Packages**: Global `claude-flow`, `@claude-flow/core`, `@claude-flow/cli`
- **NPM Cache**: Automatic cache cleaning after package removal

### 🛡️ Safety Features
- **Dry-run mode**: Preview changes without making any modifications (default)
- **Backup mode**: Archive directories before deletion
- **Size calculation**: Shows disk space to be freed
- **Interactive confirmation**: Requires explicit user confirmation
- **Verification**: Checks removal success after execution
- **Error handling**: Detailed error reporting and recovery

### 🤖 Operation Modes
1. **Standalone mode**: Direct execution with colored output
2. **Agent SDK mode**: AI-guided analysis and recommendations

### 📊 Reporting
- **Real-time progress**: Colored console output
- **JSON reports**: Detailed uninstall logs saved to `_config/MOAI-ADK/reports/`
- **Exit codes**: Standard Unix exit codes (0=success, 1=error, 4=cleanup failed)

## Usage

### Preview Mode (Default)

```bash
# Shows what would be removed without making changes
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py

# Explicit dry-run
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --dry-run

# Verbose output
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --dry-run --verbose
```

### Uninstall Mode

```bash
# Basic uninstall (with confirmation)
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --yes

# Uninstall with backup
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --backup --yes

# Uninstall without confirmation (use with caution)
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py -y
```

### AI-Guided Mode

```bash
# AI analysis and recommendations
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --agent

# AI-guided uninstall with backup
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --agent --backup
```

## Command-Line Options

```
Options:
  --dry-run          Preview what would be removed (no changes)
  --backup           Create backups before removing directories
  --yes, -y          Skip confirmation prompt
  --agent            Use Claude Agent SDK for AI-guided uninstallation
  --verbose, -v      Show detailed output
  --help, -h         Show help message
```

## Examples

### Example 1: Preview Before Uninstalling

```bash
# Step 1: See what will be removed
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py

# Step 2: If satisfied, proceed with uninstall
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --yes
```

**Output:**
```
🗑️  Claude-Flow Uninstaller [DRY RUN]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 Scanning for claude-flow directories...

  ✓ Found .claude-flow                      (12.45 MB)
  ✓ Found .swarm                            (3.21 MB)
  ✓ Found .hive-mind                        (5.67 MB)

📦 Checking npm packages...

  ✓ Found claude-flow                       (v2.0.0)

📊 Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Directories:
  Would remove    .claude-flow                      (12.45 MB)
  Would remove    .swarm                            (3.21 MB)
  Would remove    .hive-mind                        (5.67 MB)

NPM Packages:
  Would remove    claude-flow                       (v2.0.0)

Total space to be freed: 21.33 MB
```

### Example 2: Safe Uninstall with Backup

```bash
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --backup --yes
```

**Output:**
```
🗑️  Claude-Flow Uninstaller [UNINSTALL + BACKUP]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  WARNING: This will permanently remove claude-flow
ℹ  Backups will be saved to _backups/claude-flow-uninstall/

🗑️  Removing directories...

  🗑️  Removing: .claude-flow
  📦 Creating backup: .claude-flow_20251128_143022
     ✓ Removed successfully

  🗑️  Removing: .swarm
  📦 Creating backup: .swarm_20251128_143023
     ✓ Removed successfully

🗑️  Uninstalling npm packages...

  🗑️  Uninstalling: claude-flow
     ✓ Uninstalled successfully

  🧹 Cleaning npm cache...
     ✓ Cache cleaned

🔍 Verifying removal...

  ✓ .claude-flow - removed
  ✓ .swarm - removed

✓ Report saved to: _config/MOAI-ADK/reports/claude-flow-uninstall_20251128_143025.json

✅ Claude-Flow uninstalled successfully!
```

### Example 3: AI-Guided Analysis

```bash
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --agent
```

**Output:**
```
🤖 Claude Agent SDK Mode
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 Analyzing with Claude...

Based on my analysis of your claude-flow installation:

Assessment:
- 3 main directories will be removed (.claude-flow, .swarm, .hive-mind)
- 1 npm package will be uninstalled (claude-flow v2.0.0)
- Total disk space to be freed: 21.33 MB

Potential Issues:
- The .swarm directory contains coordination data that may be needed by other projects
- Consider backing up .hive-mind if you have custom neural patterns trained

Recommendations:
1. Use --backup flag to preserve data before removal
2. Check if other projects depend on claude-flow coordination features
3. Export any important session data or neural patterns
4. Verify no active swarm processes are running

This appears to be a complete uninstallation that will fully remove claude-flow
from your system. The backup option is highly recommended for safety.

Proceed with uninstall based on AI analysis? (yes/no):
```

## Exit Codes

The script uses standard Unix exit codes:

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Uninstall completed successfully or nothing to do |
| 1 | Error | Error occurred during uninstallation |
| 4 | Cleanup Failed | Verification found items still exist after removal |

## Report Format

JSON reports are saved to `_config/MOAI-ADK/reports/claude-flow-uninstall_TIMESTAMP.json`:

```json
{
  "timestamp": "2025-11-28T14:30:25.123456",
  "mode": "uninstall",
  "backup_enabled": true,
  "base_directory": "/Users/username/project",
  "directories": [
    {
      "name": ".claude-flow",
      "path": "/Users/username/project/.claude-flow",
      "size": 13058048,
      "size_formatted": "12.45 MB",
      "type": "directory",
      "removed": true,
      "backup_path": "_backups/claude-flow-uninstall/.claude-flow_20251128_143022"
    }
  ],
  "packages": [
    {
      "name": "claude-flow",
      "version": "2.0.0",
      "type": "npm-global",
      "removed": true
    }
  ],
  "total_size_bytes": 22371328,
  "total_size_formatted": "21.33 MB",
  "errors": [],
  "summary": {
    "directories_found": 3,
    "packages_found": 1,
    "items_removed": 4,
    "errors_count": 0
  }
}
```

## Backup Structure

Backups are stored in `_backups/claude-flow-uninstall/`:

```
_backups/
└── claude-flow-uninstall/
    ├── .claude-flow_20251128_143022/
    ├── .swarm_20251128_143023/
    └── .hive-mind_20251128_143024/
```

## Testing

Run the test script to verify functionality:

```bash
bash _config/MOAI-ADK/scripts/test-uninstall.sh
```

## Troubleshooting

### Issue: "Permission denied" errors

**Solution:**
```bash
# Make script executable
chmod +x _config/MOAI-ADK/scripts/uninstall-claude-flow.py

# Or run with sudo (not recommended)
sudo python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --yes
```

### Issue: NPM packages not found

**Solution:**
This is normal if claude-flow was not installed globally. The script will skip npm uninstallation and only remove directories.

### Issue: Directories still exist after uninstall

**Solution:**
```bash
# Check if processes are using the directories
lsof | grep claude-flow

# Kill any processes
pkill -f claude-flow

# Re-run uninstaller
python3 _config/MOAI-ADK/scripts/uninstall-claude-flow.py --yes
```

### Issue: Want to restore from backup

**Solution:**
```bash
# List backups
ls -la _backups/claude-flow-uninstall/

# Restore specific directory
cp -r _backups/claude-flow-uninstall/.claude-flow_20251128_143022 ./.claude-flow
```

## Dependencies

The script automatically installs required dependencies:
- `packaging` - Version comparison utilities

Optional dependencies for AI mode:
- `claude-agent-sdk` - AI-guided uninstallation

## Best Practices

1. **Always preview first**: Run without `--yes` to see what will be removed
2. **Use backups for production**: Add `--backup` flag when working on important projects
3. **Check reports**: Review JSON reports for audit trails
4. **Verify removal**: Script automatically verifies, but double-check critical directories
5. **AI guidance**: Use `--agent` mode for complex scenarios or when unsure

## Related Documentation

- [Installation Guide](./INSTALL-MOAI-ADK.md)
- [Version Checker](./scripts/check-latest-version.py)
- [MoAI-ADK Configuration](./CONFIGURATION.md)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review JSON reports in `_config/MOAI-ADK/reports/`
3. Run with `--verbose` flag for detailed output
4. Use `--agent` mode for AI-powered guidance
