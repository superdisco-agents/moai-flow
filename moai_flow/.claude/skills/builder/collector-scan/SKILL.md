---
name: collector-scan
description: Scan and compare MoAI workspaces (local and GitHub remote) to collect improvement candidates
version: 3.0.0
modularized: true
tier: 3
category: builder
last_updated: 2025-12-04
compliance_score: 95
auto_trigger_keywords:
  - workspace comparison
  - compare workspaces
  - scan workspace
  - collector scan
  - collector
  - github sync
  - remote comparison
color: cyan
---

# Collector: Scan

**Intelligent workspace scanning and comparison for MoAI consolidation**

> **Version**: 3.0.0
> **Status**: Production Ready
> **Part of**: MoAI Flow System

---

## Collector Scope

> **SCOPE**: `.claude/` `.moai/` `src/moai_adk/` **ONLY**

| Directory | Purpose |
|-----------|---------|
| `.claude/` | Claude Code config (agents, skills, commands, hooks) |
| `.moai/` | MoAI runtime (config, specs, memory, docs) |
| `src/moai_adk/` | Framework source code |

**Excluded**: All other folders (node_modules, dist, .git, README.md, etc.)

## Quick Reference

### Purpose
Scan multiple MoAI workspaces to:
- Extract metadata (versions, skills, agents, commands)
- Compare components between workspaces
- Identify differences (unique to A, unique to B, in both)
- Generate structured reports for downstream processing

### Quick Invocation
```python
Skill("moai-flow-collector")
```

### Core Workflow
```
Workspace A ──┐
              ├──▶ Scan ──▶ Compare ──▶ Report
Workspace B ──┘
```

---

## Level 1: Scanning Workspaces

### What to Scan

Every MoAI workspace has these key directories:

| Directory | Contents | Key Files |
|-----------|----------|-----------|
| `.claude/` | Claude Code config | `settings.json`, `agents/`, `commands/`, `skills/` |
| `.moai/` | MoAI runtime | `config/config.json`, `specs/`, `memory/` |
| `src/moai_adk/` | Framework source | `pyproject.toml`, `src/` |

### Scan Command Pattern

```bash
# Get skill list
ls -1 {workspace}/.claude/skills/ | sort

# Get agent list
ls -1 {workspace}/.claude/agents/moai/ | sort

# Get command list
ls -1 {workspace}/.claude/commands/ | sort

# Get moai-adk version
grep 'version' {workspace}/moai-adk/pyproject.toml | head -1

# Get last commit
cd {workspace}/moai-adk && git log -1 --format="%H %ci %s"

# Get CLAUDE.md modification time
stat -f "%Sm" {workspace}/CLAUDE.md
```

### Metadata Extraction

For each workspace, extract:

```json
{
  "id": "workspace-name",
  "path": "/absolute/path/to/workspace",
  "scanned_at": "2025-12-02T14:30:00Z",
  "moai_version": "0.31.2",
  "components": {
    "skills": {
      "count": 31,
      "list": ["moai-foundation-core", "moai-connector-github", ...]
    },
    "agents": {
      "count": 30,
      "list": ["builder-agent", "expert-backend", ...]
    },
    "commands": {
      "count": 23,
      "list": ["moai:1-plan", "moai:2-run", ...]
    }
  },
  "git": {
    "last_commit_sha": "e2494cba",
    "last_commit_date": "2025-12-02",
    "last_commit_message": "feat: add new skill"
  },
  "files": {
    "claude_md_modified": "2025-12-02T12:33:00Z",
    "settings_json_size": 4940
  }
}
```

---

## Level 2: Comparing Workspaces

### Comparison Algorithm

```
1. Load scan results for Workspace A and B
2. Compare skill lists:
   - skills_only_in_a = A.skills - B.skills
   - skills_only_in_b = B.skills - A.skills
   - skills_in_both = A.skills ∩ B.skills
3. For skills_in_both, compare modification dates
4. Repeat for agents, commands
5. Compare CLAUDE.md content (hash or line count)
6. Generate comparison report
```

### Comparison Report Format

```json
{
  "collection_id": "flow-2025-12-02-001",
  "created_at": "2025-12-02T14:35:00Z",
  "workspaces": {
    "a": { "id": "beyond-mcp", "path": "..." },
    "b": { "id": "moai-ir-deck", "path": "..." }
  },
  "summary": {
    "total_differences": 6,
    "skills_diff": 4,
    "agents_diff": 0,
    "commands_diff": 0
  },
  "skills": {
    "only_in_a": ["decision-logic-framework", "moai-connector-github"],
    "only_in_b": ["builder-workflow"],
    "in_both_different": ["builder"],
    "in_both_same": ["moai-foundation-core", ...]
  },
  "agents": {
    "only_in_a": [],
    "only_in_b": [],
    "in_both_different": [],
    "in_both_same": [...]
  },
  "files": {
    "claude_md": {
      "a_modified": "2025-12-02T12:33:00Z",
      "b_modified": "2025-12-01T16:32:00Z",
      "newer": "a"
    }
  }
}
```

---

## Level 3: Storage & Integration

### Data Storage Location

```
.moai/flow/
├── collections/
│   └── flow-2025-12-02-001/
│       ├── scan-a.json      # Workspace A metadata
│       ├── scan-b.json      # Workspace B metadata
│       └── comparison.json  # Comparison results
├── config.json              # Flow configuration
└── README.md                # Flow system documentation
```

### Collection ID Format
`flow-YYYY-MM-DD-NNN` where NNN is a zero-padded sequence number

### Integration with Downstream Skills

The collector outputs feed into:
- **moai-flow-learner**: Analyzes differences to score improvements
- **moai-flow-consolidator**: Uses comparison to merge intelligently

---

## Works Well With

**Skills**:
- `moai-flow-learner` - Analyzes collected differences
- `moai-flow-consolidator` - Merges based on comparisons
- `moai-connector-github` - Git operations for scanning

**Agents**:
- `moai-flow` - Orchestrates the full flow pipeline

**Commands**:
- `/moai-flow:compare` - Triggers collection workflow

---

## Modules

| Module | Description |
|--------|-------------|
| `scan-workspace.md` | Detailed workspace scanning procedures |
| `compare-versions.md` | Version comparison logic |
| `extract-metadata.md` | Metadata extraction patterns |
| `report-format.md` | JSON report schema documentation |

---

## Quick Checklist

Before running collection:
- [ ] Both workspace paths are accessible
- [ ] Each workspace has `.claude/`, `.moai/`, `moai-adk/`
- [ ] Git is available for commit info
- [ ] `.moai/flow/` directory exists or can be created

After collection:
- [ ] `scan-a.json` created with full metadata
- [ ] `scan-b.json` created with full metadata
- [ ] `comparison.json` shows all differences
- [ ] Collection ID logged for downstream use

---

## Level 4: GitHub Remote Scanning

### Scan Modes

| Mode | Source A | Source B | Use Case |
|------|----------|----------|----------|
| `local` | Local path | Local path | Compare two local workspaces |
| `github` | Local path | GitHub repo | Compare local vs remote |
| `branches` | GitHub main | All branches | Find best version across branches |
| `multi` | Local + GitHub | All sources | Comprehensive comparison |

### GitHub API Integration

**Fetch Repository Contents:**
```bash
# List skills in remote repo
gh api repos/{owner}/{repo}/contents/.claude/skills --jq '.[].name'

# List agents
gh api repos/{owner}/{repo}/contents/.claude/agents/moai --jq '.[].name'

# Get file content (base64 decoded)
gh api repos/{owner}/{repo}/contents/.claude/skills/{skill}/SKILL.md \
  --jq '.content' | base64 -d

# List all branches
gh api repos/{owner}/{repo}/branches --jq '.[].name'

# Get specific branch content
gh api repos/{owner}/{repo}/contents/.claude/skills?ref={branch} --jq '.[].name'
```

### Multi-Branch Comparison

**Scan across all branches to find best versions:**

```
1. Fetch all branch names
2. For each branch:
   - Scan .claude/skills/
   - Scan .claude/agents/
   - Extract metadata (version, last_commit)
3. Compare same component across branches
4. Generate multi-source comparison report
```

### GitHub Scan Output Format

```json
{
  "collection_id": "flow-2025-12-04-001",
  "mode": "github",
  "local": {
    "path": "/path/to/moai_flow",
    "components": { "skills": 45, "agents": 30 }
  },
  "remote": {
    "repo": "superdisco-agents/moai-adk",
    "branches": ["main", "feature/SPEC-first-builders", ...],
    "per_branch": {
      "main": { "skills": 31, "agents": 20 },
      "feature/SPEC-first-builders": { "skills": 35, "agents": 22 }
    }
  },
  "comparison": {
    "local_only": ["collector-scan", "collector-learner", ...],
    "remote_only": {
      "main": ["moai-domain-adb"],
      "feature/SPEC-first-builders": ["builder-workflow-designer"]
    },
    "both": {
      "moai-foundation-core": {
        "local_version": "2.5.0",
        "main_version": "2.3.0",
        "best_branch": "local"
      }
    }
  }
}
```

### Rate Limit Handling

```bash
# Check API rate limit
gh api rate_limit --jq '.resources.core'

# Response:
# { "limit": 5000, "remaining": 4999, "reset": 1701705600 }
```

**Best Practices:**
- Cache API responses for 5 minutes
- Batch requests where possible
- Use conditional requests (If-Modified-Since)
- Fall back to git clone for large comparisons

---

## Level 5: Component Fingerprinting

### Hash-Based Comparison

For accurate comparison, compute fingerprints:

```bash
# Generate hash for skill directory
find .claude/skills/{skill}/ -type f -exec sha256sum {} \; | sort | sha256sum

# Compare across sources
local_hash=$(...)
remote_hash=$(gh api ... | sha256sum)
```

### Semantic Comparison

Beyond hashes, compare semantic content:

| Check | Method | Weight |
|-------|--------|--------|
| Version string | Extract from SKILL.md frontmatter | High |
| File count | Count files in directory | Medium |
| Total lines | wc -l on all files | Medium |
| Module count | Count modules/ entries | Low |
| Script count | Count scripts/ entries | Low |

---

## Quick Reference: GitHub Commands

```bash
# Full GitHub scan
/collector:scan --mode github --repo superdisco-agents/moai-adk

# Compare against specific branch
/collector:scan --mode github --repo owner/repo --branch feature/xyz

# Multi-branch analysis
/collector:scan --mode branches --repo superdisco-agents/moai-adk

# Comprehensive (local + all remote branches)
/collector:scan --mode multi --repo superdisco-agents/moai-adk
```

---

## Level 6: Orphan Branch Detection

### What is an Orphan Branch?

Orphan 브랜치는 **스코프된 폴더만** 포함하는 브랜치:

```
Proper Orphan Branch:
├── .claude/     ✓
├── .moai/       ✓
└── src/         ✓ (containing moai_adk/)

NOT Orphan (has extra files):
├── .claude/
├── .moai/
├── src/
├── README.md    ✗ Extra
├── package.json ✗ Extra
└── node_modules/✗ Extra
```

### Detection Logic

```bash
# Get root-level contents of a branch
git ls-tree --name-only HEAD

# For proper orphan, should return ONLY:
# .claude
# .moai
# src
```

### Validation Function

```python
def is_orphan_branch(branch_name: str) -> dict:
    """Check if branch is properly scoped orphan branch."""
    import subprocess

    result = subprocess.run(
        ['git', 'ls-tree', '--name-only', branch_name],
        capture_output=True, text=True
    )

    root_items = set(result.stdout.strip().split('\n'))
    allowed = {'.claude', '.moai', 'src'}

    is_orphan = root_items.issubset(allowed)
    extra_items = root_items - allowed

    return {
        "branch": branch_name,
        "is_orphan": is_orphan,
        "root_items": list(root_items),
        "extra_items": list(extra_items),
        "recommendation": "OK" if is_orphan else "Convert with /collector:orphan"
    }
```

### Scan Report Addition

When scanning branches, include orphan status:

```json
{
  "branches": [
    {
      "name": "feature/response-assistant-korean",
      "is_orphan": true,
      "root_items": [".claude"],
      "status": "COMPLIANT"
    },
    {
      "name": "feature/old-branch",
      "is_orphan": false,
      "root_items": [".claude", ".moai", "README.md", "package.json"],
      "extra_items": ["README.md", "package.json"],
      "status": "NEEDS_CONVERSION",
      "recommendation": "Run /collector:orphan feature/old-branch convert"
    }
  ]
}
```

### Quick Commands

```bash
# Check single branch
/collector:scan --check-orphan feature/my-branch

# Scan all branches for orphan compliance
/collector:scan --mode branches --check-orphan-all

# List non-compliant branches
/collector:scan --mode branches --non-orphan-only
```

---

**Version**: 3.0.0 | **Status**: Production Ready | **Last Updated**: 2025-12-04
