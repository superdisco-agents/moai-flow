# AI Documentation Index - MoAI-ADK

**Version**: 1.0.0
**Last Updated**: November 29, 2025
**Purpose**: Machine-readable documentation for AI assistants

## 📋 Overview

This directory contains AI-optimized documentation for MoAI-ADK (Mixture of Agents - Agent Development Kit), designed for easy parsing and understanding by AI language models and automated systems.

**Target Audience**: AI assistants, chatbots, documentation scrapers, and automated tools

---

## 📚 Available Documentation

### **Core Guides**

1. **moai-adk-guide.md** (~420 lines)
   - Complete MoAI-ADK overview
   - SPEC-First methodology explanation
   - TDD workflow guide
   - 26 agents reference
   - Quick start examples
   - **Use Case**: Understanding MoAI-ADK fundamentals

2. **korean-setup.md** (~400 lines)
   - Korean language support configuration
   - D2Coding font installation
   - Terminal configuration for Korean
   - Locale setup
   - Character encoding
   - **Use Case**: Setting up Korean language environment

3. **uv-inline-dependencies.md** (~400 lines)
   - UV package manager guide
   - PEP 723 inline dependencies explanation
   - Dependency management strategies
   - Migration from pip to UV
   - **Use Case**: Modern Python dependency management

---

## 🎯 Documentation Structure

### **Format Standards**

All AI documentation follows these conventions:

- **Format**: Markdown (.md)
- **Encoding**: UTF-8
- **Line Length**: No hard limit (optimized for readability)
- **Code Blocks**: Clearly marked with language identifiers
- **Headers**: Hierarchical with emoji indicators
- **Examples**: Practical, executable code snippets

### **Progressive Disclosure**

Documentation uses progressive disclosure pattern:

1. **Overview**: Quick summary and purpose
2. **Quick Reference**: Essential information
3. **Detailed Explanation**: In-depth coverage
4. **Examples**: Practical use cases
5. **Advanced Topics**: Expert-level content
6. **Troubleshooting**: Common issues and solutions

---

## 🤖 AI Assistant Integration

### **Recommended Usage**

When an AI assistant needs to help with MoAI-ADK:

```python
# Example: AI assistant workflow
def assist_with_moai_adk(user_query):
    # 1. Identify topic
    if "installation" in user_query:
        reference = "moai-adk-guide.md"
    elif "korean" in user_query:
        reference = "korean-setup.md"
    elif "dependencies" or "uv" in user_query:
        reference = "uv-inline-dependencies.md"

    # 2. Load relevant documentation
    content = load_documentation(reference)

    # 3. Extract relevant sections
    relevant_info = extract_sections(content, user_query)

    # 4. Generate response
    return generate_response(relevant_info, user_query)
```

### **Key Information Extraction**

Each document supports easy extraction of:

- **Commands**: Shell commands clearly marked in code blocks
- **Configuration**: YAML/JSON snippets with clear labels
- **Examples**: Practical examples with expected outputs
- **Errors**: Common error messages and solutions
- **Versions**: Version compatibility information

---

## 📖 Document Summaries

### **moai-adk-guide.md**

**Topics Covered**:
- MoAI-ADK overview and architecture
- SPEC-First workflow (phases 0-4)
- TDD workflow (phases 10-14)
- Development agents (phases 20-24)
- Analysis agents (phases 30-34)
- Command reference for all 26 agents
- Korean language support
- Installation quick start
- Common workflows

**Best For**:
- Understanding what MoAI-ADK does
- Learning SPEC-First methodology
- Agent command reference
- Quick start tutorials

**Key Sections**:
```markdown
## Quick Start
## SPEC-First Methodology
## 26 Agents Reference
## Command Examples
## Workflows
```

---

### **korean-setup.md**

**Topics Covered**:
- Why Korean support matters
- D2Coding font installation (all platforms)
- Terminal configuration (Ghostty, iTerm2, GNOME, etc.)
- Locale configuration (macOS, Linux)
- Character encoding setup
- UTF-8 configuration
- Troubleshooting Korean display

**Best For**:
- Setting up Korean language support
- Fixing Korean character display issues
- Configuring terminals for CJK
- Font installation guidance

**Key Sections**:
```markdown
## D2Coding Font Installation
## Terminal Configuration
## Locale Setup
## Encoding Configuration
## Troubleshooting
```

---

### **uv-inline-dependencies.md**

**Topics Covered**:
- UV package manager overview
- PEP 723 inline dependencies
- UV vs pip comparison
- Installation and setup
- Dependency management
- Virtual environment creation
- Migration strategies
- Performance benefits

**Best For**:
- Understanding UV package manager
- Learning PEP 723 inline scripts
- Migrating from pip to UV
- Performance optimization

**Key Sections**:
```markdown
## UV Overview
## PEP 723 Explained
## Installation
## Usage Examples
## Migration Guide
## Performance Comparison
```

---

## 🔍 Search & Query Patterns

### **Common AI Queries**

| Query Type | Recommended Document | Key Section |
|------------|---------------------|-------------|
| "How to install MoAI-ADK?" | moai-adk-guide.md | Quick Start |
| "What is SPEC-First?" | moai-adk-guide.md | SPEC-First Methodology |
| "List all MoAI agents" | moai-adk-guide.md | 26 Agents Reference |
| "Korean characters not working" | korean-setup.md | Troubleshooting |
| "Install D2Coding font" | korean-setup.md | Font Installation |
| "What is UV?" | uv-inline-dependencies.md | UV Overview |
| "How to use PEP 723?" | uv-inline-dependencies.md | PEP 723 Explained |
| "Migrate from pip to UV" | uv-inline-dependencies.md | Migration Guide |

### **Keyword Index**

**Installation Keywords**:
- `install`, `setup`, `installation`, `quick start`, `getting started`
- → **moai-adk-guide.md** (Quick Start section)

**Korean Support Keywords**:
- `korean`, `한글`, `font`, `D2Coding`, `locale`, `encoding`
- → **korean-setup.md**

**Dependency Keywords**:
- `uv`, `pip`, `dependencies`, `packages`, `PEP 723`, `inline`
- → **uv-inline-dependencies.md**

**Agent Keywords**:
- `agent`, `SPEC`, `TDD`, `/moai:0`, `workflow`, `methodology`
- → **moai-adk-guide.md** (Agents section)

---

## 💾 Data Extraction

### **Structured Data Available**

Each document contains extractable structured data:

#### **Commands**
```bash
# All shell commands are in code blocks
./moai.sh /moai:0 "specification"
uv venv --python 3.13
brew install --cask font-d2coding
```

#### **Configuration**
```yaml
# YAML configurations
general:
  output_directory: outputs
  log_level: INFO
```

#### **Code Examples**
```python
# Python code examples
from langchain import Agent
agent = Agent(name="spec-agent")
```

#### **Version Information**
- Python: 3.11, 3.12, 3.13, 3.14
- UV: 0.5.0+
- MoAI-ADK: 1.0.0
- D2Coding Font: 1.3.2

---

## 🔗 Cross-References

### **Related Human Documentation**

AI documentation complements human-focused docs:

| AI Doc | Human Doc | Relationship |
|--------|-----------|--------------|
| moai-adk-guide.md | docs/api/moai-adk-api.md | AI summary ↔ Full API reference |
| korean-setup.md | docs/03-KOREAN-SETUP.md | AI summary ↔ Detailed guide |
| uv-inline-dependencies.md | docs/01-REQUIREMENTS.md | UV focus ↔ All requirements |

### **Navigation**

```
ai_docs/
├── README.md (you are here)
├── moai-adk-guide.md      → Core functionality
├── korean-setup.md        → Korean support
└── uv-inline-dependencies.md → Dependency management

Related human docs:
../docs/
├── 00-INSTALL-STEPS.md    → Quick installation
├── 01-REQUIREMENTS.md     → System requirements
├── 02-INSTALLATION.md     → Detailed installation
├── 03-KOREAN-SETUP.md     → Full Korean guide
├── 04-VERIFICATION.md     → Verification checklist
├── 05-TROUBLESHOOTING.md  → Problem solving
└── api/
    ├── moai-adk-api.md    → Complete API reference
    ├── korean-fonts.md    → Font specifications
    └── installation-schema.md → Installation architecture
```

---

## 🎯 Usage Examples

### **Example 1: AI Assistant Answering Installation Question**

**User**: "How do I install MoAI-ADK?"

**AI Process**:
1. Load `moai-adk-guide.md`
2. Extract "Quick Start" section
3. Format response with commands

**AI Response**:
```
To install MoAI-ADK:

1. Install UV:
   curl -LsSf https://astral.sh/uv/install.sh | sh

2. Create virtual environment:
   uv venv --python 3.13
   source .venv/bin/activate

3. Install dependencies:
   uv pip install -r requirements.txt

4. Verify:
   ./moai.sh --help

For detailed steps, see docs/00-INSTALL-STEPS.md
```

---

### **Example 2: AI Assistant Helping with Korean Setup**

**User**: "Korean characters show as boxes in my terminal"

**AI Process**:
1. Load `korean-setup.md`
2. Extract "Troubleshooting" section
3. Identify font installation issue

**AI Response**:
```
Korean characters displaying as boxes indicates missing Korean font.

Solution:

macOS:
  brew tap homebrew/cask-fonts
  brew install --cask font-d2coding

Linux:
  wget [D2Coding URL]
  sudo cp *.ttf /usr/share/fonts/truetype/
  sudo fc-cache -f -v

Then:
1. Configure terminal to use "D2Coding" font
2. Set font size to 13+
3. Restart terminal

For detailed configuration, see docs/03-KOREAN-SETUP.md
```

---

### **Example 3: AI Explaining UV and PEP 723**

**User**: "What is UV and PEP 723?"

**AI Process**:
1. Load `uv-inline-dependencies.md`
2. Extract overview and PEP 723 sections

**AI Response**:
```
UV: Modern Python package installer (10-100x faster than pip)

PEP 723: Standard for inline script dependencies
Allows specifying dependencies directly in Python files:

```python
# /// script
# dependencies = [
#   "requests",
#   "rich",
# ]
# ///

import requests
from rich import print
```

UV automatically installs these dependencies when running the script.

Benefits:
- Single-file scripts with dependencies
- No requirements.txt needed
- Automatic environment management

For more details, see ai_docs/uv-inline-dependencies.md
```

---

## 📊 Metadata

### **Document Metadata**

Each AI document includes:

```yaml
metadata:
  version: "1.0.0"
  last_updated: "2025-11-29"
  target_audience: "AI assistants"
  format: "markdown"
  encoding: "UTF-8"
  topics:
    - installation
    - korean-support
    - dependencies
  keywords:
    - MoAI-ADK
    - SPEC-First
    - TDD
    - Korean
    - UV
    - PEP-723
```

---

## 🤝 Contributing

### **For AI Documentation Updates**

When updating AI documentation:

1. **Keep it concise**: AI docs should be summaries, not exhaustive
2. **Use clear structure**: Headers, lists, code blocks
3. **Include examples**: Practical, executable code
4. **Cross-reference**: Link to detailed human docs
5. **Update metadata**: Version, date, keywords

### **Quality Standards**

- ✅ Clear, actionable information
- ✅ Code examples are tested and working
- ✅ Version information is current
- ✅ Cross-references are accurate
- ✅ Korean content is properly encoded (UTF-8)

---

## 📞 Support

For AI documentation questions:
- **Human Docs**: See `../docs/` directory
- **API Reference**: See `../docs/api/moai-adk-api.md`
- **Installation**: See `../docs/00-INSTALL-STEPS.md`

---

**AI Documentation for MoAI-ADK v1.0.0** - Optimized for AI assistants and automated tools 🤖
