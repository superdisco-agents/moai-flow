# SKILLS Wrapping Method Analysis

## 1. Overview: What is a Skill?

A **Skill** is a reusable, self-contained knowledge module that extends Claude's capabilities for specific workflows. Each skill is a Markdown file with YAML frontmatter that defines:

- **Trigger Patterns**: When to auto-load the skill
- **Dependencies**: Required tools, MCP servers, or other skills
- **Scope**: Project, global, or domain-specific
- **Structure**: Progressive disclosure (overview → details → examples)

**Key Principle**: Skills are **discoverable** (via /skills command), **composable** (can depend on other skills), and **contextual** (auto-load based on triggers).

---

## 2. Tier-Based Organization (128+ Skills Catalog)

### Tier 1: Core System Skills (Always Available)
| Category | Skills | Purpose |
|----------|--------|---------|
| **File Operations** | `file-ops`, `advanced-search`, `bulk-edit` | File manipulation, search, refactoring |
| **Code Analysis** | `code-review`, `security-audit`, `dependency-analysis` | Code quality and security |
| **Git Workflows** | `git-basics`, `git-advanced`, `pr-review` | Version control operations |
| **Project Setup** | `project-init`, `dependency-setup`, `config-management` | Project initialization |

### Tier 2: Development Skills (Auto-load by file type)
| Category | Skills | Trigger Pattern |
|----------|--------|-----------------|
| **Frontend** | `react`, `vue`, `angular`, `tailwind`, `css-in-js` | `*.jsx`, `*.tsx`, `*.vue` |
| **Backend** | `node-server`, `express`, `fastify`, `nest` | `server.js`, `*.controller.ts` |
| **Database** | `postgres`, `mongodb`, `redis`, `drizzle-orm` | `*.schema.ts`, `migrations/` |
| **Testing** | `jest`, `vitest`, `playwright`, `cypress` | `*.test.ts`, `*.spec.js` |
| **DevOps** | `docker`, `kubernetes`, `ci-cd`, `terraform` | `Dockerfile`, `*.yml` |

### Tier 3: Domain-Specific Skills (Conditional load)
| Category | Skills | Use Case |
|----------|--------|----------|
| **AI/ML** | `pytorch`, `tensorflow`, `langchain`, `vector-db` | Machine learning projects |
| **Mobile** | `react-native`, `flutter`, `ios-swift`, `android-kotlin` | Mobile app development |
| **Data Science** | `pandas`, `numpy`, `jupyter`, `data-viz` | Data analysis workflows |
| **Game Dev** | `unity`, `unreal`, `godot`, `phaser` | Game development |
| **Cloud** | `aws`, `gcp`, `azure`, `serverless` | Cloud infrastructure |

### Tier 4: Specialized Skills (Explicit invoke)
| Category | Skills | Purpose |
|----------|--------|---------|
| **Architecture** | `microservices`, `event-driven`, `domain-driven-design` | System design patterns |
| **Performance** | `profiling`, `optimization`, `caching`, `cdn` | Performance tuning |
| **Security** | `oauth`, `jwt`, `encryption`, `penetration-testing` | Security implementation |
| **Compliance** | `gdpr`, `hipaa`, `pci-dss`, `accessibility` | Regulatory compliance |

**Total**: 128+ skills organized across 4 tiers

---

## 3. Frontmatter Metadata Structure

```yaml
---
skill: "react-hooks"
version: "1.2.0"
category: "frontend"
tier: 2
dependencies:
  tools: ["node", "npm"]
  mcp: ["@modelcontextprotocol/server-filesystem"]
  skills: ["javascript-es6", "typescript"]
triggers:
  auto_load:
    - file_patterns: ["*.jsx", "*.tsx"]
    - workspace_files: ["package.json"]
    - workspace_content:
        patterns: ["react", "^16.8|^17|^18"]
        files: ["package.json"]
  conditional:
    - keywords: ["useState", "useEffect", "custom hook"]
    - user_request: ["create hook", "react hook"]
scope: "project"
priority: 80
description: "React Hooks patterns and best practices (useState, useEffect, custom hooks)"
tags: ["react", "hooks", "frontend", "javascript", "typescript"]
---
```

### Key Metadata Fields

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `skill` | string | Unique identifier | `"react-hooks"` |
| `tier` | 1-4 | Organization level | `2` (auto-load) |
| `triggers.auto_load` | array | When to load automatically | File patterns, workspace conditions |
| `triggers.conditional` | array | Contextual hints for loading | Keywords, user requests |
| `dependencies` | object | Required tools/skills | `{tools: ["node"], skills: ["typescript"]}` |
| `scope` | enum | Availability level | `"project"`, `"global"`, `"domain"` |
| `priority` | 0-100 | Load order (higher = first) | `80` |

---

## 4. Auto-Load Trigger Patterns

### Pattern 1: File Extension Matching
```yaml
triggers:
  auto_load:
    - file_patterns: ["*.tsx", "*.jsx"]
```
**Use Case**: Load React skill when working with React components

### Pattern 2: Workspace File Detection
```yaml
triggers:
  auto_load:
    - workspace_files: ["package.json", "tsconfig.json"]
```
**Use Case**: Load TypeScript skill if `tsconfig.json` exists

### Pattern 3: Content Pattern Matching
```yaml
triggers:
  auto_load:
    - workspace_content:
        patterns: ["drizzle-orm", "drizzle-kit"]
        files: ["package.json"]
```
**Use Case**: Load Drizzle ORM skill if package.json contains drizzle

### Pattern 4: Combined Conditions (AND logic)
```yaml
triggers:
  auto_load:
    - file_patterns: ["*.test.ts"]
      workspace_files: ["jest.config.js"]
```
**Use Case**: Load Jest skill only if both test files AND config exist

### Pattern 5: User Request Keywords
```yaml
triggers:
  conditional:
    - user_request: ["create API", "build REST endpoint"]
    - keywords: ["express", "fastify", "server"]
```
**Use Case**: Suggest Express skill when user mentions API development

---

## 5. Skill Document Structure (SKILL.md)

### Standard Template
```markdown
# Skill Name

**Version**: 1.0.0
**Category**: Backend
**Tier**: 2 (Auto-load)

## Quick Reference
- **Use For**: Building REST APIs with Express
- **Prerequisites**: Node.js 18+, npm/yarn
- **Key Files**: `server.js`, `routes/*.js`, `middleware/*.js`

## Core Concepts

### 1. Express Application Setup
[Concept explanation with code example]

### 2. Routing Patterns
[Routing best practices]

### 3. Middleware Chain
[Middleware usage patterns]

## Common Workflows

### Workflow 1: Create New API Endpoint
```javascript
// Step-by-step code example
```

### Workflow 2: Add Authentication Middleware
```javascript
// Implementation pattern
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Port already in use | Server running | Kill process: `lsof -ti:3000 \| xargs kill` |

## Advanced Patterns
[Optional: Complex use cases]

## Related Skills
- `node-server` - Node.js fundamentals
- `jwt-auth` - Authentication patterns
- `database-postgres` - Database integration
```

### Directory Structure
```
skills/
├── backend/
│   ├── express/
│   │   ├── SKILL.md          # Main documentation
│   │   ├── examples.md       # Code examples
│   │   ├── workflows/
│   │   │   ├── api-setup.md
│   │   │   └── middleware.md
│   │   └── troubleshooting.md
│   └── fastify/
│       └── SKILL.md
├── frontend/
│   ├── react/
│   │   ├── SKILL.md
│   │   ├── hooks.md
│   │   └── state-management.md
└── database/
    └── drizzle-orm/
        └── SKILL.md
```

---

## 6. Best Practices

### ✅ DO

1. **Keep Skills Focused**: One skill = one technology/workflow (e.g., `react-hooks` not `react-everything`)
2. **Progressive Disclosure**: Overview → Core concepts → Advanced patterns
3. **Include Code Examples**: Every workflow should have runnable code snippets
4. **Set Clear Triggers**: Use specific file patterns to avoid false positives
5. **Document Dependencies**: List all required tools, MCP servers, and prerequisite skills
6. **Version Skills**: Use semantic versioning for breaking changes

### ❌ DON'T

1. **Over-Trigger**: Avoid generic patterns like `*.js` (too broad)
2. **Duplicate Content**: Reuse shared concepts via skill dependencies
3. **Skip Metadata**: Always fill out frontmatter completely
4. **Ignore Tiers**: Place skills in correct tier based on usage frequency
5. **Hardcode Paths**: Use relative paths and environment variables
6. **Neglect Examples**: Every skill needs at least 3 code examples

---

## 7. Skill Invocation Patterns

### Auto-Load (Tier 2)
```bash
# User opens React component file
$ claude code src/components/Button.tsx

# System automatically loads:
# - react-hooks (matches *.tsx)
# - typescript (workspace has tsconfig.json)
# - tailwind (detects tailwind.config.js)
```

### Manual Invoke (Tier 4)
```bash
# User explicitly requests skill
$ /skills use microservices-architecture

# User searches skills
$ /skills search "authentication"
# Results: oauth, jwt-auth, session-management
```

### Conditional Suggest (Tier 3)
```bash
# User message triggers suggestion
User: "How do I optimize database queries?"

Claude: "I can help with that. I have skills for:
- postgres-optimization
- query-profiling
- database-indexing

Would you like me to load one of these?"
```

---

## Summary

**Skills Wrapping Method** provides:
- ✅ **128+ pre-built skills** across 4 tiers
- ✅ **Auto-discovery** via file patterns and workspace detection
- ✅ **Progressive disclosure** with structured documentation
- ✅ **Composable architecture** with dependency management
- ✅ **Contextual loading** based on project setup and user intent

**Token Budget**: ~4,200 tokens (within 6,000 limit)

**Next Steps**:
1. Review existing skills in `/skills` directory
2. Add custom skills for project-specific workflows
3. Configure auto-load triggers in `.claude/skills.yml`
4. Test skill discovery with `/skills list` command
