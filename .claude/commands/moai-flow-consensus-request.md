---
name: moai-flow-consensus-request
description: Request consensus decision from moai-flow swarm agents
type: prompt
---

# /moai-flow-consensus-request

Request consensus decision from moai-flow swarm agents.

## Usage

```
/moai-flow-consensus-request "<proposal>" [timeout]
```

## Parameters

- `proposal` (required): Proposal description for consensus
- `timeout` (optional): Timeout in milliseconds. Default: 5000

## Examples

```
/moai-flow-consensus-request "Approve deployment to production"
/moai-flow-consensus-request "Select optimization strategy" 10000
```

## Behavior

1. Validate swarm session is active
2. Broadcast proposal to all agents
3. Collect votes within timeout period
4. Apply consensus algorithm
5. Return agreed result or timeout error

## Output

Returns consensus result including:
- Decision (approved/rejected/timeout)
- Vote breakdown (yes/no/abstain counts)
- Participating agents
- Consensus duration
- Any dissenting opinions
