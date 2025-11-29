---
description: Validate MoAI-ADK installation completeness and correctness
tags: [moai, verify, validation, qa]
---

# Verify: MoAI-ADK Installation Validation

Comprehensive validation of MoAI-ADK installation including agents, dependencies, Korean support, and portability.

## Progressive Disclosure Structure

### Level 1: Quick Validation (Immediate Check)

Execute the `validator` agent for comprehensive validation:

```bash
# Spawn validator agent
validator --mode full --korean-fonts auto --report true
```

**Expected Duration**: 2-5 minutes
**What Gets Validated**:
- Python environment
- 26 AI agents
- Dependencies
- Korean fonts (if installed)
- Portability tests

### Level 2: Validation Categories

**Category 1: Environment Validation**
- Python version (3.13+)
- uv package manager
- Virtual environment status
- System dependencies

**Category 2: Agent Validation**
- All 26 agents present
- Agent import tests
- Agent configuration
- Entry points verification

**Category 3: Korean Support Validation** (optional)
- D2Coding font availability
- Ghostty terminal configuration
- Locale settings (ko_KR.UTF-8)
- Korean character rendering

**Category 4: Portability Validation**
- Cross-platform compatibility
- Path resolution tests
- File system operations
- Environment variable handling

### Level 3: Detailed Validation Workflow

**Phase 1: Environment Checks**
```bash
echo "=== Environment Validation ==="
npx claude-flow@alpha hooks pre-task --description "MoAI-ADK validation"

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
python_major=$(echo "$python_version" | cut -d. -f1)
python_minor=$(echo "$python_version" | cut -d. -f2)

if [[ "$python_major" -eq 3 && "$python_minor" -ge 13 ]]; then
  echo "✓ Python $python_version (OK)"
else
  echo "✗ Python $python_version (Required: 3.13+)"
  exit 1
fi

# Check uv installation
if command -v uv &> /dev/null; then
  uv_version=$(uv --version | awk '{print $2}')
  echo "✓ uv $uv_version (OK)"
else
  echo "✗ uv not found (Required: latest)"
  exit 1
fi

# Check virtual environment
if [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then
  echo "✓ Virtual environment exists (OK)"
  source .venv/bin/activate
else
  echo "✗ Virtual environment not found"
  exit 1
fi

# Check Git
if command -v git &> /dev/null; then
  git_version=$(git --version | awk '{print $3}')
  echo "✓ Git $git_version (OK)"
else
  echo "⚠ Git not found (Optional)"
fi

echo ""
```

**Phase 2: Dependency Validation**
```bash
echo "=== Dependency Validation ==="

# Verify MoAI-ADK installation
if python -c "import moai_adk" 2>/dev/null; then
  moai_version=$(python -c "import moai_adk; print(moai_adk.__version__)" 2>/dev/null || echo "unknown")
  echo "✓ MoAI-ADK $moai_version installed (OK)"
else
  echo "✗ MoAI-ADK not found (Run /install)"
  exit 1
fi

# Check core dependencies
dependencies=(
  "click"
  "pydantic"
  "rich"
  "typer"
  "httpx"
)

for dep in "${dependencies[@]}"; do
  if python -c "import $dep" 2>/dev/null; then
    dep_version=$(python -c "import $dep; print($dep.__version__)" 2>/dev/null || echo "OK")
    echo "✓ $dep $dep_version"
  else
    echo "✗ $dep not found"
  fi
done

echo ""
```

**Phase 3: Agent Validation**
```bash
echo "=== Agent Validation (26 agents) ==="

# Define expected agents by category
declare -A agent_categories=(
  ["Core Coordinators"]="hierarchical mesh adaptive collective memory"
  ["Consensus Agents"]="byzantine raft gossip crdt quorum security"
  ["Performance Agents"]="analyzer benchmarker orchestrator smart"
  ["Development Agents"]="coder reviewer tester planner researcher"
  ["Specialized Agents"]="backend mobile ml cicd apidocs architect"
  ["SPARC Agents"]="specification pseudocode architecture refinement"
  ["GitHub Agents"]="github pr-manager"
)

total_agents=0
total_expected=26

# Validate each category
for category in "${!agent_categories[@]}"; do
  echo "  Category: $category"
  agents=(${agent_categories[$category]})

  for agent in "${agents[@]}"; do
    # Test agent import (simplified check)
    agent_module="moai_adk.agents.${agent//-/_}"

    if python -c "import sys; from importlib import import_module; import_module('$agent_module')" 2>/dev/null; then
      echo "    ✓ $agent"
      ((total_agents++))
    else
      # Try alternative import path
      if python -c "from moai_adk.agents import get_agent; get_agent('$agent')" 2>/dev/null; then
        echo "    ✓ $agent (via registry)"
        ((total_agents++))
      else
        echo "    ✗ $agent (not found)"
      fi
    fi
  done
done

echo ""
echo "Agent Summary: $total_agents/$total_expected available"

if [ "$total_agents" -eq "$total_expected" ]; then
  echo "✓ All agents verified (OK)"
else
  echo "⚠ Warning: Expected $total_expected agents, found $total_agents"
fi

echo ""
```

**Phase 4: Korean Support Validation** (optional)
```bash
echo "=== Korean Support Validation ==="

korean_support=false

# Check D2Coding font
if fc-list | grep -qi "d2coding"; then
  echo "✓ D2Coding font installed"
  korean_support=true
else
  echo "⚠ D2Coding font not found (Optional)"
fi

# Check Noto Sans KR
if fc-list | grep -qi "noto.*kr"; then
  echo "✓ Noto Sans KR font installed"
else
  echo "⚠ Noto Sans KR not found (Optional)"
fi

# Check Ghostty configuration
ghostty_config="$HOME/.config/ghostty/config"
if [ -f "$ghostty_config" ]; then
  if grep -q "D2Coding" "$ghostty_config"; then
    echo "✓ Ghostty configured with D2Coding"
  else
    echo "⚠ Ghostty config exists but D2Coding not set"
  fi
else
  echo "⚠ Ghostty config not found (Optional)"
fi

# Check Korean locale
current_locale=$(locale | grep "LANG=" | cut -d= -f2)
if [[ "$current_locale" == *"ko_KR"* ]]; then
  echo "✓ Korean locale active ($current_locale)"
  korean_support=true
elif locale -a | grep -qi "ko_KR"; then
  echo "⚠ Korean locale available but not active"
  echo "  Run: export LANG=ko_KR.UTF-8"
else
  echo "⚠ Korean locale not available (Optional)"
fi

# Test Korean character rendering
echo ""
echo "Korean Character Rendering Test:"
cat > /tmp/korean_render_test.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

test_strings = [
    "한글 테스트",
    "MoAI-ADK 설치 완료",
    "가나다라마바사",
    "Agent: 조정자"
]

print("Korean Rendering:")
for s in test_strings:
    try:
        print(f"  {s}")
    except UnicodeEncodeError:
        print(f"  ✗ Encoding error")
        sys.exit(1)

print("\n✓ Korean rendering successful")
EOF

if python /tmp/korean_render_test.py 2>/dev/null; then
  echo "✓ Korean character rendering works"
else
  echo "✗ Korean rendering failed (check locale/fonts)"
fi

# Korean support summary
if [ "$korean_support" = true ]; then
  echo ""
  echo "✓ Korean support fully configured"
else
  echo ""
  echo "⚠ Korean support partial or not configured"
  echo "  Run: /install-korean to add Korean support"
fi

echo ""
```

**Phase 5: Portability Tests**
```bash
echo "=== Portability Tests ==="

# Run pytest portability tests
if [ -d "tests/portability" ]; then
  echo "Running portability test suite..."

  if uv run pytest tests/portability/ -v --tb=short 2>&1 | tee /tmp/portability_results.txt; then
    echo "✓ All portability tests passed"
  else
    echo "⚠ Some portability tests failed"
    echo "See /tmp/portability_results.txt for details"
  fi
else
  echo "⚠ Portability tests not found (tests/portability/)"
fi

echo ""
```

**Phase 6: Integration Tests** (quick smoke tests)
```bash
echo "=== Integration Tests ==="

# Test agent imports
echo "Testing agent imports..."
python << 'EOF'
from moai_adk.agents import (
    get_agent,
    list_agents,
    get_agent_by_category
)

# List all agents
agents = list_agents()
print(f"  Total agents: {len(agents)}")

# Test core agent retrieval
core_agents = ["hierarchical", "coder", "tester"]
for agent_name in core_agents:
    try:
        agent = get_agent(agent_name)
        print(f"  ✓ {agent_name}: {agent.__class__.__name__}")
    except Exception as e:
        print(f"  ✗ {agent_name}: {str(e)}")
EOF

echo ""
```

**Phase 7: Generate Validation Report**
```bash
echo "=== Validation Report ==="

# Create report
report_file="/tmp/moai-adk-validation-report.txt"
cat > "$report_file" << EOF
MoAI-ADK Installation Validation Report
========================================
Generated: $(date)

Environment:
  - Python: $python_version
  - uv: ${uv_version:-not found}
  - Git: ${git_version:-not found}
  - OS: $(uname -s) $(uname -r)

Installation:
  - MoAI-ADK: ${moai_version:-unknown}
  - Virtual Environment: $([ -d ".venv" ] && echo "Yes" || echo "No")
  - Installation Path: $(pwd)

Agents:
  - Total Verified: $total_agents/$total_expected
  - Status: $([ "$total_agents" -eq "$total_expected" ] && echo "PASS" || echo "FAIL")

Korean Support:
  - D2Coding Font: $(fc-list | grep -qi "d2coding" && echo "Yes" || echo "No")
  - Ghostty Config: $([ -f "$ghostty_config" ] && echo "Yes" || echo "No")
  - Korean Locale: ${current_locale:-not set}
  - Overall Status: $([ "$korean_support" = true ] && echo "CONFIGURED" || echo "NOT CONFIGURED")

Portability Tests:
  - Test Directory: $([ -d "tests/portability" ] && echo "Found" || echo "Not Found")
  - Results: See /tmp/portability_results.txt

Next Steps:
EOF

# Add recommendations based on validation results
if [ "$total_agents" -lt "$total_expected" ]; then
  echo "  - ⚠ Reinstall MoAI-ADK: /install" >> "$report_file"
fi

if [ "$korean_support" != true ]; then
  echo "  - ⚠ Add Korean support: /install-korean" >> "$report_file"
fi

echo "  - ✓ Review full report: $report_file" >> "$report_file"

# Display report
cat "$report_file"

# Update coordination hooks
npx claude-flow@alpha hooks post-task --task-id "moai-adk-verify"

echo ""
echo "Validation report saved to: $report_file"
```

### Level 4: Troubleshooting Validation Failures

**Issue 1: Agent Import Failures**
```bash
Problem: Cannot import specific agents
Diagnosis:
  python -c "from moai_adk.agents import list_agents; print(list_agents())"

Solution:
  # Reinstall with verbose output
  uv sync --all-extras --verbose

  # Check entry points
  python -m pip show moai-adk
```

**Issue 2: Portability Test Failures**
```bash
Problem: Portability tests fail
Diagnosis:
  uv run pytest tests/portability/ -v --tb=long

Solution:
  # Update test dependencies
  uv pip install pytest pytest-cov pytest-xdist

  # Run specific failing test
  uv run pytest tests/portability/test_failing.py -v
```

**Issue 3: Korean Font Not Detected**
```bash
Problem: fc-list doesn't show D2Coding
Diagnosis:
  fc-list | grep -i coding
  fc-cache -v

Solution:
  # Rebuild font cache
  fc-cache -f -v

  # Reinstall font
  brew reinstall --cask font-d2coding  # macOS
```

**Issue 4: Validation Report Empty**
```bash
Problem: Report file has no content
Diagnosis:
  cat /tmp/moai-adk-validation-report.txt

Solution:
  # Re-run validation with debug
  bash -x /verify > /tmp/verify-debug.log 2>&1
  cat /tmp/verify-debug.log
```

### Level 5: Expert Mode (Custom Validation)

**Custom Agent Validation**:
```python
# Validate specific agent categories
from moai_adk.agents import get_agent_by_category

categories = ["core", "consensus", "performance", "development"]
for cat in categories:
    agents = get_agent_by_category(cat)
    print(f"{cat}: {len(agents)} agents")
    for agent in agents:
        print(f"  - {agent.name}: {agent.status}")
```

**Performance Benchmarking**:
```bash
# Run performance validation
uv run pytest tests/performance/ --benchmark-only

# Generate benchmark report
uv run pytest tests/ --benchmark-json=/tmp/benchmark.json
```

**Security Validation**:
```bash
# Check for security issues
uv run safety check
uv run bandit -r src/moai_adk/

# Audit dependencies
uv pip audit
```

## Validation Success Criteria

Installation validation passes when:
- ✓ Python 3.13+ environment active
- ✓ uv package manager installed
- ✓ MoAI-ADK package importable
- ✓ 26/26 agents verified
- ✓ Core dependencies present
- ✓ Portability tests passing (if available)
- ✓ Korean support configured (if installed)

## Validation Outputs

**Console Output**: Real-time validation progress
**Report File**: `/tmp/moai-adk-validation-report.txt`
**Test Results**: `/tmp/portability_results.txt`
**Debug Log**: `/tmp/verify-debug.log` (if errors)

## Next Steps After Validation

**If All Checks Pass**:
```bash
# Start using MoAI-ADK
source .venv/bin/activate
python -m moai_adk.cli --help
```

**If Korean Support Missing**:
```bash
/install-korean
```

**If Agents Missing**:
```bash
/install --force-reinstall
```

**If Tests Failing**:
```bash
# Review test output
cat /tmp/portability_results.txt

# Fix and re-run
uv run pytest tests/portability/ -v
```

---

**Validation Type**: Comprehensive (environment, agents, Korean, portability)
**Estimated Time**: 2-5 minutes
**Agent**: `validator` (Haiku 4.5)
**Report Location**: `/tmp/moai-adk-validation-report.txt`
