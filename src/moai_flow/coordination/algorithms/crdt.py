"""
Conflict-Free Replicated Data Types (CRDTs) for distributed coordination.

CRDTs are data structures that guarantee eventual consistency without requiring
coordination between replicas. They achieve this through commutative, associative,
and idempotent merge operations.

This module provides four essential CRDT implementations:
- GCounter: Grow-only counter (increment only)
- PNCounter: Positive-negative counter (increment and decrement)
- LWWRegister: Last-write-wins register (single value with timestamp)
- ORSet: Observed-remove set (add and remove elements)

All CRDTs follow these properties:
1. Commutativity: A.merge(B) == B.merge(A)
2. Associativity: (A.merge(B)).merge(C) == A.merge(B.merge(C))
3. Idempotency: A.merge(A) == A
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Set, TypeVar
import time
import uuid


T = TypeVar('T')


class CRDT(ABC):
    """Base class for all CRDT implementations."""

    @abstractmethod
    def merge(self, other: "CRDT") -> "CRDT":
        """
        Merge another CRDT into this one.

        Must satisfy:
        - Commutativity: A.merge(B) == B.merge(A)
        - Associativity: (A.merge(B)).merge(C) == A.merge(B.merge(C))
        - Idempotency: A.merge(A) == A

        Args:
            other: Another CRDT of the same type

        Returns:
            New merged CRDT
        """
        pass


@dataclass
class GCounter(CRDT):
    """
    Grow-only Counter (G-Counter).

    A distributed counter that can only increment. Each agent maintains
    its own counter, and merge takes the maximum value for each agent.

    Properties:
    - Monotonically increasing
    - Commutative merge
    - Space: O(n) where n is number of agents

    Example:
        >>> counter1 = GCounter("agent-1")
        >>> counter1.increment(5)
        >>> counter2 = GCounter("agent-2")
        >>> counter2.increment(3)
        >>> merged = counter1.merge(counter2)
        >>> merged.value()
        8
    """

    agent_id: str
    counts: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize agent's counter to 0 if not present."""
        if self.agent_id not in self.counts:
            self.counts[self.agent_id] = 0

    def increment(self, delta: int = 1) -> None:
        """
        Increment this agent's counter.

        Args:
            delta: Amount to increment (must be positive)

        Raises:
            ValueError: If delta is not positive
        """
        if delta <= 0:
            raise ValueError(f"Delta must be positive, got {delta}")

        if self.agent_id not in self.counts:
            self.counts[self.agent_id] = 0
        self.counts[self.agent_id] += delta

    def value(self) -> int:
        """
        Get the current counter value (sum of all agent counts).

        Returns:
            Total count across all agents
        """
        return sum(self.counts.values())

    def merge(self, other: "GCounter") -> "GCounter":
        """
        Merge another G-Counter by taking max for each agent.

        Args:
            other: Another G-Counter

        Returns:
            New merged G-Counter
        """
        merged_counts = {}

        # Merge by taking max of each agent's count
        all_agents = set(self.counts.keys()) | set(other.counts.keys())
        for agent in all_agents:
            self_count = self.counts.get(agent, 0)
            other_count = other.counts.get(agent, 0)
            merged_counts[agent] = max(self_count, other_count)

        # Create new counter with merged data
        result = GCounter(self.agent_id)
        result.counts = merged_counts
        return result


@dataclass
class PNCounter(CRDT):
    """
    Positive-Negative Counter (PN-Counter).

    A distributed counter that supports both increment and decrement.
    Implemented using two G-Counters: one for increments (P) and one
    for decrements (N). Value = P - N.

    Properties:
    - Supports increment and decrement
    - Commutative merge
    - Space: O(2n) where n is number of agents

    Example:
        >>> counter = PNCounter("agent-1")
        >>> counter.increment(10)
        >>> counter.decrement(3)
        >>> counter.value()
        7
    """

    agent_id: str
    increments: GCounter = field(default_factory=lambda: None)
    decrements: GCounter = field(default_factory=lambda: None)

    def __post_init__(self):
        """Initialize increment and decrement counters."""
        if self.increments is None:
            self.increments = GCounter(self.agent_id)
        if self.decrements is None:
            self.decrements = GCounter(self.agent_id)

    def increment(self, delta: int = 1) -> None:
        """
        Increment the counter.

        Args:
            delta: Amount to increment (must be positive)
        """
        self.increments.increment(delta)

    def decrement(self, delta: int = 1) -> None:
        """
        Decrement the counter.

        Args:
            delta: Amount to decrement (must be positive)
        """
        self.decrements.increment(delta)

    def value(self) -> int:
        """
        Get the current counter value (increments - decrements).

        Returns:
            Net count value
        """
        return self.increments.value() - self.decrements.value()

    def merge(self, other: "PNCounter") -> "PNCounter":
        """
        Merge another PN-Counter.

        Args:
            other: Another PN-Counter

        Returns:
            New merged PN-Counter
        """
        result = PNCounter(self.agent_id)
        result.increments = self.increments.merge(other.increments)
        result.decrements = self.decrements.merge(other.decrements)
        return result


@dataclass
class LWWRegister(CRDT, Generic[T]):
    """
    Last-Write-Wins Register (LWW-Register).

    A distributed register that stores a single value. Conflicts are resolved
    by timestamp - the most recent write wins. In case of timestamp ties,
    agent_id is used as a tiebreaker.

    Properties:
    - Single value storage
    - Timestamp-based conflict resolution
    - Deterministic tie-breaking

    Example:
        >>> reg1 = LWWRegister("agent-1")
        >>> reg1.set("value1")
        >>> reg2 = LWWRegister("agent-2")
        >>> reg2.set("value2")  # Happens later
        >>> merged = reg1.merge(reg2)
        >>> merged.value()
        'value2'
    """

    agent_id: str
    _value: T = None
    _timestamp: float = 0.0
    _writer_id: str = ""

    def set(self, value: T) -> None:
        """
        Set the register value with current timestamp.

        Args:
            value: Value to set
        """
        self._value = value
        self._timestamp = time.time()
        self._writer_id = self.agent_id

    def value(self) -> T:
        """
        Get the current register value.

        Returns:
            Current value (may be None if never set)
        """
        return self._value

    def timestamp(self) -> float:
        """
        Get the timestamp of the current value.

        Returns:
            Timestamp of last write
        """
        return self._timestamp

    def merge(self, other: "LWWRegister[T]") -> "LWWRegister[T]":
        """
        Merge another LWW-Register by taking the value with latest timestamp.

        Tie-breaking rules:
        1. Latest timestamp wins
        2. If timestamps equal, lexicographically larger agent_id wins

        Args:
            other: Another LWW-Register

        Returns:
            New merged LWW-Register
        """
        result = LWWRegister(self.agent_id)

        # Compare timestamps
        if self._timestamp > other._timestamp:
            # This register has newer value
            result._value = self._value
            result._timestamp = self._timestamp
            result._writer_id = self._writer_id
        elif self._timestamp < other._timestamp:
            # Other register has newer value
            result._value = other._value
            result._timestamp = other._timestamp
            result._writer_id = other._writer_id
        else:
            # Timestamps are equal - use agent_id as tie-breaker
            if self._writer_id > other._writer_id:
                result._value = self._value
                result._timestamp = self._timestamp
                result._writer_id = self._writer_id
            else:
                result._value = other._value
                result._timestamp = other._timestamp
                result._writer_id = other._writer_id

        return result


@dataclass
class ORSet(CRDT, Generic[T]):
    """
    Observed-Remove Set (OR-Set).

    A distributed set that supports add and remove operations. Each element
    is tagged with a unique identifier. An element is in the set if it has
    been added but not all its tags have been removed.

    This resolves the add-remove conflict in favor of adds - concurrent
    add/remove results in the element being present.

    Properties:
    - Add-wins semantics
    - Handles concurrent operations correctly
    - Space: O(n*m) where n is elements, m is add operations

    Example:
        >>> set1 = ORSet("agent-1")
        >>> set1.add("item1")
        >>> set2 = ORSet("agent-2")
        >>> set2.add("item2")
        >>> merged = set1.merge(set2)
        >>> "item1" in merged and "item2" in merged
        True
    """

    agent_id: str
    # Map from element to set of unique tags
    elements: Dict[T, Set[str]] = field(default_factory=dict)
    # Set of removed tags
    tombstones: Set[str] = field(default_factory=set)

    def add(self, element: T) -> None:
        """
        Add an element to the set with a unique tag.

        Args:
            element: Element to add
        """
        # Generate unique tag for this add operation
        tag = f"{self.agent_id}:{uuid.uuid4()}"

        if element not in self.elements:
            self.elements[element] = set()
        self.elements[element].add(tag)

    def remove(self, element: T) -> None:
        """
        Remove an element from the set by marking all its tags as removed.

        Args:
            element: Element to remove
        """
        if element in self.elements:
            # Mark all current tags as tombstones
            self.tombstones.update(self.elements[element])

    def __contains__(self, element: T) -> bool:
        """
        Check if an element is in the set.

        An element is present if it has at least one tag that
        is not in tombstones.

        Args:
            element: Element to check

        Returns:
            True if element is in the set
        """
        if element not in self.elements:
            return False

        # Element is present if it has any non-tombstone tags
        active_tags = self.elements[element] - self.tombstones
        return len(active_tags) > 0

    def __iter__(self):
        """
        Iterate over elements in the set.

        Yields:
            Elements that are currently in the set
        """
        for element in self.elements:
            if element in self:
                yield element

    def __len__(self) -> int:
        """
        Get the number of elements in the set.

        Returns:
            Count of active elements
        """
        return sum(1 for _ in self)

    def to_set(self) -> Set[T]:
        """
        Convert to a standard Python set.

        Returns:
            Set of active elements
        """
        return {element for element in self}

    def merge(self, other: "ORSet[T]") -> "ORSet[T]":
        """
        Merge another OR-Set by taking union of elements and tombstones.

        Args:
            other: Another OR-Set

        Returns:
            New merged OR-Set
        """
        result = ORSet(self.agent_id)

        # Merge elements: take union of tags for each element
        all_elements = set(self.elements.keys()) | set(other.elements.keys())
        for element in all_elements:
            self_tags = self.elements.get(element, set())
            other_tags = other.elements.get(element, set())
            result.elements[element] = self_tags | other_tags

        # Merge tombstones: take union
        result.tombstones = self.tombstones | other.tombstones

        return result


# ============================================================================
# CRDT Consensus Adapter
# ============================================================================

class CRDTConsensus:
    """
    Consensus algorithm using CRDT for automatic conflict resolution.

    Uses G-Counter CRDT to aggregate votes across agents. Each agent's vote
    is represented as an increment to its G-Counter. Merge operation combines
    all votes deterministically.

    This provides:
    - Automatic conflict resolution (no explicit consensus protocol needed)
    - Eventual consistency (all agents converge to same decision)
    - No coordination overhead (agents vote independently)

    Example:
        >>> crdt_consensus = CRDTConsensus()
        >>> votes = {
        ...     "agent-1": "approve",
        ...     "agent-2": "approve",
        ...     "agent-3": "reject"
        ... }
        >>> result = crdt_consensus.decide(votes, threshold=0.66)
        >>> print(result["decision"])  # "approved" (2/3 = 66.7%)
    """

    def __init__(self):
        """Initialize CRDT Consensus adapter."""
        self.state = {
            "total_proposals": 0,
            "total_decisions": 0
        }

    def decide(
        self,
        votes: Dict[str, str],
        threshold: float = 0.5,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Use CRDT to merge votes and determine consensus.

        Each agent's vote is converted to a G-Counter increment. All counters
        are merged to produce final tallies.

        Args:
            votes: Dict mapping agent_id -> vote ("approve", "reject", "abstain")
            threshold: Approval threshold (0.0 to 1.0, default: 0.5)
            metadata: Additional metadata for the decision

        Returns:
            Dict with decision outcome containing:
                - decision: "approved" or "rejected"
                - votes_for: Number of approval votes
                - votes_against: Number of rejection votes
                - abstain: Number of abstentions
                - threshold: Applied threshold
                - participants: List of agent IDs
                - vote_details: Dict of individual votes
                - metadata: Additional metadata

        Raises:
            ValueError: If threshold is invalid or votes dict is empty
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be between 0.0 and 1.0 (got {threshold})")

        if not votes:
            raise ValueError("Votes dictionary cannot be empty")

        # Initialize counters for each vote type
        approve_counter = GCounter("approve")
        reject_counter = GCounter("reject")
        abstain_counter = GCounter("abstain")

        # Collect votes into G-Counters
        for agent_id, vote in votes.items():
            vote_lower = vote.lower()

            if vote_lower == "approve":
                approve_counter.increment(1)
            elif vote_lower == "reject":
                reject_counter.increment(1)
            elif vote_lower == "abstain":
                abstain_counter.increment(1)
            else:
                # Invalid vote - treat as abstain
                abstain_counter.increment(1)

        # Get final tallies
        votes_for = approve_counter.value()
        votes_against = reject_counter.value()
        abstain = abstain_counter.value()
        total_votes = votes_for + votes_against + abstain

        # Calculate approval percentage (excluding abstentions)
        active_votes = votes_for + votes_against
        approval_rate = votes_for / active_votes if active_votes > 0 else 0.0

        # Determine decision
        decision = "approved" if approval_rate >= threshold else "rejected"

        # Update state
        self.state["total_proposals"] += 1
        self.state["total_decisions"] += 1

        result = {
            "decision": decision,
            "votes_for": votes_for,
            "votes_against": votes_against,
            "abstain": abstain,
            "threshold": threshold,
            "participants": list(votes.keys()),
            "vote_details": votes,
            "metadata": {
                "approval_rate": approval_rate,
                "total_votes": total_votes,
                "crdt_type": "GCounter",
                **(metadata or {})
            }
        }

        return result

    def get_state(self) -> Dict[str, Any]:
        """
        Get current algorithm state.

        Returns:
            Dict with state information
        """
        return {
            "algorithm": "CRDTConsensus",
            "total_proposals": self.state["total_proposals"],
            "total_decisions": self.state["total_decisions"]
        }

    def reset(self) -> bool:
        """
        Reset algorithm to initial state.

        Returns:
            True (always successful)
        """
        self.state = {
            "total_proposals": 0,
            "total_decisions": 0
        }
        return True


__all__ = [
    "CRDT",
    "GCounter",
    "PNCounter",
    "LWWRegister",
    "ORSet",
    "CRDTConsensus",
]
