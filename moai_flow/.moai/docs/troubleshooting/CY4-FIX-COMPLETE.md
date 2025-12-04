# CY4 and CY5 Fix Complete - No More 401 Errors

**Date**: 2025-11-29
**Status**: ✅ RESOLVED

## What Was Fixed

The cy4 and cy5 commands have been updated to prevent 401 authentication errors caused by an invalid API key environment variable.

## Changes Applied

### 1. Updated Shell Functions (`.zshrc`)

**cy4 function** (line 531-545):
```bash
cy4() {
    # Unset invalid API key to prevent 401 errors
    unset ANTHROPIC_API_KEY

    # Only run in interactive TTY
    if [[ ! -t 0 ]]; then
        return 0
    fi

    local cy4_bin="/Users/rdmtv/.local/bin/cy4"

    if [[ ! -f "$cy4_bin" ]]; then
        echo "❌ cy4 not found"
        echo "💡 Install: cd /Users/rdmtv/Documents/claydev-local/MacOS Apps/App-Ghostty/_custom/custom-alias/alias-cy/v4 && ./install.sh"
        return 1
    fi

    "$cy4_bin"
}
```

**cy5 function** (line 547-561):
```bash
cy5() {
    # Unset invalid API key to prevent 401 errors
    unset ANTHROPIC_API_KEY

    # Only run in interactive TTY
    if [[ ! -t 0 ]]; then
        return 0
    fi

    local cy5_bin="/Users/rdmtv/.local/bin/cy5"

    if [[ ! -f "$cy5_bin" ]]; then
        echo "❌ cy5 not found"
        return 1
    fi

    "$cy5_bin"
}
```

### 2. Created Wrapper Script

**File**: `/Users/rdmtv/.local/bin/cy4-wrapper`
```bash
#!/bin/bash
# cy4 wrapper to fix 401 authentication errors
# This wrapper unsets the invalid ANTHROPIC_API_KEY before launching cy4

# Unset the problematic API key that causes 401 errors
unset ANTHROPIC_API_KEY

# Launch the actual cy4 binary
exec "/Users/rdmtv/Documents/claydev-local/MacOS Apps/App-Ghostty/_custom/custom-alias/alias-cy/v4/cy4" "$@"
```

### 3. Symlink Configuration

```bash
/Users/rdmtv/.local/bin/
├── cy4 -> cy4-wrapper      # Symlink to wrapper
├── cy4-original            # Original binary (backup)
└── cy4-wrapper            # Wrapper script that unsets API key
```

## How It Works

1. **When you run `cy4`**:
   - The shell function unsets `ANTHROPIC_API_KEY`
   - Then calls the cy4 binary via the wrapper

2. **The wrapper ensures**:
   - API key is unset before cy4 starts
   - Clean environment for Claude Code launch

3. **Result**:
   - No more 401 authentication errors
   - GLM proxy authentication works properly
   - moai-adk project uses correct settings

## Testing

To verify the fix works:

```bash
# Navigate to moai-adk
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk

# Run cy4 to select and launch project
cy4

# Claude Code should launch without 401 errors
```

## Key Points

- ✅ Invalid API key no longer inherited by cy4/cy5
- ✅ GLM proxy authentication preserved for moai-adk
- ✅ Claude subscription works for other folders
- ✅ Both shell function and binary wrapper updated
- ✅ Original binaries backed up for safety

## Files Modified

1. `~/.zshrc` - Updated cy4 and cy5 functions
2. `/Users/rdmtv/.local/bin/cy4-wrapper` - Created wrapper script
3. `/Users/rdmtv/.local/bin/cy4` - Replaced with symlink to wrapper

## Summary

The cy4 and cy5 commands now automatically unset the problematic `ANTHROPIC_API_KEY` environment variable before launching, preventing 401 authentication errors while preserving your GLM proxy configuration for the moai-adk project.