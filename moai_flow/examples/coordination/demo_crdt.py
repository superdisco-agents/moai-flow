#!/usr/bin/env python3
"""
CRDT Demonstration for PRD-07

Showcases conflict-free replicated data types and their automatic
conflict resolution capabilities in distributed agent systems.

Run: python3 moai_flow/coordination/demo_crdt.py
"""

import importlib.util
import time

# Load CRDT module directly to avoid circular import
spec = importlib.util.spec_from_file_location("crdt", "moai_flow/coordination/algorithms/crdt.py")
crdt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crdt)


def demo_section(title):
    """Print a demo section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_gcounter():
    """Demonstrate G-Counter (grow-only counter)."""
    demo_section("G-Counter: Distributed Event Counting")
    
    print("\nScenario: Three agents independently count page views")
    
    # Agent 1 counts 100 views
    agent1 = crdt.GCounter("agent-1")
    agent1.increment(100)
    print(f"Agent 1 counted: {agent1.value()} views")
    
    # Agent 2 counts 75 views
    agent2 = crdt.GCounter("agent-2")
    agent2.increment(75)
    print(f"Agent 2 counted: {agent2.value()} views")
    
    # Agent 3 counts 150 views
    agent3 = crdt.GCounter("agent-3")
    agent3.increment(150)
    print(f"Agent 3 counted: {agent3.value()} views")
    
    # Merge all counters
    print("\nMerging all agent counters...")
    merged = agent1.merge(agent2).merge(agent3)
    print(f"Total page views: {merged.value()}")
    print(f"✓ Conflict-free merge: 100 + 75 + 150 = {merged.value()}")


def demo_pncounter():
    """Demonstrate PN-Counter (positive-negative counter)."""
    demo_section("PN-Counter: Inventory Tracking")
    
    print("\nScenario: Multiple warehouses track inventory changes")
    
    # Warehouse 1: Receive 50 items, ship 10
    warehouse1 = crdt.PNCounter("warehouse-1")
    warehouse1.increment(50)
    warehouse1.decrement(10)
    print(f"Warehouse 1 net change: +{warehouse1.value()} items")
    
    # Warehouse 2: Receive 30 items, ship 15
    warehouse2 = crdt.PNCounter("warehouse-2")
    warehouse2.increment(30)
    warehouse2.decrement(15)
    print(f"Warehouse 2 net change: +{warehouse2.value()} items")
    
    # Merge inventory changes
    print("\nMerging warehouse inventories...")
    merged = warehouse1.merge(warehouse2)
    print(f"Total net inventory change: +{merged.value()} items")
    print(f"✓ Combined: (50-10) + (30-15) = {merged.value()}")


def demo_lww_register():
    """Demonstrate LWW-Register (last-write-wins)."""
    demo_section("LWW-Register: Configuration Management")
    
    print("\nScenario: Multiple admins update server configuration")
    
    # Admin 1 sets configuration
    admin1 = crdt.LWWRegister("admin-1")
    admin1.set({"max_connections": 100, "timeout": 30})
    print(f"Admin 1 config: {admin1.value()}")
    print(f"  Timestamp: {admin1.timestamp():.2f}")
    
    # Small delay to ensure different timestamps
    time.sleep(0.01)
    
    # Admin 2 updates configuration
    admin2 = crdt.LWWRegister("admin-2")
    admin2.set({"max_connections": 200, "timeout": 60})
    print(f"\nAdmin 2 config: {admin2.value()}")
    print(f"  Timestamp: {admin2.timestamp():.2f}")
    
    # Merge configurations (latest wins)
    print("\nMerging configurations...")
    merged = admin1.merge(admin2)
    print(f"Final config (latest timestamp): {merged.value()}")
    print(f"✓ Latest write wins: Admin 2's config applied")


def demo_orset():
    """Demonstrate OR-Set (observed-remove set)."""
    demo_section("OR-Set: Collaborative Tag Management")
    
    print("\nScenario: Multiple users manage document tags")
    
    # User 1 adds tags
    user1 = crdt.ORSet("user-1")
    user1.add("python")
    user1.add("distributed-systems")
    print(f"User 1 tags: {user1.to_set()}")
    
    # User 2 adds different tags
    user2 = crdt.ORSet("user-2")
    user2.add("consensus")
    user2.add("crdt")
    print(f"User 2 tags: {user2.to_set()}")
    
    # User 1 removes a tag
    user1.remove("distributed-systems")
    print(f"\nUser 1 removed 'distributed-systems': {user1.to_set()}")
    
    # Merge tag sets
    print("\nMerging tag sets...")
    merged = user1.merge(user2)
    print(f"Final tags: {merged.to_set()}")
    print(f"✓ Add-wins semantics: All tags preserved except removed ones")


def demo_crdt_consensus():
    """Demonstrate CRDT-based consensus."""
    demo_section("CRDT Consensus: Distributed Voting")
    
    print("\nScenario 1: Simple Majority (threshold=0.5)")
    consensus = crdt.CRDTConsensus()
    
    votes = {
        "agent-1": "approve",
        "agent-2": "approve",
        "agent-3": "reject",
        "agent-4": "approve",
        "agent-5": "reject"
    }
    
    result = consensus.decide(votes, threshold=0.5)
    print(f"Votes: 3 approve, 2 reject")
    print(f"Decision: {result['decision']}")
    print(f"Approval rate: {result['metadata']['approval_rate']:.1%}")
    print(f"✓ Simple majority achieved (60% > 50%)")
    
    print("\nScenario 2: Supermajority (threshold=0.66)")
    
    votes2 = {
        "agent-1": "approve",
        "agent-2": "approve",
        "agent-3": "reject"
    }
    
    result2 = consensus.decide(votes2, threshold=0.66)
    print(f"Votes: 2 approve, 1 reject")
    print(f"Decision: {result2['decision']}")
    print(f"Approval rate: {result2['metadata']['approval_rate']:.1%}")
    print(f"✓ Supermajority achieved (66.7% >= 66%)")
    
    print("\nScenario 3: Unanimous (threshold=1.0)")
    
    votes3 = {
        "agent-1": "approve",
        "agent-2": "approve",
        "agent-3": "approve"
    }
    
    result3 = consensus.decide(votes3, threshold=1.0)
    print(f"Votes: 3 approve, 0 reject")
    print(f"Decision: {result3['decision']}")
    print(f"Approval rate: {result3['metadata']['approval_rate']:.1%}")
    print(f"✓ Unanimous consensus achieved")


def demo_merge_properties():
    """Demonstrate CRDT mathematical properties."""
    demo_section("CRDT Properties: Commutativity, Associativity, Idempotency")
    
    print("\n1. Commutativity: merge(A, B) = merge(B, A)")
    c1 = crdt.GCounter("agent-1")
    c1.increment(5)
    c2 = crdt.GCounter("agent-2")
    c2.increment(3)
    
    merged_ab = c1.merge(c2)
    merged_ba = c2.merge(c1)
    
    print(f"   merge(c1, c2).value() = {merged_ab.value()}")
    print(f"   merge(c2, c1).value() = {merged_ba.value()}")
    print(f"   ✓ Order doesn't matter: {merged_ab.value() == merged_ba.value()}")
    
    print("\n2. Associativity: merge(merge(A, B), C) = merge(A, merge(B, C))")
    c3 = crdt.GCounter("agent-3")
    c3.increment(7)
    
    left = c1.merge(c2).merge(c3)
    right = c1.merge(c2.merge(c3))
    
    print(f"   merge(merge(c1, c2), c3).value() = {left.value()}")
    print(f"   merge(c1, merge(c2, c3)).value() = {right.value()}")
    print(f"   ✓ Grouping doesn't matter: {left.value() == right.value()}")
    
    print("\n3. Idempotency: merge(A, A) = A")
    merged_self = c1.merge(c1)
    
    print(f"   c1.value() = {c1.value()}")
    print(f"   merge(c1, c1).value() = {merged_self.value()}")
    print(f"   ✓ Merging with self is safe: {c1.value() == merged_self.value()}")


def main():
    """Run all CRDT demonstrations."""
    print("\n" + "▓" * 60)
    print("  CRDT DEMONSTRATION - PRD-07")
    print("  Conflict-Free Replicated Data Types for MoAI-Flow")
    print("▓" * 60)
    
    demo_gcounter()
    demo_pncounter()
    demo_lww_register()
    demo_orset()
    demo_crdt_consensus()
    demo_merge_properties()
    
    print("\n" + "=" * 60)
    print("  ✅ ALL DEMONSTRATIONS COMPLETED")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("- CRDTs provide automatic conflict resolution")
    print("- No coordination required between agents")
    print("- Eventual consistency guaranteed")
    print("- All merge operations are deterministic")
    print("- Perfect for distributed agent systems")


if __name__ == "__main__":
    main()
