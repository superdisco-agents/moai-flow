---
description: Load MoAI-ADK installation context and system overview
tags: [moai, context, primer]
---

# Prime: MoAI-ADK Installation Context Loader

Load comprehensive context about MoAI-ADK installation system, agents, and workflows.

## Progressive Disclosure Structure

### Level 1: Quick Overview (Show Immediately)

**MoAI-ADK Installation System**
- **What**: Automated installation framework for MoAI-ADK (26 AI agents)
- **Why**: Ensures reproducible, portable installation across environments
- **Where**: `/Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/`
- **How**: SPEC-First + TDD + Progressive Disclosure + Korean Support

**26 AI Agents Overview**:
- 5 Core Coordinators (hierarchical, mesh, adaptive, collective, memory)
- 6 Consensus Agents (Byzantine, Raft, gossip, CRDT, quorum, security)
- 4 Performance Agents (analyzer, benchmarker, orchestrator, smart)
- 5 Development Agents (coder, reviewer, tester, planner, researcher)
- 6 Specialized Agents (backend, mobile, ML, CI/CD, API docs, architect)

**Installation Approaches**:
1. Standard Installation (`/install`)
2. Korean Support Installation (`/install-korean`) ⭐
3. Validation & Testing (`/verify`)

### Level 2: System Architecture (Expand on Request)

**Directory Structure**:
```
moai-adk/
├── _config/install-moai-ko/          # Installation configurations
│   ├── .claude/                      # Claude Code integration
│   │   ├── commands/                 # 4 slash commands
│   │   ├── agents/                   # 2 specialized agents
│   │   └── settings.json             # Configuration registry
│   ├── pyproject.toml                # Python project config
│   └── uv.lock                       # Locked dependencies
├── src/moai_adk/                     # Core agent implementations
└── tests/                            # Test suites
```

**Technology Stack**:
- **Python**: 3.13+ (uv package manager)
- **Terminal**: Ghostty (Korean font support)
- **Fonts**: D2Coding, Noto Sans KR
- **AI Models**: Claude Sonnet 4.5, Haiku 4.5
- **Orchestration**: Claude Flow, beyond-MCP

### Level 3: Installation Workflows (Show on Demand)

**Standard Installation Workflow**:
1. System requirements check (Python, uv, Git)
2. Clone MoAI-ADK repository
3. Install dependencies (`uv sync`)
4. Verify 26 agents
5. Run portability tests

**Korean Support Workflow** (extends standard):
1. Install D2Coding font
2. Configure Ghostty terminal
3. Set Korean locale (ko_KR.UTF-8)
4. Test Korean rendering
5. Validate all 26 agents with Korean context

**Validation Workflow**:
1. Check Python environment
2. Verify agent availability
3. Test Korean fonts (if installed)
4. Run integration tests
5. Generate validation report

### Level 4: Commands & Agents Reference

**Slash Commands**:
- `/prime` - Load this context (current command)
- `/install` - Standard installation workflow
- `/install-korean` - Korean-enabled installation
- `/verify` - Validate installation completeness

**Specialized Agents**:
- `installer` (Sonnet 4.5) - Installation orchestration
- `validator` (Haiku 4.5) - Quality assurance & testing

### Level 5: Technical Details (Expert Mode)

**SPEC-First Methodology**:
```yaml
Phase 1: Specification
  - Define installation requirements
  - Document Korean support needs
  - Identify system dependencies

Phase 2: Pseudocode
  - Design installation algorithm
  - Plan error handling strategies
  - Structure validation logic

Phase 3: Architecture
  - Design agent coordination
  - Plan file organization
  - Define interfaces

Phase 4: Refinement (TDD)
  - Write installation tests
  - Implement workflows
  - Validate Korean support

Phase 5: Completion
  - Integration testing
  - Documentation generation
  - Release preparation
```

**Progressive Disclosure Pattern**:
- Commands provide graduated context depth
- Agents adapt to user expertise level
- Documentation scales from quick-start to deep-dive

**Korean Support Features**:
- D2Coding font (monospace, coding-optimized)
- Ghostty terminal configuration
- UTF-8 locale setup (ko_KR.UTF-8)
- Noto Sans KR for UI elements
- Korean error messages and logging

## Usage Examples

**Load context only**:
```bash
/prime
```

**Chain with installation**:
```bash
/prime && /install-korean
```

**Chain with validation**:
```bash
/prime && /verify
```

## Next Steps

After priming context:
1. Run `/install-korean` for full Korean setup
2. Run `/install` for standard setup
3. Run `/verify` to validate existing installation

---

**Context Loaded**: MoAI-ADK Installation System (26 agents, SPEC-First, Korean Support)
**Ready For**: Installation, Validation, Agent Development
