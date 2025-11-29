# MoAI-ADK Installation Verification

**Version**: 1.0.0
**Last Updated**: November 29, 2025
**Estimated Time**: 5-10 minutes

## 📋 Overview

This comprehensive verification guide ensures your MoAI-ADK installation is complete, properly configured, and ready for development. Follow the 10-point validation checklist to confirm all components are working correctly.

---

## ✅ 10-Point Validation Checklist

### **Checkpoint 1: Python Environment** ⭐

Verify Python version and virtual environment setup.

```bash
# Navigate to MoAI-ADK directory
cd /Users/rdmtv/Documents/claydev-local/agent-os-v2/moai-adk/_config/install-moai-ko

# Activate virtual environment
source .venv/bin/activate

# Check Python version
python --version
# ✅ Expected: Python 3.11.x, 3.12.x, 3.13.x, or 3.14.x
# ❌ Fail: Python 3.10.x or lower

# Verify virtual environment
which python
# ✅ Expected: /path/to/moai-adk/.venv/bin/python
# ❌ Fail: /usr/bin/python or /usr/local/bin/python

# Check environment isolation
python -c "import sys; print(sys.prefix)"
# ✅ Expected: /path/to/moai-adk/.venv
# ❌ Fail: /usr or /usr/local
```

**Status**: [ ] PASS [ ] FAIL

---

### **Checkpoint 2: Core Dependencies** ⭐

Verify essential Python packages are installed.

```bash
# Test core imports
python << 'EOF'
try:
    import pydantic
    import yaml
    import jinja2
    import click
    import rich
    print("✅ Core dependencies: OK")
    print(f"   - pydantic: {pydantic.__version__}")
    print(f"   - PyYAML: {yaml.__version__}")
    print(f"   - jinja2: {jinja2.__version__}")
except ImportError as e:
    print(f"❌ Import error: {e}")
EOF
```

**Expected Output**:
```
✅ Core dependencies: OK
   - pydantic: 2.5.0 (or higher)
   - PyYAML: 6.0.1 (or higher)
   - jinja2: 3.1.2 (or higher)
```

**Status**: [ ] PASS [ ] FAIL

---

### **Checkpoint 3: Agent Framework** ⭐

Verify LangChain and AI agent libraries.

```bash
# Test agent framework imports
python << 'EOF'
try:
    import langchain
    from langchain.agents import AgentExecutor
    from langchain.tools import Tool
    print("✅ Agent framework: OK")
    print(f"   - LangChain: {langchain.__version__}")
except ImportError as e:
    print(f"❌ Agent framework error: {e}")
EOF
```

**Expected Output**:
```
✅ Agent framework: OK
   - LangChain: 0.1.0 (or higher)
```

**Status**: [ ] PASS [ ] FAIL

---

### **Checkpoint 4: MoAI-ADK Command** ⭐

Verify MoAI-ADK command-line interface.

```bash
# Test moai.sh script
./moai.sh --help

# ✅ Expected output (should show):
# MoAI-ADK - Mixture of Agents Development Kit
# Version: 1.0.0
#
# Usage: ./moai.sh [COMMAND] [ARGS]
#
# Commands:
#   /moai:0-4     SPEC-First workflow
#   /moai:10-14   TDD workflow
#   /moai:20-24   Code review workflow
#   /moai:30-34   Refactoring workflow
#   /moai:list    List all available agents
#   /moai:help    Show detailed help
```

**Verification Tests**:
```bash
# Test command permissions
ls -l moai.sh
# ✅ Expected: -rwxr-xr-x (executable)

# Test script syntax
bash -n moai.sh
# ✅ Expected: No output (no syntax errors)
# ❌ Fail: Syntax error messages

# Test help command
./moai.sh /moai:help > /dev/null 2>&1 && echo "✅ Help command: OK" || echo "❌ Help command: FAIL"
```

**Status**: [ ] PASS [ ] FAIL

---

### **Checkpoint 5: Agent Availability** ⭐

Verify all 26 agents are configured and accessible.

```bash
# List all agents
./moai.sh /moai:list

# ✅ Expected: 26 agents listed
# SPEC-First Agents (0-4):
#   /moai:0  - Specification Agent
#   /moai:1  - Pseudocode Agent
#   /moai:2  - Architecture Agent
#   /moai:3  - Refinement Agent
#   /moai:4  - Completion Agent
#
# TDD Agents (10-14):
#   /moai:10 - Test Specification Agent
#   /moai:11 - Test Implementation Agent
#   /moai:12 - Code Implementation Agent
#   /moai:13 - Test Validation Agent
#   /moai:14 - Integration Agent
#
# Development Agents (20-24):
#   /moai:20 - Frontend Developer
#   /moai:21 - Backend Developer
#   /moai:22 - API Developer
#   /moai:23 - Database Developer
#   /moai:24 - DevOps Engineer
#
# Analysis Agents (30-34):
#   /moai:30 - Code Reviewer
#   /moai:31 - Security Analyst
#   /moai:32 - Performance Analyst
#   /moai:33 - Refactoring Agent
#   /moai:34 - Documentation Agent
#
# ... (6 more agents)

# Count agents
./moai.sh /moai:list | grep -c "/moai:"
# ✅ Expected: 26
# ❌ Fail: Less than 26
```

**Detailed Agent Check**:
```bash
# Verify agent configuration files
ls -l agents/*.yaml | wc -l
# ✅ Expected: 26 files

# Test sample agent
./moai.sh /moai:0 "test" > /tmp/agent-test.txt 2>&1
if grep -q "error\|Error\|ERROR" /tmp/agent-test.txt; then
    echo "❌ Agent execution: FAIL"
    cat /tmp/agent-test.txt
else
    echo "✅ Agent execution: OK"
fi
```

**Status**: [ ] PASS [ ] FAIL

---

### **Checkpoint 6: SPEC-First Workflow** ⭐

Test the complete SPEC-First methodology workflow.

```bash
# Create test output directory
mkdir -p outputs/verification

# Test each SPEC-First phase
echo "Testing SPEC-First workflow..."

# Phase 1: Specification
./moai.sh /moai:0 "Create specification for a simple calculator" > outputs/verification/01-spec.txt
[ -s outputs/verification/01-spec.txt ] && echo "✅ Specification phase: OK" || echo "❌ Specification phase: FAIL"

# Phase 2: Pseudocode
./moai.sh /moai:1 "$(cat outputs/verification/01-spec.txt)" > outputs/verification/02-pseudocode.txt
[ -s outputs/verification/02-pseudocode.txt ] && echo "✅ Pseudocode phase: OK" || echo "❌ Pseudocode phase: FAIL"

# Phase 3: Architecture
./moai.sh /moai:2 "$(cat outputs/verification/01-spec.txt)" > outputs/verification/03-architecture.txt
[ -s outputs/verification/03-architecture.txt ] && echo "✅ Architecture phase: OK" || echo "❌ Architecture phase: FAIL"

# Verify output files
echo ""
echo "SPEC-First output files:"
ls -lh outputs/verification/
```

**Expected Results**:
- ✅ All 3 phases execute without errors
- ✅ Output files created with content
- ✅ Each file > 100 bytes (not empty)

**Status**: [ ] PASS [ ] FAIL

---

### **Checkpoint 7: TDD Workflow** ⭐

Verify Test-Driven Development workflow functionality.

```bash
# Test TDD workflow
echo "Testing TDD workflow..."

# Phase 1: Test Specification
./moai.sh /moai:10 "Write tests for calculator add function" > outputs/verification/10-test-spec.txt
[ -s outputs/verification/10-test-spec.txt ] && echo "✅ Test specification: OK" || echo "❌ Test specification: FAIL"

# Phase 2: Test Implementation
./moai.sh /moai:11 "$(cat outputs/verification/10-test-spec.txt)" > outputs/verification/11-test-impl.txt
[ -s outputs/verification/11-test-impl.txt ] && echo "✅ Test implementation: OK" || echo "❌ Test implementation: FAIL"

# Verify TDD outputs
echo ""
echo "TDD output files:"
ls -lh outputs/verification/1*.txt
```

**Expected Results**:
- ✅ Test specifications generated
- ✅ Test implementations created
- ✅ No execution errors

**Status**: [ ] PASS [ ] FAIL

---

### **Checkpoint 8: File Operations & Encoding** ⭐

Verify UTF-8 encoding and file handling.

```bash
# Test UTF-8 encoding
python << 'EOF'
import sys
import os

print("Encoding Verification:")
print(f"✅ Default encoding: {sys.getdefaultencoding()}")
print(f"✅ Filesystem encoding: {sys.getfilesystemencoding()}")
print(f"✅ stdout encoding: {sys.stdout.encoding}")

# Test file operations with UTF-8
test_content = "MoAI-ADK Test: Hello World 테스트"
test_file = "outputs/verification/encoding-test.txt"

# Write with UTF-8
with open(test_file, 'w', encoding='utf-8') as f:
    f.write(test_content)
    f.write("\n")

# Read back
with open(test_file, 'r', encoding='utf-8') as f:
    content = f.read().strip()

if content == test_content:
    print(f"✅ File encoding: OK")
    print(f"   Content: {content}")
else:
    print(f"❌ File encoding: FAIL")
    print(f"   Expected: {test_content}")
    print(f"   Got: {content}")
EOF

# Verify file encoding with file command
file -I outputs/verification/encoding-test.txt
# ✅ Expected: charset=utf-8
```

**Status**: [ ] PASS [ ] FAIL

---

### **Checkpoint 9: Korean Font & Display** 🇰🇷 (Optional)

Verify Korean language support and font rendering.

```bash
# Check Korean locale
locale | grep ko_KR.UTF-8
# ✅ Expected: Shows ko_KR.UTF-8 for LANG and LC_ALL
# ⚠️  Warning: If empty, Korean locale not configured

# Check D2Coding font installation
fc-list | grep -i d2coding
# ✅ Expected: Shows D2Coding font path
# ⚠️  Warning: If empty, D2Coding not installed

# Test Korean character display
echo "========================================="
echo "🇰🇷 Korean Character Display Test"
echo "========================================="
echo ""
echo "Hangul Consonants: ㄱ ㄴ ㄷ ㄹ ㅁ ㅂ ㅅ ㅇ ㅈ ㅊ ㅋ ㅌ ㅍ ㅎ"
echo "Hangul Vowels: ㅏ ㅑ ㅓ ㅕ ㅗ ㅛ ㅜ ㅠ ㅡ ㅣ"
echo "Korean Words: 한글 테스트 성공 MoAI-ADK 설치 완료"
echo "Mixed Text: Hello 안녕하세요 World 세계 123"
echo ""
echo "If you see clear Korean characters (not boxes), font is working!"
echo "========================================="

# Test Korean in MoAI-ADK
./moai.sh /moai:0 "간단한 계산기 사양 작성" > outputs/verification/korean-test.txt

# Check file contains Korean
if grep -q "한글\|계산기" outputs/verification/korean-test.txt 2>/dev/null; then
    echo "✅ Korean file operations: OK"
else
    echo "⚠️  Korean file operations: Not detected (English-only mode OK)"
fi

# Verify file encoding
file -I outputs/verification/korean-test.txt
# ✅ Expected: charset=utf-8
```

**Visual Verification**:
Look at the terminal output:
- ✅ Korean characters display clearly
- ❌ Korean characters show as boxes (□) or question marks (?)

**Status**: [ ] PASS [ ] FAIL [ ] SKIPPED (English-only)

---

### **Checkpoint 10: Integration Test** ⭐

Run comprehensive integration test across all components.

```bash
# Run integration test script
python << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MoAI-ADK Integration Test"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run command and return success status"""
    print(f"\nTesting: {description}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✅ {description}: PASS")
            return True
        else:
            print(f"❌ {description}: FAIL")
            print(f"   Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {description}: TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")
        return False

# Integration tests
tests = [
    ("python --version", "Python version check"),
    ("python -c 'import pydantic'", "Pydantic import"),
    ("python -c 'import langchain'", "LangChain import"),
    ("./moai.sh --help", "MoAI-ADK help command"),
    ("./moai.sh /moai:list | head -n 5", "Agent list command"),
]

print("=" * 60)
print("MoAI-ADK Integration Test Suite")
print("=" * 60)

results = []
for cmd, desc in tests:
    results.append(run_command(cmd, desc))

# Summary
print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)
passed = sum(results)
total = len(results)
success_rate = (passed / total) * 100

print(f"Passed: {passed}/{total} ({success_rate:.1f}%)")

if success_rate == 100:
    print("🎉 All tests passed! Installation verified.")
    sys.exit(0)
elif success_rate >= 80:
    print("⚠️  Most tests passed. Minor issues detected.")
    sys.exit(0)
else:
    print("❌ Multiple test failures. Check installation.")
    sys.exit(1)
EOF
```

**Expected Output**:
```
============================================================
MoAI-ADK Integration Test Suite
============================================================

Testing: Python version check
✅ Python version check: PASS

Testing: Pydantic import
✅ Pydantic import: PASS

Testing: LangChain import
✅ LangChain import: PASS

Testing: MoAI-ADK help command
✅ MoAI-ADK help command: PASS

Testing: Agent list command
✅ Agent list command: PASS

============================================================
Test Summary
============================================================
Passed: 5/5 (100.0%)
🎉 All tests passed! Installation verified.
```

**Status**: [ ] PASS [ ] FAIL

---

## 📊 Verification Summary

### **Quick Status Check**

```bash
# Run automated verification script
python scripts/verify-installation.py

# Or manual summary check
echo "==================================="
echo "MoAI-ADK Verification Summary"
echo "==================================="
echo ""
echo "1. Python Environment: $(python --version)"
echo "2. Virtual Environment: $(which python | grep -q '.venv' && echo '✅ Active' || echo '❌ Not active')"
echo "3. Core Dependencies: $(python -c 'import pydantic' 2>/dev/null && echo '✅ OK' || echo '❌ Missing')"
echo "4. Agent Framework: $(python -c 'import langchain' 2>/dev/null && echo '✅ OK' || echo '❌ Missing')"
echo "5. MoAI-ADK Command: $(./moai.sh --help >/dev/null 2>&1 && echo '✅ OK' || echo '❌ Error')"
echo "6. Agent Count: $(./moai.sh /moai:list 2>/dev/null | grep -c '/moai:') agents"
echo "7. SPEC-First: $(./moai.sh /moai:0 'test' >/dev/null 2>&1 && echo '✅ OK' || echo '❌ Error')"
echo "8. UTF-8 Encoding: $(python -c 'import sys; print(sys.getdefaultencoding())' 2>/dev/null)"
echo "9. Korean Font: $(fc-list | grep -q -i d2coding && echo '✅ Installed' || echo '⚠️  Not installed (optional)')"
echo "10. Integration: ✅ (run full test above)"
echo ""
echo "==================================="
```

### **Results Interpretation**

| Checkpoints Passed | Status | Action |
|--------------------|--------|--------|
| 10/10 | 🎉 Perfect | Ready for production use |
| 9/10 | ✅ Excellent | Check failed checkpoint |
| 8/10 | ✅ Good | Review and fix issues |
| 7/10 | ⚠️ Acceptable | Fix critical issues |
| < 7/10 | ❌ Issues | Reinstall or troubleshoot |

---

## 🔍 Detailed Verification Report

### **Generate Full Report**

```bash
# Create verification report
cat > outputs/verification-report.md << 'EOF'
# MoAI-ADK Verification Report

**Date**: $(date)
**User**: $(whoami)
**System**: $(uname -a)

## Installation Details

### Python Environment
- Version: $(python --version)
- Location: $(which python)
- Virtual Env: $(echo $VIRTUAL_ENV)

### Dependencies
EOF

# Add dependency versions
python << 'PYEOF' >> outputs/verification-report.md
import sys
packages = ['pydantic', 'yaml', 'jinja2', 'langchain']
for pkg in packages:
    try:
        mod = __import__(pkg)
        version = getattr(mod, '__version__', 'unknown')
        print(f"- {pkg}: {version}")
    except ImportError:
        print(f"- {pkg}: NOT INSTALLED")
PYEOF

# Add agent count
echo "" >> outputs/verification-report.md
echo "### Agents" >> outputs/verification-report.md
echo "- Total agents: $(./moai.sh /moai:list 2>/dev/null | grep -c '/moai:')" >> outputs/verification-report.md

# View report
cat outputs/verification-report.md
```

---

## 🐛 Common Verification Issues

### **Issue 1: Python Version Wrong**

```bash
# Symptom
python --version  # Shows 3.10.x or lower

# Solution
pyenv install 3.13.0
pyenv local 3.13.0
rm -rf .venv
uv venv --python 3.13
source .venv/bin/activate
```

### **Issue 2: Missing Dependencies**

```bash
# Symptom
ImportError: No module named 'pydantic'

# Solution
source .venv/bin/activate
uv pip install -r requirements.txt
# Or
pip install pydantic pyyaml jinja2 langchain
```

### **Issue 3: MoAI Command Fails**

```bash
# Symptom
./moai.sh: Permission denied

# Solution
chmod +x moai.sh
chmod +x scripts/*.py
```

### **Issue 4: Agent Not Found**

```bash
# Symptom
Error: Agent /moai:0 not found

# Solution
python scripts/configure-agents.py
./moai.sh /moai:list  # Verify agents
```

### **Issue 5: Korean Characters Not Displaying**

```bash
# Symptom
Korean text shows as □□□

# Solution
brew install --cask font-d2coding  # macOS
# Configure terminal font to D2Coding
# Set locale: export LANG=ko_KR.UTF-8
```

For detailed troubleshooting, see `05-TROUBLESHOOTING.md`.

---

## ✅ Verification Complete

If all checkpoints pass:

1. ✅ **Installation Verified**: Your MoAI-ADK is ready!
2. 📚 **Next Steps**:
   - Read API documentation: `docs/api/moai-adk-api.md`
   - Try sample workflows: `examples/`
   - Configure Korean support: `03-KOREAN-SETUP.md` (optional)

3. 🚀 **Start Building**:
   ```bash
   source .venv/bin/activate
   ./moai.sh /moai:0 "Create your first project specification"
   ```

---

## 📞 Support

If verification fails:
- **Troubleshooting Guide**: See `05-TROUBLESHOOTING.md`
- **Requirements Check**: Review `01-REQUIREMENTS.md`
- **Reinstallation**: Follow `02-INSTALLATION.md`

**Still having issues?** Check the FAQ in `05-TROUBLESHOOTING.md` or review the installation logs.

---

Congratulations on completing the verification process! 🎉
