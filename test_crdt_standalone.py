#!/usr/bin/env python3
"""
Standalone CRDT test runner to bypass circular import issues.

This script directly loads and tests the CRDT module without
going through the package hierarchy that has circular dependencies.
"""

import importlib.util
import sys
import time

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Load crdt module directly
spec = importlib.util.spec_from_file_location(
    'crdt',
    'moai_flow/coordination/algorithms/crdt.py'
)
crdt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crdt)

# Import CRDT classes
GCounter = crdt.GCounter
PNCounter = crdt.PNCounter
LWWRegister = crdt.LWWRegister
ORSet = crdt.ORSet

# Test counters
passed = 0
failed = 0
total = 0


def test(name):
    """Decorator to mark and run tests."""
    def decorator(func):
        global passed, failed, total
        total += 1
        try:
            func()
            passed += 1
            print(f"{GREEN}✓{RESET} {name}")
            return True
        except AssertionError as e:
            failed += 1
            print(f"{RED}✗{RESET} {name}")
            print(f"  {RED}Error: {e}{RESET}")
            return False
        except Exception as e:
            failed += 1
            print(f"{RED}✗{RESET} {name}")
            print(f"  {RED}Unexpected error: {e}{RESET}")
            return False
    return decorator


print(f"\n{BOLD}{BLUE}{'=' * 70}{RESET}")
print(f"{BOLD}{BLUE}CRDT Test Suite (Standalone){RESET}")
print(f"{BOLD}{BLUE}{'=' * 70}{RESET}\n")

# GCounter Tests
print(f"{BOLD}GCounter Tests:{RESET}")


@test("GCounter: Basic increment and value")
def test_gc_increment():
    counter = GCounter("agent-1")
    assert counter.value() == 0
    counter.increment()
    assert counter.value() == 1
    counter.increment(5)
    assert counter.value() == 6


@test("GCounter: Merge takes maximum")
def test_gc_merge():
    c1 = GCounter("agent-1")
    c1.increment(5)
    c2 = GCounter("agent-2")
    c2.increment(3)
    merged = c1.merge(c2)
    assert merged.value() == 8


@test("GCounter: Commutativity")
def test_gc_commutative():
    c1 = GCounter("agent-1")
    c1.increment(5)
    c2 = GCounter("agent-2")
    c2.increment(3)
    assert c1.merge(c2).value() == c2.merge(c1).value()


@test("GCounter: Associativity")
def test_gc_associative():
    c1, c2, c3 = GCounter("a1"), GCounter("a2"), GCounter("a3")
    c1.increment(5)
    c2.increment(3)
    c3.increment(7)
    left = c1.merge(c2).merge(c3)
    right = c1.merge(c2.merge(c3))
    assert left.value() == right.value()


@test("GCounter: Idempotency")
def test_gc_idempotent():
    c = GCounter("agent-1")
    c.increment(5)
    assert c.merge(c).value() == c.value()


# PNCounter Tests
print(f"\n{BOLD}PNCounter Tests:{RESET}")


@test("PNCounter: Increment and decrement")
def test_pn_inc_dec():
    counter = PNCounter("agent-1")
    counter.increment(10)
    assert counter.value() == 10
    counter.decrement(3)
    assert counter.value() == 7


@test("PNCounter: Merge")
def test_pn_merge():
    c1 = PNCounter("agent-1")
    c1.increment(10)
    c1.decrement(3)
    c2 = PNCounter("agent-2")
    c2.increment(5)
    c2.decrement(2)
    merged = c1.merge(c2)
    assert merged.value() == 10  # (10-3) + (5-2) = 10


@test("PNCounter: Value calculation")
def test_pn_value():
    counter = PNCounter("agent-1")
    counter.increment(15)
    counter.decrement(5)
    assert counter.value() == 10
    counter.decrement(15)
    assert counter.value() == -5


@test("PNCounter: Commutativity")
def test_pn_commutative():
    c1 = PNCounter("agent-1")
    c1.increment(8)
    c1.decrement(2)
    c2 = PNCounter("agent-2")
    c2.increment(4)
    c2.decrement(1)
    assert c1.merge(c2).value() == c2.merge(c1).value()


# LWWRegister Tests
print(f"\n{BOLD}LWWRegister Tests:{RESET}")


@test("LWWRegister: Set and get")
def test_lww_set_get():
    reg = LWWRegister("agent-1")
    assert reg.value() is None
    reg.set("value1")
    assert reg.value() == "value1"
    reg.set("value2")
    assert reg.value() == "value2"


@test("LWWRegister: Latest wins")
def test_lww_latest_wins():
    r1 = LWWRegister("agent-1")
    r1.set("first")
    time.sleep(0.01)
    r2 = LWWRegister("agent-2")
    r2.set("second")
    merged = r1.merge(r2)
    assert merged.value() == "second"


@test("LWWRegister: Tie-breaking")
def test_lww_tie_break():
    r1 = LWWRegister("agent-1")
    r1.set("value1")
    ts = r1.timestamp()
    r2 = LWWRegister("agent-2")
    r2._value = "value2"
    r2._timestamp = ts
    r2._writer_id = "agent-2"
    merged = r1.merge(r2)
    assert merged.value() == "value2"  # agent-2 > agent-1


@test("LWWRegister: Concurrent updates")
def test_lww_concurrent():
    r1 = LWWRegister("agent-alpha")
    r1.set("alpha-value")
    ts = r1.timestamp()
    r2 = LWWRegister("agent-beta")
    r2._value = "beta-value"
    r2._timestamp = ts
    r2._writer_id = "agent-beta"
    r3 = LWWRegister("agent-gamma")
    r3._value = "gamma-value"
    r3._timestamp = ts
    r3._writer_id = "agent-gamma"
    merged = r1.merge(r2).merge(r3)
    assert merged.value() == "gamma-value"  # gamma > beta > alpha


# ORSet Tests
print(f"\n{BOLD}ORSet Tests:{RESET}")


@test("ORSet: Add elements")
def test_or_add():
    s = ORSet("agent-1")
    assert len(s) == 0
    s.add("item1")
    assert "item1" in s
    assert len(s) == 1
    s.add("item2")
    s.add("item3")
    assert len(s) == 3


@test("ORSet: Remove elements")
def test_or_remove():
    s = ORSet("agent-1")
    s.add("item1")
    assert "item1" in s
    s.remove("item1")
    assert "item1" not in s


@test("ORSet: Merge union")
def test_or_merge():
    s1 = ORSet("agent-1")
    s1.add("item1")
    s1.add("item2")
    s2 = ORSet("agent-2")
    s2.add("item3")
    s2.add("item4")
    merged = s1.merge(s2)
    assert len(merged) == 4
    assert "item1" in merged and "item4" in merged


@test("ORSet: Concurrent add/remove (add-wins)")
def test_or_concurrent():
    s1 = ORSet("agent-1")
    s1.add("item1")
    s2 = ORSet("agent-2")
    s2.add("item1")
    s1.remove("item1")
    merged = s1.merge(s2)
    assert "item1" in merged  # Add-wins


# CRDT Properties Tests
print(f"\n{BOLD}CRDT Properties (All Types):{RESET}")


@test("All CRDTs: Commutativity")
def test_all_commutative():
    # GCounter
    gc1, gc2 = GCounter("a1"), GCounter("a2")
    gc1.increment(5)
    gc2.increment(3)
    assert gc1.merge(gc2).value() == gc2.merge(gc1).value()
    # PNCounter
    pn1, pn2 = PNCounter("a1"), PNCounter("a2")
    pn1.increment(10)
    pn2.decrement(3)
    assert pn1.merge(pn2).value() == pn2.merge(pn1).value()
    # LWWRegister
    lww1, lww2 = LWWRegister("a1"), LWWRegister("a2")
    lww1.set("v1")
    time.sleep(0.01)
    lww2.set("v2")
    assert lww1.merge(lww2).value() == lww2.merge(lww1).value()
    # ORSet
    or1, or2 = ORSet("a1"), ORSet("a2")
    or1.add("i1")
    or2.add("i2")
    assert or1.merge(or2).to_set() == or2.merge(or1).to_set()


@test("All CRDTs: Associativity")
def test_all_associative():
    # GCounter
    gc1, gc2, gc3 = GCounter("a1"), GCounter("a2"), GCounter("a3")
    gc1.increment(2)
    gc2.increment(3)
    gc3.increment(5)
    left = gc1.merge(gc2).merge(gc3)
    right = gc1.merge(gc2.merge(gc3))
    assert left.value() == right.value()


@test("All CRDTs: Idempotency")
def test_all_idempotent():
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
    ors = ORSet("a1")
    ors.add("item")
    assert ors.merge(ors).to_set() == ors.to_set()


# Summary
print(f"\n{BOLD}{BLUE}{'=' * 70}{RESET}")
print(f"{BOLD}Test Summary:{RESET}")
print(f"  Total:  {total}")
print(f"  {GREEN}Passed: {passed}{RESET}")
if failed > 0:
    print(f"  {RED}Failed: {failed}{RESET}")
    sys.exit(1)
else:
    print(f"  {GREEN}All tests passed!{RESET}")
print(f"{BOLD}{BLUE}{'=' * 70}{RESET}\n")
