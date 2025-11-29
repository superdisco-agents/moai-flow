# MOAI Cleanup Workflow

You are implementing the MOAI cleanup system - a 5-phase intelligent workspace cleanup workflow with user oversight and safety features.

## CRITICAL RULES
1. **NEVER directly execute file operations** - Use Task() delegation ONLY
2. **ALWAYS use AskUserQuestion()** for user interaction
3. **ALWAYS create checkboxes** for item selection
4. **ALWAYS require explicit confirmation** before any deletion/archival
5. **ALWAYS use safe archival** (move to .archive/ with timestamps)

## 5-PHASE WORKFLOW

### Phase 1: Analysis (Delegation)
Delegate to macos-cleaner agent to analyze workspace:

```javascript
Task(
  "MacOS Cleaner Agent",
  `Analyze workspace for cleanup opportunities:

  Working directory: ${process.cwd()}

  Tasks:
  1. Scan for cleanup candidates:
     - Temporary files (*.tmp, *.log, *.cache)
     - Build artifacts (node_modules, dist, build, .next, .turbo)
     - System files (.DS_Store, Thumbs.db)
     - Large files (>100MB)
     - Duplicate files
     - Old archives (>30 days)
     - Empty directories

  2. Calculate space savings for each category

  3. Generate JSON report:
  {
    "totalSize": "500MB",
    "categories": [
      {
        "name": "Build Artifacts",
        "items": ["path1", "path2"],
        "size": "250MB",
        "risk": "low"
      }
    ]
  }

  4. Store report in memory:
     npx claude-flow@alpha hooks post-edit --memory-key "moai/cleanup/report"

  IMPORTANT: Only analyze, DO NOT delete or modify anything.`,
  "code-analyzer"
)
```

### Phase 2: User Review (AskUserQuestion)
Display analysis report and get user approval:

```javascript
// Retrieve analysis report
const report = await retrieveMemory("moai/cleanup/report");

AskUserQuestion({
  questions: [
    {
      question: "Review the cleanup analysis report. Would you like to proceed with cleanup?",
      header: "Cleanup Report",
      options: [
        {
          label: "Proceed with selection",
          description: `Found ${report.totalSize} of cleanable items. Next: Select specific items to clean.`
        },
        {
          label: "Cancel cleanup",
          description: "Exit without making any changes to the workspace."
        }
      ],
      multiSelect: false
    }
  ]
})
```

### Phase 3: Checkbox Modification (Interactive Selection)
Allow user to select specific items to clean:

```javascript
// Build checkbox options from report
const checkboxOptions = report.categories.map(cat => ({
  label: `${cat.name} (${cat.size})`,
  description: `Risk: ${cat.risk} | Items: ${cat.items.length} | Space saved: ${cat.size}`
}));

AskUserQuestion({
  questions: [
    {
      question: "Select categories to clean (you can select multiple):",
      header: "Select Items",
      options: checkboxOptions,
      multiSelect: true
    }
  ]
})
```

### Phase 4: Confirmation (Explicit Approval)
Show final summary and require explicit confirmation:

```javascript
// Calculate selected items
const selectedCategories = getSelectedCategories();
const totalSelected = calculateTotalSize(selectedCategories);
const itemCount = calculateItemCount(selectedCategories);

AskUserQuestion({
  questions: [
    {
      question: `FINAL CONFIRMATION: Archive ${itemCount} items (${totalSelected})?`,
      header: "Confirm Cleanup",
      options: [
        {
          label: "Execute cleanup",
          description: `Archive ${itemCount} items to .archive/ folder. This is REVERSIBLE - items can be restored.`
        },
        {
          label: "Cancel",
          description: "Exit without making any changes."
        }
      ],
      multiSelect: false
    }
  ]
})
```

### Phase 5: Execution (Safe Archival)
Delegate to macos-cleaner agent for safe archival:

```javascript
Task(
  "MacOS Cleaner Agent",
  `Execute safe archival of selected items:

  Selected categories: ${JSON.stringify(selectedCategories)}
  Working directory: ${process.cwd()}
  Archive location: .archive/cleanup-${Date.now()}/

  Tasks:
  1. Create timestamped archive directory
  2. For each selected item:
     - Verify item exists
     - Calculate checksum (for verification)
     - Move to archive with metadata
     - Create manifest.json

  3. Generate cleanup report:
     - Items archived
     - Space freed
     - Archive location
     - Restoration instructions

  4. Store results in memory:
     npx claude-flow@alpha hooks post-edit --memory-key "moai/cleanup/results"

  Safety rules:
  - NEVER delete permanently
  - ALWAYS move to .archive/
  - ALWAYS create manifest
  - ALWAYS verify operations
  - Handle errors gracefully`,
  "code-analyzer"
)
```

## COORDINATION HOOKS

### Before Analysis
```bash
npx claude-flow@alpha hooks pre-task --description "MOAI cleanup workflow analysis"
npx claude-flow@alpha hooks session-restore --session-id "moai-cleanup"
```

### After Each Phase
```bash
npx claude-flow@alpha hooks post-edit --memory-key "moai/cleanup/phase-${phaseNumber}"
npx claude-flow@alpha hooks notify --message "Phase ${phaseNumber} completed"
```

### After Execution
```bash
npx claude-flow@alpha hooks post-task --task-id "moai-cleanup"
npx claude-flow@alpha hooks session-end --export-metrics true
```

## ERROR HANDLING

### Graceful Degradation
```javascript
try {
  // Execute phase
} catch (error) {
  AskUserQuestion({
    questions: [{
      question: `Error during cleanup: ${error.message}. How would you like to proceed?`,
      header: "Error",
      options: [
        { label: "Retry", description: "Retry the current phase" },
        { label: "Skip", description: "Skip this phase and continue" },
        { label: "Abort", description: "Cancel entire cleanup operation" }
      ],
      multiSelect: false
    }]
  });
}
```

### Safety Checks
- Verify sufficient disk space before archival
- Check write permissions on archive directory
- Validate file paths to prevent directory traversal
- Confirm no critical system files in selection
- Verify archive integrity after operations

## RESTORATION INSTRUCTIONS

Generate restoration script in archive:
```bash
# .archive/cleanup-${timestamp}/RESTORE.sh
#!/bin/bash
# Restoration script generated by MOAI cleanup
# To restore all items: bash RESTORE.sh
# To restore specific item: bash RESTORE.sh path/to/item

# Script moves items back to original locations
# Verifies checksums before restoration
```

## WORKFLOW EXECUTION

```javascript
// Complete workflow in single message
async function executeCleanupWorkflow() {
  // Initialize swarm
  await mcp__claude_flow__swarm_init({
    topology: "hierarchical",
    maxAgents: 5,
    strategy: "auto"
  });

  // Phase 1: Analysis
  await Task("Analysis", analysisInstructions, "code-analyzer");

  // Phase 2: Review
  const reviewResponse = await AskUserQuestion(reviewQuestion);
  if (reviewResponse.cancelled) return;

  // Phase 3: Selection
  const selectionResponse = await AskUserQuestion(selectionQuestion);
  if (!selectionResponse.selectedItems.length) return;

  // Phase 4: Confirmation
  const confirmResponse = await AskUserQuestion(confirmQuestion);
  if (!confirmResponse.confirmed) return;

  // Phase 5: Execution
  await Task("Execution", executionInstructions, "code-analyzer");

  // Generate report
  await displayCompletionReport();
}
```

## TODOS

```javascript
TodoWrite({
  todos: [
    {
      content: "Initialize cleanup workflow and swarm coordination",
      status: "in_progress",
      activeForm: "Initializing cleanup workflow and swarm coordination"
    },
    {
      content: "Execute Phase 1: Delegate workspace analysis",
      status: "pending",
      activeForm: "Executing Phase 1: Delegating workspace analysis"
    },
    {
      content: "Execute Phase 2: Display report and get user approval",
      status: "pending",
      activeForm: "Executing Phase 2: Displaying report and getting approval"
    },
    {
      content: "Execute Phase 3: Interactive item selection via checkboxes",
      status: "pending",
      activeForm: "Executing Phase 3: Interactive item selection"
    },
    {
      content: "Execute Phase 4: Final confirmation with summary",
      status: "pending",
      activeForm: "Executing Phase 4: Final confirmation"
    },
    {
      content: "Execute Phase 5: Safe archival with delegation",
      status: "pending",
      activeForm: "Executing Phase 5: Safe archival operation"
    },
    {
      content: "Generate cleanup report and restoration instructions",
      status: "pending",
      activeForm: "Generating cleanup report and restoration instructions"
    },
    {
      content: "Store results in memory for future reference",
      status: "pending",
      activeForm: "Storing results in memory"
    }
  ]
});
```

## SUCCESS CRITERIA
- ✅ No direct file operations (all via Task delegation)
- ✅ User approval at each critical phase
- ✅ Interactive checkbox selection
- ✅ Explicit final confirmation
- ✅ Safe archival with restoration capability
- ✅ Comprehensive error handling
- ✅ Coordination hooks integration
- ✅ Memory persistence for audit trail

## NOTES
- This workflow is REVERSIBLE - all operations use archival, not deletion
- Archive location: `.archive/cleanup-${timestamp}/`
- Restoration script generated automatically
- All operations logged to memory for audit trail
- Graceful degradation on errors
- Compatible with hierarchical swarm topology

---

**Remember**: Safety first - delegate, review, confirm, archive (never delete permanently).
