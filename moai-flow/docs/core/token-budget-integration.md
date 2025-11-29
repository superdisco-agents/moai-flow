# TokenBudget Integration Guide

> Per-swarm token allocation manager integrated with MoAI-ADK's JIT Context Loader

## Overview

TokenBudget provides per-swarm token allocation to prevent context window overflow (200K limit) while working with MoAI-ADK's existing JIT Context Loading System.

**Key Features**:
- 200,000 token global budget (from CLAUDE.md)
- Per-swarm allocation with custom limits
- Real-time consumption tracking
- Warning thresholds at 150K and 180K
- Integration with `.moai/config/config.json`
- Thread-safe operations

---

## Architecture

```
┌─────────────────────────────────────────────┐
│         Global Token Budget (200K)          │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────┐  ┌─────────────┐          │
│  │  Swarm A    │  │  Swarm B    │  ...     │
│  │  50K tokens │  │  40K tokens │          │
│  └─────────────┘  └─────────────┘          │
│       │                 │                   │
│       ▼                 ▼                   │
│  Consumption        Consumption             │
│  Tracking           Tracking                │
│       │                 │                   │
│       └─────────┬───────┘                   │
│                 ▼                           │
│       Global Usage Monitoring               │
│       (150K/180K thresholds)                │
└─────────────────────────────────────────────┘
```

---

## Quick Start

### Basic Usage

```python
from moai_flow.resource import TokenBudget

# Initialize with config
budget = TokenBudget(config_path=".moai/config/config.json")

# Allocate tokens to a swarm
budget.allocate_swarm("swarm-backend", 50000)

# Consume tokens during operations
budget.consume("swarm-backend", 5000)

# Check remaining balance
balance = budget.get_balance("swarm-backend")
print(f"Remaining: {balance} tokens")
```

### Convenience Functions

```python
from moai_flow.resource import (
    allocate_swarm,
    consume_tokens,
    get_swarm_balance,
    reset_swarm,
    get_budget_status
)

# Using global instance
allocate_swarm("swarm-testing", 30000)
consume_tokens("swarm-testing", 8000)
balance = get_swarm_balance("swarm-testing")

# Global status
status = get_budget_status()
print(f"Total consumed: {status['total_consumed']}")
```

---

## Integration with JIT Context Loader

TokenBudget complements MoAI-ADK's existing JIT Context Loader by adding per-swarm budget management:

### JIT Context Loader (Existing)

**Location**: `moai-adk/src/moai_adk/core/jit_context_loader.py`

**Responsibilities**:
- Phase-based context loading (SPEC, RED, GREEN, REFACTOR, SYNC, DEBUG, PLANNING)
- Skill filtering and selection
- Document loading and compression
- Token budget management per phase (30K-40K)

**Phase Budgets**:
```python
Phase.SPEC:      30,000 tokens
Phase.RED:       25,000 tokens
Phase.GREEN:     25,000 tokens
Phase.REFACTOR:  20,000 tokens
Phase.SYNC:      40,000 tokens
Phase.DEBUG:     15,000 tokens
Phase.PLANNING:  35,000 tokens
```

### TokenBudget (New)

**Location**: `moai-flow/resource/token_budget.py`

**Responsibilities**:
- Per-swarm token allocation across multiple agents
- Real-time consumption tracking
- Global threshold monitoring (150K/180K)
- Budget rebalancing and reset

**Swarm Budgets**:
```python
Default per-swarm:  50,000 tokens
Custom allocation:  Flexible (up to global limit)
Global budget:      200,000 tokens
Reserve buffer:     10,000 tokens
```

### Integration Pattern

```python
from moai_adk.core.jit_context_loader import JITContextLoader, Phase
from moai_flow.resource import TokenBudget

# Initialize both systems
jit_loader = JITContextLoader()
token_budget = TokenBudget()

# Allocate swarm budget
swarm_id = "swarm-implementation"
token_budget.allocate_swarm(swarm_id, 60000)

# Load context for specific phase
user_input = "/moai:2-run SPEC-001 RED"
context_data, metrics = await jit_loader.load_context(
    user_input=user_input,
    conversation_history=[],
    context={"spec_id": "SPEC-001"}
)

# Track token consumption
phase_tokens = metrics.token_count
if token_budget.consume(swarm_id, phase_tokens):
    print(f"Phase consumed {phase_tokens} tokens")

    # Check if warning needed
    should_warn, message = token_budget.should_warn(swarm_id)
    if should_warn:
        print(f"⚠️  {message}")
else:
    print(f"❌ Insufficient tokens for phase")
```

---

## Configuration

### Default Configuration

```python
BudgetConfig(
    total_budget=200000,        # Global 200K budget
    warning_threshold_1=150000, # First warning at 150K
    warning_threshold_2=180000, # Critical warning at 180K
    default_swarm_limit=50000,  # Default per-swarm allocation
    enable_auto_rebalance=True,
    enable_warnings=True,
    reserve_buffer=10000        # Reserve 10K for critical operations
)
```

### Custom Configuration via `.moai/config/config.json`

```json
{
  "token_budget": {
    "total_budget": 200000,
    "warning_threshold_1": 150000,
    "warning_threshold_2": 180000,
    "default_swarm_limit": 50000,
    "enable_auto_rebalance": true,
    "enable_warnings": true,
    "reserve_buffer": 10000
  }
}
```

---

## API Reference

### Core Methods

#### `allocate_swarm(swarm_id: str, token_limit: Optional[int] = None) -> bool`

Allocate tokens to a specific swarm.

**Parameters**:
- `swarm_id`: Unique identifier for the swarm
- `token_limit`: Custom token limit (uses default if None)

**Returns**: `True` if successful, `False` otherwise

**Example**:
```python
budget.allocate_swarm("swarm-backend", 50000)
budget.allocate_swarm("swarm-frontend")  # Uses default 50K
```

#### `consume(swarm_id: str, tokens: int) -> bool`

Track token consumption for a swarm.

**Parameters**:
- `swarm_id`: Swarm identifier
- `tokens`: Number of tokens to consume

**Returns**: `True` if allowed, `False` if exceeds budget

**Example**:
```python
if budget.consume("swarm-backend", 5000):
    print("Tokens consumed successfully")
```

#### `get_balance(swarm_id: str) -> int`

Get remaining token balance for a swarm.

**Returns**: Available tokens, or -1 if swarm not found

**Example**:
```python
balance = budget.get_balance("swarm-backend")
print(f"Remaining: {balance} tokens")
```

#### `get_usage_percent(swarm_id: str) -> float`

Calculate usage percentage for a swarm.

**Returns**: Usage percentage (0-100), or -1 if not found

**Example**:
```python
usage = budget.get_usage_percent("swarm-backend")
print(f"Usage: {usage:.1f}%")
```

#### `should_warn(swarm_id: str) -> Tuple[bool, Optional[str]]`

Check if swarm has exceeded warning thresholds.

**Returns**: Tuple of (should_warn, warning_message)

**Thresholds**:
- 75% usage: WARNING
- 90% usage: CRITICAL

**Example**:
```python
should_warn, message = budget.should_warn("swarm-backend")
if should_warn:
    print(f"⚠️  {message}")
```

#### `reset(swarm_id: str) -> bool`

Reset swarm budget (e.g., after `/clear` command).

**Returns**: `True` if successful

**Example**:
```python
# User executes /clear
budget.reset("swarm-backend")
```

#### `get_global_status() -> Dict`

Get comprehensive global status.

**Returns**: Dictionary with status information

**Example**:
```python
status = budget.get_global_status()
print(f"Total: {status['total_consumed']} / {status['total_budget']}")
print(f"Warning level: {status['warn_level']}")
```

### Advanced Methods

#### `reserve(swarm_id: str, tokens: int) -> bool`

Reserve tokens for planned operations.

#### `release_reservation(swarm_id: str, tokens: int) -> bool`

Release previously reserved tokens.

#### `rebalance() -> Dict[str, int]`

Rebalance token allocations across swarms.

#### `deallocate_swarm(swarm_id: str) -> bool`

Remove swarm allocation completely.

---

## Usage Scenarios

### Scenario 1: TDD Cycle Management

```python
budget = TokenBudget()
budget.allocate_swarm("swarm-tdd", 60000)

# RED Phase
budget.consume("swarm-tdd", 15000)  # Test creation

# GREEN Phase
budget.consume("swarm-tdd", 12000)  # Minimal implementation

# REFACTOR Phase
budget.consume("swarm-tdd", 10000)  # Code cleanup

# Check status
usage = budget.get_usage_percent("swarm-tdd")
print(f"TDD cycle used {usage:.1f}% of budget")
```

### Scenario 2: Multi-Swarm Coordination

```python
budget = TokenBudget()

# Allocate to multiple swarms
budget.allocate_swarm("swarm-backend", 50000)
budget.allocate_swarm("swarm-frontend", 40000)
budget.allocate_swarm("swarm-database", 30000)

# Track consumption across swarms
budget.consume("swarm-backend", 20000)
budget.consume("swarm-frontend", 15000)
budget.consume("swarm-database", 10000)

# Global monitoring
status = budget.get_global_status()
if status['warn_level'] != 'normal':
    print(f"⚠️  Global warning: {status['warn_level']}")
```

### Scenario 3: Context Reset After /clear

```python
budget = TokenBudget()
budget.allocate_swarm("swarm-session", 50000)

# Work during session
budget.consume("swarm-session", 30000)

# User executes /clear command
budget.reset("swarm-session")

# Continue with fresh budget
print(f"Available after reset: {budget.get_balance('swarm-session')}")
```

---

## Warning System

### Per-Swarm Warnings

| Threshold | Level    | Action                              |
|-----------|----------|-------------------------------------|
| 75%       | WARNING  | Log warning, notify user            |
| 90%       | CRITICAL | Log critical, suggest optimization  |

### Global Warnings

| Threshold | Level    | Recommendation                    |
|-----------|----------|-----------------------------------|
| 150K      | WARNING  | Monitor closely                   |
| 180K      | CRITICAL | Execute `/clear` recommended      |

**Example Warning Output**:
```
WARNING: Swarm swarm-backend at 76.3% token usage
CRITICAL: Swarm swarm-frontend at 91.2% token usage
CRITICAL: Global token usage at 182,000/200,000 (91.0%) - Execute /clear recommended
```

---

## Thread Safety

All TokenBudget operations are thread-safe using `threading.RLock`:

```python
# Safe for concurrent swarm operations
import threading

def worker(swarm_id, tokens):
    budget.consume(swarm_id, tokens)

threads = [
    threading.Thread(target=worker, args=("swarm-1", 1000)),
    threading.Thread(target=worker, args=("swarm-2", 1500)),
]

for t in threads:
    t.start()
for t in threads:
    t.join()
```

---

## Performance Considerations

### Memory Usage

- **SwarmAllocation**: ~200 bytes per swarm
- **Global instance**: ~2KB base overhead
- **History tracking**: Limited to last 50 entries

### CPU Impact

- Allocation/consumption: O(1)
- Global status: O(n) where n = number of swarms
- Rebalancing: O(n)

**Recommendation**: Limit to 10-20 active swarms per session.

---

## Testing

See `moai-flow/docs/examples/token_budget_usage.py` for comprehensive examples.

**Run examples**:
```bash
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk
python moai-flow/docs/examples/token_budget_usage.py
```

---

## Future Enhancements

1. **Persistence**: Save budget state to `.swarm/token_budget.json`
2. **Analytics**: Historical usage analysis and optimization recommendations
3. **Auto-scaling**: Dynamic allocation based on swarm workload
4. **Integration**: Direct hooks into Claude Code's token tracking API

---

## Related Documentation

- [MoAI-ADK JIT Context Loader](../../moai-adk/src/moai_adk/core/jit_context_loader.py)
- [PRD-02: Swarm Coordination](../../specs/PRD-02-swarm-coordination.md)
- [CLAUDE.md Token Management](../../CLAUDE.md#rule-4-token-management)

---

**Last Updated**: 2025-11-29
**Version**: 1.0.0
**Status**: Production Ready
