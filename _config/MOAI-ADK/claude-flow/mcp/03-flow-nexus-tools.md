# Flow-Nexus MCP Tools

> 70+ cloud-based orchestration tools (Advanced Features)

## Overview

Flow-Nexus is Claude-Flow's cloud platform providing 70+ advanced MCP tools. These are **optional** features requiring registration.

---

## Registration Required

```bash
# Register for Flow-Nexus
npx flow-nexus@latest register

# Login
npx flow-nexus@latest login

# Or via MCP
mcp__flow-nexus__user_register
mcp__flow-nexus__user_login
```

---

## Tool Categories

### 1. Swarm & Agents (Enhanced)

| Tool | Purpose |
|------|---------|
| `swarm_init` | Initialize cloud swarm |
| `swarm_scale` | Auto-scale agents |
| `agent_spawn` | Cloud agent spawning |
| `task_orchestrate` | Cloud orchestration |

### 2. Sandboxes (Cloud Execution)

| Tool | Purpose |
|------|---------|
| `sandbox_create` | Create isolated sandbox |
| `sandbox_execute` | Run code in sandbox |
| `sandbox_upload` | Upload files to sandbox |
| `sandbox_list` | List sandboxes |
| `sandbox_delete` | Remove sandbox |

### Use Case
Run untrusted or experimental code in isolated cloud environments.

### 3. Templates

| Tool | Purpose |
|------|---------|
| `template_list` | List available templates |
| `template_deploy` | Deploy project template |
| `template_create` | Create new template |

### Available Templates
- React/Next.js starters
- API boilerplates
- Full-stack scaffolds
- ML project templates

### 4. Neural AI (Advanced)

| Tool | Purpose |
|------|---------|
| `neural_train` | Cloud neural training |
| `neural_patterns` | Pattern management |
| `seraphina_chat` | AI assistant chat |

### 5. GitHub (Enhanced)

| Tool | Purpose |
|------|---------|
| `github_repo_analyze` | Deep repository analysis |
| `github_pr_manage` | Advanced PR management |
| `github_workflow_optimize` | Optimize GitHub Actions |

### 6. Real-time

| Tool | Purpose |
|------|---------|
| `execution_stream_subscribe` | Stream execution logs |
| `realtime_subscribe` | Live monitoring |
| `websocket_connect` | Real-time connection |

### 7. Storage

| Tool | Purpose |
|------|---------|
| `storage_upload` | Upload to cloud |
| `storage_list` | List cloud files |
| `storage_download` | Download from cloud |
| `storage_delete` | Remove cloud files |

---

## Platform Features

| Feature | Description |
|---------|-------------|
| **Cloud Execution** | Run agents in cloud |
| **Sandboxed Environments** | Isolated execution |
| **Persistent Storage** | Cloud file storage |
| **Real-time Monitoring** | Live execution streams |
| **Neural Training** | Cloud-based ML |
| **Templates** | Pre-built projects |

---

## MoAI Comparison

### MoAI Has
- Local execution only
- No cloud sandboxes
- No cloud storage
- No templates system
- No neural training

### Flow-Nexus Advantages
1. Cloud-based agent execution
2. Sandboxed code execution
3. Pre-built templates
4. Real-time monitoring
5. Cloud storage

### MoAI Advantages
1. No registration required
2. No cloud dependency
3. Local-first architecture
4. Works offline
5. No additional costs

---

## Integration Consideration

### If Adding Flow-Nexus to MoAI

```json
{
  "flow-nexus": {
    "command": "npx",
    "args": ["flow-nexus@latest", "mcp", "start"],
    "env": {
      "FLOW_NEXUS_TOKEN": "${FLOW_NEXUS_TOKEN}"
    }
  }
}
```

### Trade-offs

| Aspect | With Flow-Nexus | Without |
|--------|-----------------|---------|
| Cloud Features | Yes | No |
| Offline Work | Limited | Full |
| Cost | May have fees | Free |
| Dependency | External service | Self-contained |
| Sandboxing | Cloud sandboxes | Local only |

---

## Recommendation

### For MoAI

**Priority: LOW (P3)**

Flow-Nexus provides advanced features but adds:
- External dependency
- Registration requirement
- Potential costs
- Cloud reliance

Consider only if:
1. Cloud execution is critical
2. Sandboxing is required
3. Templates would accelerate development

### Alternative

Build local equivalents:
1. Local sandboxing with Docker
2. Local templates with `builder-*` agents
3. Local storage with `.moai/` hierarchy

---

## Summary

Flow-Nexus is a powerful cloud extension but requires careful consideration of trade-offs. MoAI's local-first approach has different strengths. Integration is optional based on specific needs.
