# Collector README Workflows

> Automated pipelines for branch README generation and validation

---

## Available Workflows

| Workflow | Description | Trigger |
|----------|-------------|---------|
| [readme-generation](./readme-generation.md) | 7-stage README generation pipeline | manual, on_branch_update, on_merge |

---

## Workflow Structure

Each workflow follows TOON+MD pairing:

```
workflows/
├── README.md           # This index file
├── {name}.toon         # YAML orchestration (machine-readable)
└── {name}.md           # Documentation (human-readable)
```

---

## Quick Commands

```bash
# Generate README for specific branch
/collector:readme feature/branch-name

# Generate for all tracked branches
/collector:readme --all

# Validate only (no file output)
/collector:readme --validate-only
```

---

**Version**: 1.0.0 | **Last Updated**: 2025-12-04
