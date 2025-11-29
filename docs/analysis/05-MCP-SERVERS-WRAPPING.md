# MCP Servers Wrapping Method Analysis

**Document Version**: 1.0.0
**Last Updated**: 2025-11-28
**Analysis Scope**: 4 MCP Servers (context7, playwright, figma, sequential-thinking)
**Protocol**: JSON-RPC 2.0

---

## 1. Overview: MCP Server Architecture

### What is an MCP Server?

**MCP (Model Context Protocol) Server** is a standardized interface that wraps external tools/services into agent-accessible endpoints using JSON-RPC 2.0 protocol.

```
┌─────────────────────────────────────────────────────────────┐
│                      Agent Runtime (Claude)                  │
├─────────────────────────────────────────────────────────────┤
│  Tool Call Interface (MCP Client)                           │
│  ├─ JSON-RPC Request Builder                                │
│  ├─ Response Parser                                         │
│  └─ Error Handler                                           │
├─────────────────────────────────────────────────────────────┤
│                    JSON-RPC 2.0 Protocol                     │
│                    (stdio/HTTP transport)                    │
├─────────────────────────────────────────────────────────────┤
│  MCP Server (Tool Provider)                                 │
│  ├─ Method Registry (tools.list, tools.call)                │
│  ├─ State Management (optional)                             │
│  └─ External Service Wrapper                                │
├─────────────────────────────────────────────────────────────┤
│            External Services (APIs, CLIs, etc.)              │
└─────────────────────────────────────────────────────────────┘
```

**Key Characteristics**:
- **Protocol**: JSON-RPC 2.0 (stateless by default)
- **Transport**: stdio (local) or HTTP (remote)
- **Discovery**: `tools/list` method exposes available tools
- **Execution**: `tools/call` method invokes specific tool
- **State**: Optional session management via server-side context

---

## 2. MCP Server Catalog

| Server Name | Type | Primary Function | State Management | Transport |
|-------------|------|------------------|------------------|-----------|
| **context7** | Documentation | Fetches library docs from Context7 CDN | ✅ Stateful (library cache) | stdio |
| **playwright** | Browser Automation | Controls headless Chrome via CDP | ✅ Stateful (browser session) | stdio |
| **figma** | Design Tool | Accesses Figma API for design data | ❌ Stateless (token-based) | stdio |
| **sequential-thinking** | Cognitive Aid | Provides structured reasoning framework | ❌ Stateless (pure function) | stdio |

### Server Characteristics

#### context7
- **Purpose**: Resolve library names → fetch latest documentation
- **State**: Caches resolved library IDs to reduce CDN lookups
- **Key Tools**: `resolve-library-id`, `get-library-docs`
- **Pattern**: Two-phase fetch (resolve → retrieve)

#### playwright
- **Purpose**: Web scraping, UI testing, screenshot capture
- **State**: Maintains browser instance + page contexts across calls
- **Key Tools**: `navigate`, `screenshot`, `click`, `fill`
- **Pattern**: Session-based automation (init → actions → cleanup)

#### figma
- **Purpose**: Extract design tokens, components, frames from Figma files
- **State**: None (uses API token from environment)
- **Key Tools**: `get-file`, `get-components`, `get-styles`
- **Pattern**: RESTful API wrapper

#### sequential-thinking
- **Purpose**: Break complex problems into sequential thought steps
- **State**: None (pure reasoning tool)
- **Key Tools**: `sequentialthinking` (single recursive tool)
- **Pattern**: Chain-of-thought prompting aid

---

## 3. JSON-RPC 2.0 Mechanism

### Request Flow

```
Agent                MCP Server              External Service
  │                      │                          │
  │  tools/list         │                          │
  ├─────────────────────>│                          │
  │  {tools: [...]}     │                          │
  │<─────────────────────┤                          │
  │                      │                          │
  │  tools/call         │                          │
  │  {name, params}     │                          │
  ├─────────────────────>│                          │
  │                      │  API/CLI Call           │
  │                      ├─────────────────────────>│
  │                      │  Response               │
  │                      │<─────────────────────────┤
  │  {result}           │                          │
  │<─────────────────────┤                          │
  │                      │                          │
```

### Message Format

**Request** (from agent):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "mcp__context7__get-library-docs",
    "arguments": {
      "context7CompatibleLibraryID": "/vercel/next.js",
      "tokens": 5000
    }
  }
}
```

**Response** (from server):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "# Next.js Documentation\n..."
      }
    ]
  }
}
```

**Error** (on failure):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Invalid library ID format"
  }
}
```

---

## 4. Tool Design Principles (Agent-Centric)

### Principle 1: **Single Responsibility**
Each tool performs ONE well-defined action.

❌ **Bad**: `mcp__figma__do-everything`
✅ **Good**: `mcp__figma__get-file`, `mcp__figma__get-components`

### Principle 2: **Parameter Validation**
Use JSON Schema to enforce required fields and types.

```typescript
// playwright navigate tool
{
  "name": "navigate",
  "inputSchema": {
    "type": "object",
    "properties": {
      "url": { "type": "string", "format": "uri" }
    },
    "required": ["url"]
  }
}
```

### Principle 3: **Descriptive Naming**
Tool names should indicate action + target.

- `get-library-docs` (context7)
- `screenshot` (playwright)
- `get-components` (figma)
- `sequentialthinking` (sequential-thinking)

### Principle 4: **Structured Output**
Return consistent formats (JSON, Markdown, base64).

```json
// playwright screenshot returns base64 image
{
  "type": "image",
  "data": "iVBORw0KGgoAAAANSUhEUgAA...",
  "mimeType": "image/png"
}
```

### Principle 5: **Error Context**
Include actionable error messages.

❌ **Bad**: `"Error: Failed"`
✅ **Good**: `"Error: Library '/invalid/path' not found. Use resolve-library-id first."`

---

## 5. Stateful Implementation Pattern

### Pattern: Session-Based Browser Automation (playwright)

```typescript
// Server maintains global state
class PlaywrightServer {
  private browser: Browser | null = null;
  private page: Page | null = null;

  async initialize() {
    this.browser = await chromium.launch({ headless: true });
    this.page = await this.browser.newPage();
  }

  async handleNavigate(url: string) {
    if (!this.page) await this.initialize();
    await this.page.goto(url);
    return { status: 'success', url };
  }

  async handleScreenshot() {
    if (!this.page) throw new Error('No active page');
    const buffer = await this.page.screenshot();
    return { type: 'image', data: buffer.toString('base64') };
  }

  async cleanup() {
    await this.browser?.close();
    this.browser = null;
    this.page = null;
  }
}
```

**Key Characteristics**:
- State persists across tool calls within same session
- Lifecycle: `initialize()` → `handleX()` → `cleanup()`
- Error handling: Check state before operations

### Pattern: Cache-Based Resolution (context7)

```typescript
class Context7Server {
  private libraryCache = new Map<string, string>();

  async resolveLibrary(name: string): Promise<string> {
    if (this.libraryCache.has(name)) {
      return this.libraryCache.get(name)!;
    }

    const id = await fetchFromCDN(name);
    this.libraryCache.set(name, id);
    return id;
  }

  async getDocs(libraryID: string, tokens: number) {
    const docs = await fetchDocs(libraryID, tokens);
    return { content: [{ type: 'text', text: docs }] };
  }
}
```

**Key Characteristics**:
- State = performance optimization (not session state)
- Cache invalidation: TTL or manual clear
- Transparent to agent (cache hits are invisible)

---

## 6. Best Practices

### 1. **Implement Idempotency**
Repeated calls with same params should produce same result.

```typescript
// ✅ Good: sequential-thinking (pure function)
function sequentialThinking(thought: string, step: number) {
  return { thought, step, timestamp: Date.now() };
}
```

### 2. **Handle Timeouts Gracefully**
Long-running operations should support cancellation.

```typescript
// playwright with timeout
async navigate(url: string, timeout = 30000) {
  await this.page.goto(url, { timeout });
}
```

### 3. **Validate Early**
Reject invalid inputs before expensive operations.

```typescript
// context7 library ID validation
if (!libraryID.match(/^\/[a-z0-9-]+\/[a-z0-9-]+$/)) {
  throw new Error('Invalid library ID format');
}
```

### 4. **Support Partial Results**
For large datasets, allow pagination/chunking.

```typescript
// context7 token limit
async getDocs(libraryID: string, tokens = 5000) {
  const fullDocs = await fetchDocs(libraryID);
  return truncate(fullDocs, tokens);
}
```

### 5. **Clean Up Resources**
Implement graceful shutdown for stateful servers.

```typescript
// playwright cleanup on exit
process.on('SIGTERM', async () => {
  await server.cleanup();
  process.exit(0);
});
```

### 6. **Version Tools Explicitly**
Include version in tool metadata for compatibility.

```json
{
  "name": "mcp__playwright__screenshot",
  "version": "1.2.0",
  "description": "Capture page screenshot (requires playwright@1.40+)"
}
```

---

## Real-World Integration Patterns

### Pattern A: Two-Phase Fetch (context7)
```
Agent: "Get Next.js documentation"
  ↓
1. resolve-library-id("Next.js") → "/vercel/next.js"
2. get-library-docs("/vercel/next.js", 5000) → docs
```

### Pattern B: Session Automation (playwright)
```
Agent: "Screenshot example.com's login page"
  ↓
1. navigate("https://example.com") → success
2. fill("#username", "demo") → success
3. screenshot() → base64 PNG
```

### Pattern C: Stateless API Wrapper (figma)
```
Agent: "Get Figma file components"
  ↓
1. get-file(fileKey) → file metadata
2. get-components(fileKey) → component list
```

### Pattern D: Pure Reasoning Aid (sequential-thinking)
```
Agent: "Think through API design"
  ↓
1. sequentialthinking("Consider REST vs GraphQL", step=1)
2. sequentialthinking("Evaluate trade-offs", step=2)
3. sequentialthinking("Choose GraphQL for flexibility", step=3)
```

---

## Stateful vs Stateless Comparison

| Aspect | Stateful (playwright) | Stateless (figma) |
|--------|----------------------|-------------------|
| **Complexity** | High (session management) | Low (pure wrapper) |
| **Performance** | Better (reuses browser) | Slower (new request each call) |
| **Reliability** | Lower (state corruption risk) | Higher (no shared state) |
| **Scalability** | Limited (session limits) | Unlimited (horizontal scaling) |
| **Use Case** | Interactive workflows | Independent queries |

---

## Conclusion

**MCP servers wrap external tools using JSON-RPC 2.0, following agent-centric design principles:**

1. **Protocol**: Standardized JSON-RPC 2.0 for tool discovery/execution
2. **State Management**: Choose stateful (sessions) vs stateless (pure functions) based on use case
3. **Tool Design**: Single responsibility + parameter validation + descriptive naming
4. **Error Handling**: Validate early, provide context, clean up resources
5. **Real-World Patterns**: Two-phase fetch, session automation, API wrappers, reasoning aids

**Key Takeaway**: MCP servers transform any external service into agent-accessible tools by implementing a minimal JSON-RPC interface with clear tool contracts and proper state management.

---

**End of Analysis** | Token Count: ~5,850 tokens