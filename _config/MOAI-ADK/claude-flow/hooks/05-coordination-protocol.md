# Coordination Protocol Hooks

> Multi-agent coordination and swarm event hooks

## Overview

Coordination hooks manage events in multi-agent scenarios, handling consensus, conflicts, heartbeats, and swarm state changes. **This is a major gap in MoAI** as it currently lacks multi-agent coordination.

---

## Hook Categories

### 1. Consensus Hooks

Handle agreement events between agents.

| Hook | Trigger | Purpose |
|------|---------|---------|
| `OnConsensusStart` | Consensus process begins | Setup voting |
| `OnConsensusVote` | Agent votes | Record vote |
| `OnConsensusReached` | Agreement achieved | Apply decision |
| `OnConsensusFailed` | No agreement | Escalate or retry |

### 2. Conflict Hooks

Handle disagreements and conflicts.

| Hook | Trigger | Purpose |
|------|---------|---------|
| `OnConflictDetected` | Conflict found | Alert, log |
| `OnConflictResolution` | Resolution attempt | Apply strategy |
| `OnConflictResolved` | Conflict resolved | Record resolution |
| `OnConflictEscalated` | Cannot resolve | Human intervention |

### 3. Heartbeat Hooks

Monitor agent health.

| Hook | Trigger | Purpose |
|------|---------|---------|
| `OnHeartbeat` | Regular interval | Health check |
| `OnHeartbeatMissed` | Agent unresponsive | Alert, retry |
| `OnAgentTimeout` | Agent failed | Cleanup, reassign |

### 4. Swarm State Hooks

Manage swarm lifecycle.

| Hook | Trigger | Purpose |
|------|---------|---------|
| `OnSwarmInit` | Swarm initialized | Setup coordination |
| `OnAgentJoin` | Agent joins swarm | Update topology |
| `OnAgentLeave` | Agent leaves swarm | Reassign tasks |
| `OnSwarmShutdown` | Swarm terminates | Cleanup all |

---

## Implementation Patterns

### Pattern 1: Consensus Hook

```bash
#!/bin/bash
# on-consensus-reached.sh

CONSENSUS_ID="$1"
DECISION="$2"
VOTERS="$3"
VOTE_COUNT="$4"

# Log consensus
LOG_FILE=".moai/logs/consensus.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "{\"timestamp\":\"$TIMESTAMP\",\"consensus_id\":\"$CONSENSUS_ID\",\"decision\":\"$DECISION\",\"voters\":$VOTERS,\"vote_count\":$VOTE_COUNT}" >> "$LOG_FILE"

# Apply decision
case "$DECISION" in
    "approve_merge")
        echo "Applying merge decision..."
        # Trigger merge workflow
        ;;
    "reject_change")
        echo "Change rejected by consensus..."
        # Notify requester
        ;;
    "escalate")
        echo "Escalating to human review..."
        # Create issue/notification
        ;;
esac

exit 0
```

### Pattern 2: Conflict Resolution Hook

```bash
#!/bin/bash
# on-conflict-detected.sh

CONFLICT_ID="$1"
CONFLICT_TYPE="$2"
AGENT_A="$3"
AGENT_B="$4"
RESOURCE="$5"

# Log conflict
LOG_FILE=".moai/logs/conflicts.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "{\"timestamp\":\"$TIMESTAMP\",\"conflict_id\":\"$CONFLICT_ID\",\"type\":\"$CONFLICT_TYPE\",\"agents\":[\"$AGENT_A\",\"$AGENT_B\"],\"resource\":\"$RESOURCE\"}" >> "$LOG_FILE"

# Apply resolution strategy based on conflict type
case "$CONFLICT_TYPE" in
    "file_edit")
        # Priority-based resolution
        echo "Applying priority-based resolution"
        ;;
    "resource_claim")
        # First-come-first-served
        echo "Applying FCFS resolution"
        ;;
    "decision_conflict")
        # Voting-based resolution
        echo "Initiating consensus vote"
        ;;
    *)
        # Escalate unknown conflicts
        echo "Escalating to coordinator"
        exit 2
        ;;
esac

exit 0
```

### Pattern 3: Heartbeat Monitor Hook

```bash
#!/bin/bash
# on-heartbeat-missed.sh

AGENT_ID="$1"
MISSED_COUNT="$2"
LAST_SEEN="$3"

# Log missed heartbeat
LOG_FILE=".moai/logs/heartbeats.log"
echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") MISSED: $AGENT_ID count=$MISSED_COUNT last=$LAST_SEEN" >> "$LOG_FILE"

# Take action based on missed count
if [[ $MISSED_COUNT -ge 3 ]]; then
    echo "Agent $AGENT_ID unresponsive - initiating recovery"

    # Try to recover agent
    RECOVERY_RESULT=$(attempt_agent_recovery "$AGENT_ID")

    if [[ $RECOVERY_RESULT == "failed" ]]; then
        echo "Recovery failed - reassigning tasks"

        # Get agent's pending tasks
        PENDING_TASKS=$(get_agent_tasks "$AGENT_ID")

        # Reassign to available agents
        for task in $PENDING_TASKS; do
            reassign_task "$task"
        done

        # Mark agent as dead
        mark_agent_dead "$AGENT_ID"
    fi
elif [[ $MISSED_COUNT -ge 1 ]]; then
    echo "Agent $AGENT_ID slow - monitoring"
fi

exit 0
```

### Pattern 4: Swarm State Hook

```bash
#!/bin/bash
# on-agent-join.sh

SWARM_ID="$1"
AGENT_ID="$2"
AGENT_TYPE="$3"
TOPOLOGY="$4"

# Update swarm registry
REGISTRY=".moai/cache/swarm-registry.json"

if [[ ! -f "$REGISTRY" ]]; then
    echo '{"swarms":{}}' > "$REGISTRY"
fi

# Add agent to swarm
jq ".swarms[\"$SWARM_ID\"].agents += [{\"id\":\"$AGENT_ID\",\"type\":\"$AGENT_TYPE\",\"joined\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"}]" "$REGISTRY" > "${REGISTRY}.tmp"
mv "${REGISTRY}.tmp" "$REGISTRY"

# Update topology if needed
case "$TOPOLOGY" in
    "mesh")
        # Connect new agent to all existing agents
        echo "Establishing mesh connections for $AGENT_ID"
        ;;
    "hierarchical")
        # Connect to parent node
        echo "Connecting $AGENT_ID to hierarchy"
        ;;
    "ring")
        # Insert into ring
        echo "Inserting $AGENT_ID into ring"
        ;;
esac

# Notify existing agents
EXISTING_AGENTS=$(jq -r ".swarms[\"$SWARM_ID\"].agents[].id" "$REGISTRY" | grep -v "$AGENT_ID")
for agent in $EXISTING_AGENTS; do
    notify_agent "$agent" "new_peer" "$AGENT_ID"
done

echo "Agent $AGENT_ID joined swarm $SWARM_ID"
exit 0
```

---

## Coordination Protocol Flow

```
┌─────────────────────────────────────────────────────────┐
│                 COORDINATION PROTOCOL                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   Agent A   │    │   Agent B   │    │   Agent C   │ │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘ │
│         │                  │                  │         │
│         │◄────Heartbeat───►│◄────Heartbeat───►│         │
│         │                  │                  │         │
│         └────────┬─────────┴─────────┬────────┘         │
│                  │                   │                   │
│                  ▼                   ▼                   │
│         ┌────────────────────────────────────┐          │
│         │        COORDINATION LAYER          │          │
│         ├────────────────────────────────────┤          │
│         │  • Consensus Management            │          │
│         │  • Conflict Resolution             │          │
│         │  • Health Monitoring               │          │
│         │  • Topology Management             │          │
│         └────────────────────────────────────┘          │
│                                                          │
│  Events:                                                │
│  ├── OnConsensusReached → Apply decision                │
│  ├── OnConflictDetected → Resolve conflict              │
│  ├── OnHeartbeatMissed  → Recovery/reassign             │
│  └── OnAgentJoin/Leave  → Update topology               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## MoAI Gap Analysis

### Current State: No Coordination Hooks

MoAI currently has:
- Single-agent execution via Task()
- No multi-agent coordination
- No consensus mechanisms
- No conflict resolution
- No swarm topology

### Gap Table

| Coordination Hook | Claude-Flow | MoAI |
|-------------------|-------------|------|
| OnConsensusStart | Yes | No |
| OnConsensusReached | Yes | No |
| OnConflictDetected | Yes | No |
| OnConflictResolved | Yes | No |
| OnHeartbeat | Yes | No |
| OnHeartbeatMissed | Yes | No |
| OnSwarmInit | Yes | No |
| OnAgentJoin | Yes | No |
| OnAgentLeave | Yes | No |
| OnSwarmShutdown | Yes | No |

---

## Recommendation

### Priority: P2 (Medium-term)

Coordination hooks require swarm infrastructure first.

### Phase 1: Foundation

Add basic coordination hooks (without swarm):

```json
{
  "hooks": {
    "OnAgentStart": {
      "enabled": true,
      "command": ".moai/hooks/on-agent-start.sh"
    },
    "OnAgentEnd": {
      "enabled": true,
      "command": ".moai/hooks/on-agent-end.sh"
    }
  }
}
```

### Phase 2: Swarm Support

After implementing swarm infrastructure:

```json
{
  "hooks": {
    "coordination": {
      "consensus": {
        "OnConsensusReached": { "enabled": true },
        "OnConsensusFailed": { "enabled": true }
      },
      "conflict": {
        "OnConflictDetected": { "enabled": true },
        "OnConflictResolved": { "enabled": true }
      },
      "health": {
        "OnHeartbeat": { "enabled": true, "interval_ms": 5000 },
        "OnHeartbeatMissed": { "enabled": true, "threshold": 3 }
      }
    }
  }
}
```

### Benefits of Adding Coordination Hooks

1. **Reliability**: Automatic recovery from agent failures
2. **Consistency**: Consensus-based decisions
3. **Scalability**: Support for larger agent teams
4. **Observability**: Full visibility into multi-agent operations
