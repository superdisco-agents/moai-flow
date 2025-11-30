# /swarm-init

Initialize a new moai-flow swarm session with specified topology and configuration.

## Usage

```
/swarm-init [topology] [agent_count]
```

## Parameters

- `topology` (optional): Topology type (hierarchical, mesh, star, ring, adaptive). Default: adaptive
- `agent_count` (optional): Number of agents. Default: 3

## Examples

```
/swarm-init
/swarm-init mesh 5
/swarm-init hierarchical
```

## Behavior

1. Initialize SwarmCoordinator with specified topology
2. Create agent pool with requested count
3. Set up coordination protocols
4. Initialize shared memory
5. Report swarm session ID and status

## Output

Returns swarm session details including:
- Session ID
- Topology configuration
- Active agents count
- Coordination state
