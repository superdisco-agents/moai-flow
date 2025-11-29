"""
Comprehensive test suite for CRDT implementations.

Tests all CRDT types (GCounter, PNCounter, LWWRegister, ORSet) for:
- Basic operations (increment, decrement, set, add, remove)
- Merge semantics (commutativity, associativity, idempotency)
- Conflict resolution (concurrent operations)
- Edge cases and error handling

Target: 90%+ coverage, 16+ tests
"""

import pytest
import time
from moai_flow.coordination.algorithms.crdt import (
    GCounter,
    PNCounter,
    LWWRegister,
    ORSet,
)


class TestGCounter:
    """Test suite for GCounter (Grow-only Counter)."""

    def test_g_counter_increment(self):
        """Test basic increment and value operations."""
        counter = GCounter("agent-1")

        # Initial value should be 0
        assert counter.value() == 0

        # Increment by 1
        counter.increment()
        assert counter.value() == 1

        # Increment by 5
        counter.increment(5)
        assert counter.value() == 6

        # Increment by 10
        counter.increment(10)
        assert counter.value() == 16

    def test_g_counter_merge_max(self):
        """Test merge takes maximum value for each agent."""
        counter1 = GCounter("agent-1")
        counter1.increment(5)

        counter2 = GCounter("agent-2")
        counter2.increment(3)

        # Merge should combine both counters
        merged = counter1.merge(counter2)
        assert merged.value() == 8

        # Merge with overlapping updates
        counter3 = GCounter("agent-1")
        counter3.increment(10)  # Higher than counter1's 5

        merged2 = counter1.merge(counter3)
        assert merged2.value() == 10  # Takes max for agent-1

    def test_g_counter_commutativity(self):
        """Test merge is commutative: A.merge(B) == B.merge(A)."""
        counter1 = GCounter("agent-1")
        counter1.increment(5)

        counter2 = GCounter("agent-2")
        counter2.increment(3)

        # Merge in both orders
        merged_ab = counter1.merge(counter2)
        merged_ba = counter2.merge(counter1)

        # Results should be identical
        assert merged_ab.value() == merged_ba.value()
        assert merged_ab.counts == merged_ba.counts

    def test_g_counter_associativity(self):
        """Test merge is associative: (A.merge(B)).merge(C) == A.merge(B.merge(C))."""
        counter1 = GCounter("agent-1")
        counter1.increment(5)

        counter2 = GCounter("agent-2")
        counter2.increment(3)

        counter3 = GCounter("agent-3")
        counter3.increment(7)

        # Merge with different grouping
        left_assoc = counter1.merge(counter2).merge(counter3)
        right_assoc = counter1.merge(counter2.merge(counter3))

        # Results should be identical
        assert left_assoc.value() == right_assoc.value()
        assert left_assoc.counts == right_assoc.counts

    def test_g_counter_idempotency(self):
        """Test merge is idempotent: A.merge(A) == A."""
        counter = GCounter("agent-1")
        counter.increment(5)

        # Merge with itself
        merged = counter.merge(counter)

        # Should have same value
        assert merged.value() == counter.value()
        assert merged.counts == counter.counts

    def test_g_counter_negative_increment_fails(self):
        """Test that negative increments raise ValueError."""
        counter = GCounter("agent-1")

        with pytest.raises(ValueError, match="Delta must be positive"):
            counter.increment(-5)

        with pytest.raises(ValueError, match="Delta must be positive"):
            counter.increment(0)


class TestPNCounter:
    """Test suite for PNCounter (Positive-Negative Counter)."""

    def test_pn_counter_inc_dec(self):
        """Test increment and decrement operations."""
        counter = PNCounter("agent-1")

        # Initial value should be 0
        assert counter.value() == 0

        # Increment
        counter.increment(10)
        assert counter.value() == 10

        # Decrement
        counter.decrement(3)
        assert counter.value() == 7

        # More operations
        counter.increment(5)
        counter.decrement(2)
        assert counter.value() == 10

    def test_pn_counter_merge(self):
        """Test merge combines both positive and negative counters."""
        counter1 = PNCounter("agent-1")
        counter1.increment(10)
        counter1.decrement(3)

        counter2 = PNCounter("agent-2")
        counter2.increment(5)
        counter2.decrement(2)

        # Merge
        merged = counter1.merge(counter2)

        # (10 - 3) + (5 - 2) = 7 + 3 = 10
        assert merged.value() == 10

    def test_pn_counter_value(self):
        """Test value calculation is correct (P - N)."""
        counter = PNCounter("agent-1")

        # P=15, N=5 -> value=10
        counter.increment(15)
        counter.decrement(5)
        assert counter.value() == 10

        # P=15, N=20 -> value=-5 (negative result)
        counter.decrement(15)
        assert counter.value() == -5

    def test_pn_counter_commutativity(self):
        """Test merge is commutative."""
        counter1 = PNCounter("agent-1")
        counter1.increment(8)
        counter1.decrement(2)

        counter2 = PNCounter("agent-2")
        counter2.increment(4)
        counter2.decrement(1)

        # Merge in both orders
        merged_ab = counter1.merge(counter2)
        merged_ba = counter2.merge(counter1)

        assert merged_ab.value() == merged_ba.value()

    def test_pn_counter_associativity(self):
        """Test merge is associative."""
        counter1 = PNCounter("agent-1")
        counter1.increment(5)

        counter2 = PNCounter("agent-2")
        counter2.decrement(3)

        counter3 = PNCounter("agent-3")
        counter3.increment(7)

        # Different grouping
        left_assoc = counter1.merge(counter2).merge(counter3)
        right_assoc = counter1.merge(counter2.merge(counter3))

        assert left_assoc.value() == right_assoc.value()

    def test_pn_counter_idempotency(self):
        """Test merge is idempotent."""
        counter = PNCounter("agent-1")
        counter.increment(10)
        counter.decrement(3)

        merged = counter.merge(counter)
        assert merged.value() == counter.value()


class TestLWWRegister:
    """Test suite for LWWRegister (Last-Write-Wins Register)."""

    def test_lww_set_get(self):
        """Test set and get value operations."""
        register = LWWRegister("agent-1")

        # Initial value should be None
        assert register.value() is None

        # Set value
        register.set("value1")
        assert register.value() == "value1"

        # Update value
        register.set("value2")
        assert register.value() == "value2"

        # Can store any type
        register.set({"key": "value"})
        assert register.value() == {"key": "value"}

    def test_lww_merge_latest_wins(self):
        """Test merge takes value with latest timestamp."""
        register1 = LWWRegister("agent-1")
        register1.set("first")

        # Wait to ensure different timestamp
        time.sleep(0.01)

        register2 = LWWRegister("agent-2")
        register2.set("second")

        # Merge should take the later value
        merged = register1.merge(register2)
        assert merged.value() == "second"

        # Reverse merge should give same result (commutativity)
        merged_reverse = register2.merge(register1)
        assert merged_reverse.value() == "second"

    def test_lww_merge_tie_break_agent_id(self):
        """Test tie-breaking logic when timestamps are equal."""
        # Create registers with same timestamp by copying
        register1 = LWWRegister("agent-1")
        register1.set("value1")
        timestamp = register1.timestamp()

        register2 = LWWRegister("agent-2")
        register2._value = "value2"
        register2._timestamp = timestamp  # Same timestamp
        register2._writer_id = "agent-2"

        # Merge should use agent_id as tie-breaker
        # "agent-2" > "agent-1" lexicographically
        merged = register1.merge(register2)
        assert merged.value() == "value2"

    def test_lww_concurrent_updates(self):
        """Test concurrent updates resolve deterministically."""
        # Simulate three agents with concurrent writes
        register1 = LWWRegister("agent-alpha")
        register1.set("alpha-value")
        ts = register1.timestamp()

        register2 = LWWRegister("agent-beta")
        register2._value = "beta-value"
        register2._timestamp = ts
        register2._writer_id = "agent-beta"

        register3 = LWWRegister("agent-gamma")
        register3._value = "gamma-value"
        register3._timestamp = ts
        register3._writer_id = "agent-gamma"

        # Merge all three
        merged = register1.merge(register2).merge(register3)

        # Should take lexicographically largest agent_id
        # "agent-gamma" > "agent-beta" > "agent-alpha"
        assert merged.value() == "gamma-value"

    def test_lww_commutativity(self):
        """Test merge is commutative."""
        register1 = LWWRegister("agent-1")
        register1.set("value1")

        time.sleep(0.01)

        register2 = LWWRegister("agent-2")
        register2.set("value2")

        merged_ab = register1.merge(register2)
        merged_ba = register2.merge(register1)

        assert merged_ab.value() == merged_ba.value()

    def test_lww_associativity(self):
        """Test merge is associative."""
        register1 = LWWRegister("agent-1")
        register1.set("value1")

        time.sleep(0.01)
        register2 = LWWRegister("agent-2")
        register2.set("value2")

        time.sleep(0.01)
        register3 = LWWRegister("agent-3")
        register3.set("value3")

        left_assoc = register1.merge(register2).merge(register3)
        right_assoc = register1.merge(register2.merge(register3))

        assert left_assoc.value() == right_assoc.value()

    def test_lww_idempotency(self):
        """Test merge is idempotent."""
        register = LWWRegister("agent-1")
        register.set("value")

        merged = register.merge(register)
        assert merged.value() == register.value()


class TestORSet:
    """Test suite for ORSet (Observed-Remove Set)."""

    def test_or_set_add(self):
        """Test add elements to set."""
        orset = ORSet("agent-1")

        # Initially empty
        assert len(orset) == 0
        assert "item1" not in orset

        # Add element
        orset.add("item1")
        assert "item1" in orset
        assert len(orset) == 1

        # Add more elements
        orset.add("item2")
        orset.add("item3")
        assert len(orset) == 3
        assert "item2" in orset
        assert "item3" in orset

    def test_or_set_remove(self):
        """Test remove elements from set."""
        orset = ORSet("agent-1")

        # Add and remove
        orset.add("item1")
        assert "item1" in orset

        orset.remove("item1")
        assert "item1" not in orset
        assert len(orset) == 0

        # Remove non-existent element (should not error)
        orset.remove("item2")
        assert len(orset) == 0

    def test_or_set_merge_union(self):
        """Test merge is union of sets."""
        set1 = ORSet("agent-1")
        set1.add("item1")
        set1.add("item2")

        set2 = ORSet("agent-2")
        set2.add("item3")
        set2.add("item4")

        # Merge should have all elements
        merged = set1.merge(set2)
        assert len(merged) == 4
        assert "item1" in merged
        assert "item2" in merged
        assert "item3" in merged
        assert "item4" in merged

    def test_or_set_concurrent_add_remove(self):
        """Test concurrent add/remove operations resolve correctly (add-wins)."""
        set1 = ORSet("agent-1")
        set1.add("item1")

        # Agent 2 adds same item concurrently
        set2 = ORSet("agent-2")
        set2.add("item1")

        # Agent 1 removes it
        set1.remove("item1")

        # Merge: agent-2's concurrent add should win
        merged = set1.merge(set2)

        # Add-wins semantics: item should be present
        assert "item1" in merged

    def test_or_set_iteration(self):
        """Test iterating over set elements."""
        orset = ORSet("agent-1")
        orset.add("item1")
        orset.add("item2")
        orset.add("item3")

        # Convert to Python set
        items = set(orset)
        assert items == {"item1", "item2", "item3"}

        # Test to_set() method
        items_set = orset.to_set()
        assert items_set == {"item1", "item2", "item3"}

    def test_or_set_commutativity(self):
        """Test merge is commutative."""
        set1 = ORSet("agent-1")
        set1.add("item1")
        set1.add("item2")

        set2 = ORSet("agent-2")
        set2.add("item3")

        merged_ab = set1.merge(set2)
        merged_ba = set2.merge(set1)

        assert merged_ab.to_set() == merged_ba.to_set()

    def test_or_set_associativity(self):
        """Test merge is associative."""
        set1 = ORSet("agent-1")
        set1.add("item1")

        set2 = ORSet("agent-2")
        set2.add("item2")

        set3 = ORSet("agent-3")
        set3.add("item3")

        left_assoc = set1.merge(set2).merge(set3)
        right_assoc = set1.merge(set2.merge(set3))

        assert left_assoc.to_set() == right_assoc.to_set()

    def test_or_set_idempotency(self):
        """Test merge is idempotent."""
        orset = ORSet("agent-1")
        orset.add("item1")
        orset.add("item2")

        merged = orset.merge(orset)
        assert merged.to_set() == orset.to_set()


class TestCRDTProperties:
    """Test CRDT mathematical properties across all types."""

    def test_merge_commutative_all_types(self):
        """Test commutativity property for all CRDT types."""
        # GCounter
        gc1 = GCounter("a1")
        gc1.increment(5)
        gc2 = GCounter("a2")
        gc2.increment(3)
        assert gc1.merge(gc2).value() == gc2.merge(gc1).value()

        # PNCounter
        pn1 = PNCounter("a1")
        pn1.increment(10)
        pn2 = PNCounter("a2")
        pn2.decrement(3)
        assert pn1.merge(pn2).value() == pn2.merge(pn1).value()

        # LWWRegister
        lww1 = LWWRegister("a1")
        lww1.set("v1")
        time.sleep(0.01)
        lww2 = LWWRegister("a2")
        lww2.set("v2")
        assert lww1.merge(lww2).value() == lww2.merge(lww1).value()

        # ORSet
        or1 = ORSet("a1")
        or1.add("item1")
        or2 = ORSet("a2")
        or2.add("item2")
        assert or1.merge(or2).to_set() == or2.merge(or1).to_set()

    def test_merge_associative_all_types(self):
        """Test associativity property for all CRDT types."""
        # GCounter
        gc1, gc2, gc3 = GCounter("a1"), GCounter("a2"), GCounter("a3")
        gc1.increment(2)
        gc2.increment(3)
        gc3.increment(5)
        left = gc1.merge(gc2).merge(gc3)
        right = gc1.merge(gc2.merge(gc3))
        assert left.value() == right.value()

        # PNCounter
        pn1, pn2, pn3 = PNCounter("a1"), PNCounter("a2"), PNCounter("a3")
        pn1.increment(5)
        pn2.decrement(2)
        pn3.increment(7)
        left = pn1.merge(pn2).merge(pn3)
        right = pn1.merge(pn2.merge(pn3))
        assert left.value() == right.value()

        # LWWRegister (value should be deterministic)
        lww1, lww2, lww3 = LWWRegister("a1"), LWWRegister("a2"), LWWRegister("a3")
        lww1.set("v1")
        time.sleep(0.01)
        lww2.set("v2")
        time.sleep(0.01)
        lww3.set("v3")
        left = lww1.merge(lww2).merge(lww3)
        right = lww1.merge(lww2.merge(lww3))
        assert left.value() == right.value()

        # ORSet
        or1, or2, or3 = ORSet("a1"), ORSet("a2"), ORSet("a3")
        or1.add("i1")
        or2.add("i2")
        or3.add("i3")
        left = or1.merge(or2).merge(or3)
        right = or1.merge(or2.merge(or3))
        assert left.to_set() == right.to_set()

    def test_merge_idempotent_all_types(self):
        """Test idempotency property for all CRDT types."""
        # GCounter
        gc = GCounter("a1")
        gc.increment(5)
        assert gc.merge(gc).value() == gc.value()

        # PNCounter
        pn = PNCounter("a1")
        pn.increment(10)
        pn.decrement(3)
        assert pn.merge(pn).value() == pn.value()

        # LWWRegister
        lww = LWWRegister("a1")
        lww.set("value")
        assert lww.merge(lww).value() == lww.value()

        # ORSet
        orset = ORSet("a1")
        orset.add("item")
        assert orset.merge(orset).to_set() == orset.to_set()


class TestCRDTConsensus:
    """Test suite for CRDTConsensus (CRDT-based consensus algorithm)."""

    def test_crdt_consensus_simple_majority(self):
        """Test simple majority consensus (threshold=0.5)."""
        consensus = CRDTConsensus()

        # 2 approve, 1 reject -> approved
        votes = {
            "agent-1": "approve",
            "agent-2": "approve",
            "agent-3": "reject"
        }

        result = consensus.decide(votes, threshold=0.5)

        assert result["decision"] == "approved"
        assert result["votes_for"] == 2
        assert result["votes_against"] == 1
        assert result["abstain"] == 0
        assert result["threshold"] == 0.5
        assert result["metadata"]["approval_rate"] == 2/3

    def test_crdt_consensus_supermajority(self):
        """Test supermajority consensus (threshold=0.66)."""
        consensus = CRDTConsensus()

        # 2 approve, 1 reject -> 66.7% approval
        votes = {
            "agent-1": "approve",
            "agent-2": "approve",
            "agent-3": "reject"
        }

        result = consensus.decide(votes, threshold=0.66)

        assert result["decision"] == "approved"
        assert result["metadata"]["approval_rate"] >= 0.66

        # 2 approve, 2 reject -> 50% approval (rejected)
        votes2 = {
            "agent-1": "approve",
            "agent-2": "approve",
            "agent-3": "reject",
            "agent-4": "reject"
        }

        result2 = consensus.decide(votes2, threshold=0.66)
        assert result2["decision"] == "rejected"

    def test_crdt_consensus_unanimous(self):
        """Test unanimous consensus (threshold=1.0)."""
        consensus = CRDTConsensus()

        # All approve -> approved
        votes = {
            "agent-1": "approve",
            "agent-2": "approve",
            "agent-3": "approve"
        }

        result = consensus.decide(votes, threshold=1.0)
        assert result["decision"] == "approved"

        # One reject -> rejected
        votes2 = {
            "agent-1": "approve",
            "agent-2": "approve",
            "agent-3": "reject"
        }

        result2 = consensus.decide(votes2, threshold=1.0)
        assert result2["decision"] == "rejected"

    def test_crdt_consensus_with_abstentions(self):
        """Test consensus with abstaining votes (excluded from calculation)."""
        consensus = CRDTConsensus()

        # 2 approve, 1 abstain -> 100% of active votes
        votes = {
            "agent-1": "approve",
            "agent-2": "approve",
            "agent-3": "abstain"
        }

        result = consensus.decide(votes, threshold=0.66)

        assert result["decision"] == "approved"
        assert result["votes_for"] == 2
        assert result["votes_against"] == 0
        assert result["abstain"] == 1
        assert result["metadata"]["approval_rate"] == 1.0  # 2/2 active votes

    def test_crdt_consensus_invalid_votes(self):
        """Test invalid votes are treated as abstentions."""
        consensus = CRDTConsensus()

        votes = {
            "agent-1": "approve",
            "agent-2": "approve",
            "agent-3": "invalid-vote"  # Should be treated as abstain
        }

        result = consensus.decide(votes, threshold=0.5)

        assert result["abstain"] == 1
        assert result["metadata"]["approval_rate"] == 1.0  # 2/2 active votes

    def test_crdt_consensus_state_tracking(self):
        """Test consensus state tracking."""
        consensus = CRDTConsensus()

        # Initial state
        state = consensus.get_state()
        assert state["algorithm"] == "CRDTConsensus"
        assert state["total_proposals"] == 0
        assert state["total_decisions"] == 0

        # After one decision
        votes = {"agent-1": "approve", "agent-2": "approve"}
        consensus.decide(votes)

        state = consensus.get_state()
        assert state["total_proposals"] == 1
        assert state["total_decisions"] == 1

        # After reset
        consensus.reset()
        state = consensus.get_state()
        assert state["total_proposals"] == 0
        assert state["total_decisions"] == 0

    def test_crdt_consensus_vote_details(self):
        """Test result contains detailed vote information."""
        consensus = CRDTConsensus()

        votes = {
            "agent-1": "approve",
            "agent-2": "reject",
            "agent-3": "abstain"
        }

        result = consensus.decide(votes)

        assert result["participants"] == ["agent-1", "agent-2", "agent-3"]
        assert result["vote_details"] == votes
        assert "approval_rate" in result["metadata"]
        assert "total_votes" in result["metadata"]
        assert result["metadata"]["crdt_type"] == "GCounter"

    def test_crdt_consensus_custom_metadata(self):
        """Test custom metadata is preserved."""
        consensus = CRDTConsensus()

        votes = {"agent-1": "approve", "agent-2": "approve"}
        custom_meta = {"proposal_id": "PROP-123", "priority": "high"}

        result = consensus.decide(votes, metadata=custom_meta)

        assert result["metadata"]["proposal_id"] == "PROP-123"
        assert result["metadata"]["priority"] == "high"

    def test_crdt_consensus_empty_votes_error(self):
        """Test error handling for empty votes."""
        consensus = CRDTConsensus()

        with pytest.raises(ValueError, match="Votes dictionary cannot be empty"):
            consensus.decide({})

    def test_crdt_consensus_invalid_threshold_error(self):
        """Test error handling for invalid threshold."""
        consensus = CRDTConsensus()

        votes = {"agent-1": "approve"}

        # Threshold < 0
        with pytest.raises(ValueError, match="Threshold must be between 0.0 and 1.0"):
            consensus.decide(votes, threshold=-0.1)

        # Threshold > 1
        with pytest.raises(ValueError, match="Threshold must be between 0.0 and 1.0"):
            consensus.decide(votes, threshold=1.1)

    def test_crdt_consensus_all_abstain(self):
        """Test handling when all votes are abstentions."""
        consensus = CRDTConsensus()

        votes = {
            "agent-1": "abstain",
            "agent-2": "abstain",
            "agent-3": "abstain"
        }

        result = consensus.decide(votes)

        # With no active votes, approval_rate is 0
        assert result["decision"] == "rejected"
        assert result["metadata"]["approval_rate"] == 0.0
        assert result["votes_for"] == 0
        assert result["votes_against"] == 0
        assert result["abstain"] == 3
