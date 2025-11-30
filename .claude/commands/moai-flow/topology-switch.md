# /topology-switch

Switch moai-flow swarm topology dynamically while preserving state.

## Usage

```
/topology-switch <new_topology>
```

## Parameters

- `new_topology` (required): Target topology (hierarchical, mesh, star, ring, adaptive)

## Examples

```
/topology-switch mesh
/topology-switch adaptive
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
