# File Organization Rules

> Claude-Flow's Absolute Rule: NEVER save working files to the root folder

## Overview

Claude-Flow enforces strict file organization to prevent project root pollution - a principle MoAI already partially implements via `.moai/` hierarchy.

---

## Claude-Flow Rules

### Absolute Rule

```
🚨 NEVER save working files, text/mds and tests to the root folder
```

### Required Directory Structure

| Directory | Purpose | File Types |
|-----------|---------|------------|
| `/src` | Source code | `.js`, `.ts`, `.py`, etc. |
| `/tests` | Test files | `*.test.js`, `*.spec.ts` |
| `/docs` | Documentation | `*.md` (except root README) |
| `/config` | Configuration | `*.json`, `*.yaml`, `*.env` |
| `/scripts` | Utility scripts | `*.sh`, `*.py` scripts |
| `/examples` | Example code | Sample implementations |

### Prohibited in Root

- Working files (`*.tmp`, `*.bak`)
- Test files (`*.test.js`)
- Documentation (except `README.md`)
- Generated reports
- Temporary outputs

---

## MoAI Current Implementation

MoAI has a comprehensive document management system in `.moai/config/config.json`:

### Existing Structure

```
.moai/
├── reports/          # inspection, phases, sync, analysis, validation, daily
├── logs/             # sessions, agent-transcripts, errors, execution
├── scripts/          # dev, conversion, validation, analysis, maintenance
├── temp/             # tests, coverage, work, research
├── backups/          # specs, docs, hooks, skills, config, legacy
├── cache/            # mcp, analysis
├── specs/            # SPEC-* documents
├── docs/             # Generated documentation
└── memory/           # Session state
```

### Root Whitelist (Allowed in Root)

MoAI explicitly allows these in project root:
- `README.md`, `README.*.md`
- `CHANGELOG.md`, `CONTRIBUTING.md`, `CLAUDE.md`
- `LICENSE`, `LICENSE.*`
- Build configs: `pyproject.toml`, `package.json`, `tsconfig.json`
- Git files: `.gitignore`, `.gitattributes`
- Docker: `Dockerfile`, `docker-compose.yml`
- Editor: `.editorconfig`, `.prettierrc`, `.eslintrc*`

---

## Comparison

| Aspect | Claude-Flow | MoAI |
|--------|-------------|------|
| Root Protection | Enforced | Configurable (`block_root_pollution`) |
| Report Location | `/docs` | `.moai/reports/` |
| Test Location | `/tests` | Project `/tests` or `.moai/temp/tests/` |
| Validation | Implicit | Explicit (`validation.enabled`) |
| Auto-Migration | No | Yes (`auto_migration.enabled`) |
| Cleanup | Manual | Automated (`cleanup.schedule`) |

---

## MoAI Advantage

MoAI's system is MORE sophisticated:

1. **Auto-categorization**: Files automatically sorted by pattern
2. **Retention policies**: Different retention days per category
3. **Cleanup automation**: Scheduled cleanup at session end
4. **Migration suggestions**: Auto-detect misplaced files
5. **Whitelist system**: Explicit allowed files in root

### Configuration Example

```json
{
  "document_management": {
    "enabled": true,
    "enforce_structure": true,
    "block_root_pollution": false,
    "validation": {
      "on_file_create": true,
      "on_session_end": true,
      "warn_violations": true
    },
    "auto_migration": {
      "suggest_moves": true,
      "require_user_approval": true
    }
  }
}
```

---

## Recommendation

MoAI's existing system is **superior** to Claude-Flow's simple rules.

**Enhancement opportunity**: Make `block_root_pollution: true` the default for stricter enforcement matching Claude-Flow's philosophy.

---

## Key Principle

Both systems share the same core principle:

> **Keep project root clean. Organize files in appropriate subdirectories.**

MoAI implements this more comprehensively with `.moai/` hierarchy and automated management.
