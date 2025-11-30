---
name: moai-flow-topology-switch
description: Switch moai-flow swarm topology dynamically while preserving state
type: prompt
---

# /moai-flow-topology-switch

Switch moai-flow swarm topology dynamically while preserving state.

## Usage

```
/moai-flow-topology-switch <new_topology>
```

## Parameters

- `new_topology` (required): Target topology (hierarchical, mesh, star, ring, adaptive)

## Examples

```
/moai-flow-topology-switch mesh
/moai-flow-topology-switch adaptive
```

## Behavior

1. Validate current swarm session exists
2. Validate target topology is different from current
3. Preserve agent states and pending tasks
4. Transition to new topology
5. Restore coordination protocols
6. Report transition success

## Output

Returns transition report including:
- Previous topology
- New topology
- Transition duration
- Agent migration status
- Any warnings or errors
