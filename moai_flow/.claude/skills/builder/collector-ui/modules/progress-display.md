# Progress Display Patterns

**Progress indicators and status updates for collector operations**

> **Version**: 1.0.0
> **Part of**: collector-ui skill
> **Last Updated**: 2025-12-04

---

## Overview

Progress displays keep users informed during long-running collector operations like scanning, learning, and merging.

---

## Progress Patterns

### 1. Simple Item Progress

For sequential item processing:

```
Scanning Branches...

[1/5] main .......................... Done
[2/5] feature/SPEC-first ............ Done
[3/5] feature/workspace ............. In Progress
[4/5] feature/tdd-integration ....... Pending
[5/5] docs/readme-updates ........... Pending

Current: feature/workspace (47 components found)
Time elapsed: 12s
```

### 2. Progress Bar

For percentage-based progress:

```
Analyzing Components...

[=================>  ] 85% (40/47)

Current: builder-skill
Estimated remaining: 8s
```

### 3. Phase Progress

For multi-phase operations:

```
GitHub Sync Progress
====================

Phase 1: Scanning       [====================] 100% Complete
Phase 2: Learning       [===============>    ]  75% In Progress
Phase 3: Strategy       [                    ]   0% Pending
Phase 4: Apply          [                    ]   0% Pending

Overall: 44% complete
```

### 4. Detailed Score Progress

During learning phase:

```
Learning: Component Analysis
============================

Component: builder-skill (12/47)

  Criterion        Score   Max    Progress
  ------------------------------------------------
  Structure        18      20     [==================  ] 90%
  Documentation    16      20     [================    ] 80%
  Functionality    22      25     [=================>  ] 88%
  Quality          17      20     [=================>  ] 85%
  Freshness        12      15     [================    ] 80%
  ------------------------------------------------
  TOTAL            85     100     [=================>  ] 85%

Status: SHOULD_MERGE (Score: 85)
```

### 5. Merge Progress

During sync application:

```
Applying Sync Changes
=====================

[1/4] PRESERVE collector-scan
      Status: Keeping local version
      Action: No changes needed
      .......................... Done

[2/4] UPDATE foundation-core
      Source: feature/SPEC-first
      Files: 3 modified, 1 added
      .......................... Done

[3/4] SMART MERGE decision-framework
      Combining: local base + main features
      Files: 2 merged
      .......................... In Progress

[4/4] UPDATE builder-skill
      Source: main
      .......................... Pending

Progress: [=================>  ] 62%
Backup: .moai/backups/sync-2025-12-04-001/
```

### 6. Summary Progress

End-of-operation summary:

```
Sync Complete
=============

Results:
  PRESERVED:    1 component  (collector-scan)
  UPDATED:      2 components (foundation-core, builder-skill)
  MERGED:       1 component  (decision-framework)
  SKIPPED:      0 components

Statistics:
  Files modified:  12
  Files added:      3
  Files removed:    0
  Time taken:      45s

Backup Location: .moai/backups/sync-2025-12-04-001/
Rollback Command: /collector:rollback sync-2025-12-04-001
```

---

## Progress Bar Styles

### Standard ASCII

```
[===================>] 100%
[===============>    ]  75%
[=========>          ]  50%
[====>               ]  25%
[                    ]   0%
```

### With Label

```
Scanning: [=================>  ] 85% (40/47 components)
```

### Multi-Line Detailed

```
Phase: Learning
Component: decision-framework
Progress: [==================> ] 92%
ETA: ~3s
```

---

## Status Indicators

### Item Status

```
Done         = Completed successfully
In Progress  = Currently processing
Pending      = Waiting to start
Skipped      = Intentionally skipped
Failed       = Error occurred
```

### Visual Markers

```
[x] Done        = Completed
[>] In Progress = Processing
[ ] Pending     = Waiting
[-] Skipped     = Skipped
[!] Failed      = Error
```

---

## Real-Time Updates

### Streaming Pattern

For operations that can stream progress:

```python
def show_progress_stream():
    """
    Stream progress updates as operations complete.
    """
    for i, item in enumerate(items):
        # Show current item
        print(f"\r[{i+1}/{len(items)}] {item.name}...", end="")

        # Process item
        result = process(item)

        # Show result
        print(f"\r[{i+1}/{len(items)}] {item.name} {'Done' if result else 'Failed'}")
```

### Batch Pattern

For operations that report in batches:

```python
def show_batch_progress(batch_num, total_batches, items_processed):
    """
    Show progress for batch operations.
    """
    pct = (batch_num / total_batches) * 100
    bar = "=" * int(pct / 5) + ">" + " " * (20 - int(pct / 5))
    print(f"Batch {batch_num}/{total_batches} [{bar}] {pct:.0f}%")
    print(f"  Items processed: {items_processed}")
```

---

## Time Estimates

### Elapsed Time

```
Time elapsed: 1m 23s
```

### Remaining Estimate

```
Estimated remaining: ~30s
```

### Rate Display

```
Processing: 3.2 components/sec
```

---

## Error Display in Progress

### Inline Error

```
[1/5] main .......................... Done
[2/5] feature/SPEC-first ............ Done
[3/5] feature/workspace ............. Failed: Connection timeout
[4/5] feature/tdd-integration ....... Pending
[5/5] docs/readme-updates ........... Pending

Warning: 1 branch failed. Continue with remaining? [Y/n]
```

### Summary Error

```
Sync Progress: Partial Failure
==============================

Completed: 3/4
Failed:    1/4

Failed Items:
  - decision-framework: Merge conflict in SKILL.md

Options:
  [1] Retry failed items
  [2] Skip and continue
  [3] Rollback all changes
  [4] Manual resolution
```

---

## Integration Guidelines

### When to Show Progress

```yaml
show_progress_when:
  - Operation > 2 seconds estimated
  - More than 5 items to process
  - User explicitly requested verbose mode
  - Any phase-based operation

hide_progress_when:
  - Quick operations (< 2 seconds)
  - Single item operations
  - Quiet mode enabled
```

### Update Frequency

```yaml
update_frequency:
  progress_bar: Every 1% or 1 second (whichever is less frequent)
  item_status: Immediately on completion
  phase_change: Immediately
  time_estimates: Every 5 seconds
```

---

**Version**: 1.0.0 | **Status**: Production Ready | **Last Updated**: 2025-12-04
