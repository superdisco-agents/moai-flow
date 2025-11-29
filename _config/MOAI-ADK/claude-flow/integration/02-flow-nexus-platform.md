# Flow-Nexus Platform

> Cloud-based orchestration and execution platform

## Overview

Flow-Nexus is Claude-Flow's cloud platform providing 70+ advanced MCP tools. It offers sandboxed execution, templates, cloud storage, and more. **This is optional for MoAI** and requires registration.

---

## Platform Features

### 1. Cloud Execution

Run agents in isolated cloud environments:

```javascript
mcp__flow-nexus__sandbox_create {
  type: "python",
  resources: {
    memory: "2GB",
    cpu: 2,
    timeout_minutes: 30
  }
}

mcp__flow-nexus__sandbox_execute {
  sandboxId: "sb-123",
  code: "print('Hello from cloud!')",
  language: "python"
}
```

### 2. Sandbox Features

| Feature | Description |
|---------|-------------|
| Isolation | Complete environment isolation |
| Languages | Python, Node.js, Go, Rust, etc. |
| Dependencies | Install any packages |
| Persistence | Save state between runs |
| Networking | Controlled outbound access |

### 3. Templates

Pre-built project scaffolds:

```javascript
mcp__flow-nexus__template_list {
  category: "fullstack"
}

// Available templates:
// - react-nextjs-starter
// - fastapi-backend
// - flask-ml-api
// - express-graphql
// - rust-axum-api
// - go-gin-rest
```

### 4. Cloud Storage

```javascript
mcp__flow-nexus__storage_upload {
  path: "project/results.json",
  content: { ... },
  ttl_days: 30
}

mcp__flow-nexus__storage_list {
  prefix: "project/"
}
```

### 5. Real-time Streaming

```javascript
mcp__flow-nexus__execution_stream_subscribe {
  executionId: "exec-456"
}

// Streams execution logs in real-time
```

---

## Tool Categories

### User Management

```javascript
mcp__flow-nexus__user_register { email, password }
mcp__flow-nexus__user_login { email, password }
mcp__flow-nexus__user_profile {}
mcp__flow-nexus__user_usage {}
```

### Sandbox Management

```javascript
mcp__flow-nexus__sandbox_create { type, resources }
mcp__flow-nexus__sandbox_execute { sandboxId, code }
mcp__flow-nexus__sandbox_upload { sandboxId, files }
mcp__flow-nexus__sandbox_list {}
mcp__flow-nexus__sandbox_delete { sandboxId }
```

### Storage

```javascript
mcp__flow-nexus__storage_upload { path, content }
mcp__flow-nexus__storage_download { path }
mcp__flow-nexus__storage_list { prefix }
mcp__flow-nexus__storage_delete { path }
```

### Templates

```javascript
mcp__flow-nexus__template_list { category }
mcp__flow-nexus__template_deploy { template, config }
mcp__flow-nexus__template_create { name, files }
```

### Neural/AI

```javascript
mcp__flow-nexus__neural_train { patterns, config }
mcp__flow-nexus__neural_patterns { filter }
mcp__flow-nexus__seraphina_chat { message }
```

### Real-time

```javascript
mcp__flow-nexus__execution_stream_subscribe { executionId }
mcp__flow-nexus__realtime_subscribe { channel }
mcp__flow-nexus__websocket_connect { endpoint }
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  FLOW-NEXUS PLATFORM                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │ Claude  │  │ Claude  │  │ Claude  │  │ Claude  │   │
│  │ Code 1  │  │ Code 2  │  │ Code 3  │  │ Code N  │   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │
│       │            │            │            │         │
│       └────────────┴─────┬──────┴────────────┘         │
│                          │                              │
│                    ┌─────▼─────┐                        │
│                    │    MCP    │                        │
│                    │  Gateway  │                        │
│                    └─────┬─────┘                        │
│                          │                              │
│     ┌───────────────────┼───────────────────┐          │
│     │                   │                   │          │
│  ┌──▼──┐          ┌─────▼─────┐         ┌──▼──┐       │
│  │Sand-│          │   Cloud   │         │Temp-│       │
│  │boxes│          │  Storage  │         │lates│       │
│  └─────┘          └───────────┘         └─────┘       │
│                                                         │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐        │
│  │ Neural  │      │Real-time│      │  User   │        │
│  │Training │      │Streaming│      │  Mgmt   │        │
│  └─────────┘      └─────────┘      └─────────┘        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## MoAI Comparison

### MoAI Current State

MoAI is entirely local-first:

```
┌─────────────────────────────────────────────────────────┐
│                    MOAI (LOCAL)                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ✅ Local execution                                     │
│  ✅ No registration required                            │
│  ✅ Works offline                                       │
│  ✅ No cloud dependency                                 │
│  ✅ No additional costs                                 │
│  ✅ Full privacy                                        │
│                                                         │
│  ❌ No cloud sandboxes                                  │
│  ❌ No cloud storage                                    │
│  ❌ No templates system                                 │
│  ❌ No neural training cloud                            │
│  ❌ No real-time streaming                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Feature Comparison

| Feature | Flow-Nexus | MoAI |
|---------|------------|------|
| Execution | Cloud + Local | Local only |
| Sandboxes | Yes | No |
| Storage | Cloud | Local |
| Templates | 50+ | None |
| Neural Cloud | Yes | No |
| Registration | Required | Not needed |
| Cost | May have fees | Free |
| Offline | No | Yes |
| Privacy | Cloud | Full local |

---

## Integration Options

### Option 1: Add Flow-Nexus MCP

If cloud features needed:

```json
{
  "mcpServers": {
    "flow-nexus": {
      "command": "npx",
      "args": ["flow-nexus@latest", "mcp", "start"],
      "env": {
        "FLOW_NEXUS_TOKEN": "${FLOW_NEXUS_TOKEN}"
      }
    }
  }
}
```

### Option 2: Build Local Alternatives

Create local equivalents:

| Flow-Nexus | MoAI Local Alternative |
|------------|------------------------|
| Sandboxes | Docker containers |
| Templates | `builder-*` agents |
| Storage | `.moai/` directory |
| Streaming | Local logging |

### Option 3: Hybrid Approach

- Use MoAI for most work (local)
- Use Flow-Nexus for specific cloud needs
- Best of both worlds

---

## Local Alternatives for MoAI

### Sandboxes → Docker

```json
{
  "sandboxing": {
    "provider": "docker",
    "default_image": "python:3.11",
    "memory_limit": "2g",
    "cpu_limit": 2,
    "timeout_seconds": 1800
  }
}
```

```bash
# MoAI sandbox command
docker run --rm -it \
  -v $(pwd):/workspace \
  -m 2g \
  --cpus 2 \
  python:3.11 \
  python /workspace/script.py
```

### Templates → Builder Agents

```yaml
# builder-scaffold agent
name: builder-scaffold
description: Create project scaffolds

templates:
  - fastapi-basic
  - react-nextjs
  - flask-ml

usage:
  Task(subagent_type="builder-scaffold",
       prompt="Create FastAPI project for user API")
```

### Storage → Local Files

MoAI already has organized storage:

```
.moai/
├── memory/        # Persistent state
├── cache/         # Temporary cache
├── reports/       # Analysis reports
├── specs/         # SPEC documents
└── backups/       # Backups
```

### Streaming → Local Logs

```json
{
  "logging": {
    "execution_logs": {
      "enabled": true,
      "location": ".moai/logs/execution/",
      "stream_to_console": true,
      "retain_days": 7
    }
  }
}
```

---

## Recommendation

### Priority: P3 (Low)

Flow-Nexus is optional for most use cases.

### When to Use Flow-Nexus

Consider adding if you need:
1. **Sandboxed execution** for untrusted code
2. **Cloud collaboration** across machines
3. **Pre-built templates** for rapid prototyping
4. **Real-time streaming** for remote monitoring

### When to Stay Local

Keep MoAI local-only if:
1. **Privacy** is critical
2. **Offline work** is common
3. **Cost** is a concern
4. **Local Docker** can provide sandboxing

### MoAI Philosophy Alignment

MoAI's local-first approach aligns with:
- Zero external dependencies
- Full offline capability
- No registration requirements
- Complete privacy
- No cloud costs

---

## Trade-offs Summary

| Aspect | With Flow-Nexus | Without (Local) |
|--------|-----------------|-----------------|
| **Sandboxing** | Cloud sandboxes | Docker (setup needed) |
| **Templates** | 50+ ready | Build with agents |
| **Storage** | Cloud shared | Local only |
| **Collaboration** | Yes | Git-based |
| **Offline** | Limited | Full |
| **Privacy** | Cloud | Complete |
| **Cost** | Potential fees | Free |
| **Setup** | Registration | None |

---

## Summary

Flow-Nexus provides powerful cloud features that extend Claude-Flow's capabilities. However, MoAI's local-first architecture has its own strengths. For most development workflows, MoAI's local approach is sufficient. Flow-Nexus integration should be considered only for specific cloud needs like sandboxed execution of untrusted code or cloud collaboration. Local alternatives (Docker, builder agents, local storage) can address most needs without external dependencies.
