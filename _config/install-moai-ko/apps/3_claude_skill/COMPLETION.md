# Post-Installation Guide & Completion Checklist

Comprehensive guide for what to do after successfully installing MoAI-ADK via the Claude Skill installer.

## Installation Verification

### Quick Verification

Ask Claude:
```
"Verify MoAI-ADK installation"
```

Claude will check:
- ✓ Configuration directory exists (`~/.moai`)
- ✓ MoAI-ADK package is importable
- ✓ Korean support (if installed)
- ✓ UV package manager
- ✓ Activation script

### Manual Verification

```bash
# Check Python import
python3 -c "import moai_adk; print(f'Version: {moai_adk.__version__}')"

# Check configuration
cat ~/.moai/config/settings.json

# Check logs
tail -n 50 ~/.moai/logs/installer.log
```

**Expected output:**
```
Version: 1.0.0
```

### Korean Support Verification

```bash
# Check Korean fonts (macOS/Linux)
fc-list | grep -i nanum

# Check Korean configuration
cat ~/.moai/config/settings.json | grep korean

# Test Korean text
python3 -c "
import moai_adk
text = '안녕하세요, MoAI-ADK입니다.'
result = moai_adk.process_korean_text(text)
print(result)
"
```

## Environment Setup

### Activate MoAI Environment

```bash
# Source activation script
source ~/.moai/activate.sh

# Verify environment variables
echo $MOAI_CONFIG_DIR
echo $MOAI_CACHE_DIR
echo $MOAI_LOG_DIR
```

**Add to shell configuration (permanent):**

```bash
# For Zsh
echo 'source ~/.moai/activate.sh' >> ~/.zshrc

# For Bash
echo 'source ~/.moai/activate.sh' >> ~/.bashrc
```

### Path Configuration

Ensure UV is in PATH:

```bash
# Check if UV is accessible
which uv

# If not found, add to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Make permanent
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
```

## Configuration

### Basic Configuration

Edit `~/.moai/config/settings.json`:

```json
{
  "language": "en_US",
  "locale": "en_US.UTF-8",
  "encoding": "UTF-8",
  "ui": {
    "font_family": "Helvetica",
    "font_size": 14,
    "theme": "light"
  },
  "features": {
    "korean_nlp": false,
    "korean_tokenizer": false,
    "auto_update": true,
    "telemetry": false
  },
  "models": {
    "default_provider": "openai",
    "temperature": 0.7,
    "max_tokens": 2048
  }
}
```

### Korean Configuration

If Korean support was installed:

```json
{
  "language": "ko_KR",
  "locale": "ko_KR.UTF-8",
  "encoding": "UTF-8",
  "ui": {
    "font_family": "Nanum Gothic",
    "font_size": 14,
    "theme": "light"
  },
  "features": {
    "korean_nlp": true,
    "korean_tokenizer": true,
    "korean_morphology": true,
    "korean_sentiment": true
  }
}
```

### Advanced Configuration

```json
{
  "cache": {
    "enabled": true,
    "max_size_mb": 1000,
    "ttl_hours": 24
  },
  "logging": {
    "level": "INFO",
    "file": "~/.moai/logs/moai.log",
    "max_size_mb": 10,
    "backup_count": 5
  },
  "agents": {
    "max_concurrent": 10,
    "timeout_seconds": 300,
    "retry_attempts": 3
  },
  "mixture": {
    "default_strategy": "weighted_voting",
    "aggregation_method": "confidence_weighted"
  }
}
```

## First Steps with MoAI-ADK

### 1. Test Basic Import

```python
import moai_adk

# Check version
print(f"MoAI-ADK version: {moai_adk.__version__}")

# Load configuration
config = moai_adk.config.load()
print(f"Language: {config.language}")
print(f"Features: {config.features}")
```

### 2. Create Your First Agent

```python
from moai_adk import Agent

# Create a simple agent
agent = Agent(
    name="MyFirstAgent",
    role="assistant",
    model="gpt-4",
    temperature=0.7
)

# Test the agent
response = agent.process("Hello, MoAI-ADK!")
print(response)
```

### 3. Test Korean NLP (if installed)

```python
from moai_adk import korean

# Tokenize Korean text
text = "안녕하세요, MoAI-ADK를 사용해 주셔서 감사합니다."
tokens = korean.tokenize(text)
print(f"Tokens: {tokens}")

# Morphological analysis
morphemes = korean.analyze_morphology(text)
print(f"Morphemes: {morphemes}")

# Sentiment analysis
sentiment = korean.analyze_sentiment(text)
print(f"Sentiment: {sentiment}")
```

### 4. Create a Multi-Agent Mixture

```python
from moai_adk import Agent, Mixture

# Create multiple agents
agent1 = Agent(name="Expert1", model="gpt-4")
agent2 = Agent(name="Expert2", model="claude-3-sonnet")
agent3 = Agent(name="Expert3", model="gemini-pro")

# Create mixture
mixture = Mixture(
    agents=[agent1, agent2, agent3],
    strategy="weighted_voting",
    weights=[0.4, 0.4, 0.2]
)

# Process with mixture
result = mixture.process("Explain quantum computing")
print(result)
```

## Project Integration

### Create a New Project

```bash
# Create project directory
mkdir my-moai-project
cd my-moai-project

# Initialize MoAI project
python3 -c "
from moai_adk import Project

project = Project.create(
    name='my-moai-project',
    description='My first MoAI-ADK project',
    korean_support=True
)

print('Project created!')
"
```

### Project Structure

```
my-moai-project/
├── .moai/
│   ├── config.json          # Project-specific config
│   └── agents/              # Agent definitions
├── src/
│   └── main.py              # Main application
├── tests/
│   └── test_agents.py       # Tests
└── README.md
```

### Example Project (`src/main.py`)

```python
from moai_adk import Agent, Mixture, Pipeline

def main():
    # Create agents
    researcher = Agent(
        name="Researcher",
        role="research",
        model="gpt-4"
    )

    writer = Agent(
        name="Writer",
        role="content_creation",
        model="claude-3-sonnet"
    )

    editor = Agent(
        name="Editor",
        role="editing",
        model="gpt-4"
    )

    # Create pipeline
    pipeline = Pipeline([
        researcher,
        writer,
        editor
    ])

    # Process
    topic = "Artificial Intelligence in Healthcare"
    result = pipeline.process(topic)

    print(result)

if __name__ == "__main__":
    main()
```

## Korean Language Usage

### Korean Text Processing

```python
from moai_adk import korean

# Example Korean text
text = """
인공지능 기술이 빠르게 발전하고 있습니다.
특히 자연어 처리 분야에서 큰 진전이 있었습니다.
"""

# Sentence segmentation
sentences = korean.segment_sentences(text)
for i, sentence in enumerate(sentences, 1):
    print(f"{i}. {sentence}")

# Word tokenization
words = korean.tokenize_words(text)
print(f"Words: {words}")

# Named entity recognition
entities = korean.extract_entities(text)
print(f"Entities: {entities}")
```

### Korean-English Translation

```python
from moai_adk import Agent

# Create translation agent
translator = Agent(
    name="Translator",
    role="translation",
    model="gpt-4",
    system_prompt="You are a professional Korean-English translator."
)

# Translate Korean to English
korean_text = "안녕하세요, 반갑습니다."
english = translator.process(f"Translate to English: {korean_text}")
print(f"English: {english}")

# Translate English to Korean
english_text = "Hello, nice to meet you."
korean = translator.process(f"Translate to Korean: {english_text}")
print(f"Korean: {korean}")
```

## Completion Checklist

### Essential Steps

- [ ] **Installation verified** (`python3 -c "import moai_adk"`)
- [ ] **Environment activated** (`source ~/.moai/activate.sh`)
- [ ] **Configuration reviewed** (`~/.moai/config/settings.json`)
- [ ] **Korean support tested** (if installed)
- [ ] **First agent created** and tested
- [ ] **Documentation reviewed**

### Optional Steps

- [ ] **Project created** with MoAI-ADK structure
- [ ] **Korean NLP tested** (if needed)
- [ ] **Multi-agent mixture** created
- [ ] **Pipeline configured** for workflow
- [ ] **Tests written** for agents
- [ ] **Git repository** initialized

### Configuration Steps

- [ ] **Shell activation** added to `.zshrc`/`.bashrc`
- [ ] **UV in PATH** verified
- [ ] **Custom settings** configured
- [ ] **Logging** configured
- [ ] **Cache settings** optimized

### Learning Steps

- [ ] **Documentation** read (`moai-adk docs`)
- [ ] **Examples** reviewed
- [ ] **Tutorials** completed
- [ ] **Community** joined (if available)

## Next Steps

### 1. Explore Examples

Ask Claude:
```
"Show me MoAI-ADK examples"
"How do I create a multi-agent system?"
"Demonstrate Korean NLP features"
```

### 2. Build Your Application

```
"Help me build a chatbot with MoAI-ADK"
"Create a document analysis pipeline"
"Set up a Korean language sentiment analyzer"
```

### 3. Customize Configuration

```
"Change MoAI-ADK UI font to Malgun Gothic"
"Enable debug logging"
"Configure agent timeout settings"
```

### 4. Troubleshoot Issues

```
"Why isn't Korean text displaying correctly?"
"How do I update MoAI-ADK?"
"The agent is timing out, how do I fix it?"
```

## Common Tasks

### Update MoAI-ADK

Ask Claude:
```
"Update MoAI-ADK to the latest version"
```

Or manually:
```bash
uv pip install --upgrade moai-adk
```

### Uninstall MoAI-ADK

Ask Claude:
```
"Uninstall MoAI-ADK"
```

Or manually:
```bash
uv pip uninstall moai-adk
rm -rf ~/.moai
```

### Backup Configuration

```bash
# Backup entire config directory
tar -czf moai-backup-$(date +%Y%m%d).tar.gz ~/.moai

# Restore from backup
tar -xzf moai-backup-20250129.tar.gz -C ~/
```

### Reset to Defaults

Ask Claude:
```
"Reset MoAI-ADK configuration to defaults"
```

Or manually:
```bash
rm ~/.moai/config/settings.json
# Reinstall to recreate defaults
```

## Troubleshooting

### Issue: Import Error

```python
# Error: ModuleNotFoundError: No module named 'moai_adk'

# Solution 1: Verify installation
uv pip list | grep moai-adk

# Solution 2: Reinstall
uv pip install --force-reinstall moai-adk
```

### Issue: Korean Fonts Not Displaying

```
# Check fonts
fc-list | grep -i nanum

# Reinstall fonts
Ask Claude: "Reinstall Korean fonts for MoAI-ADK"
```

### Issue: Configuration Not Loading

```python
# Check config file
cat ~/.moai/config/settings.json

# Validate JSON
python3 -m json.tool ~/.moai/config/settings.json

# Recreate if invalid
Ask Claude: "Reset MoAI-ADK configuration"
```

## Learning Resources

### Documentation

```python
# Access documentation
import moai_adk
help(moai_adk)

# Specific modules
help(moai_adk.Agent)
help(moai_adk.Mixture)
help(moai_adk.korean)
```

### Interactive Help via Claude

```
"Show me MoAI-ADK documentation for Agents"
"How do I use the Mixture class?"
"What are the available Korean NLP features?"
"Explain mixture strategies"
```

### Example Projects

Ask Claude:
```
"Create an example MoAI-ADK project for document analysis"
"Build a multi-agent research assistant"
"Set up Korean chatbot with MoAI-ADK"
```

## Best Practices

### 1. Configuration Management

- Keep `settings.json` in version control
- Document custom configurations
- Use environment-specific configs

### 2. Agent Design

- Give agents clear roles
- Use appropriate models for tasks
- Set reasonable timeouts
- Handle errors gracefully

### 3. Korean Language

- Use UTF-8 encoding consistently
- Test with Korean fonts
- Validate Korean text processing
- Consider locale settings

### 4. Performance

- Enable caching for repeated tasks
- Use appropriate model sizes
- Implement rate limiting
- Monitor resource usage

## Support

### Ask Claude

```
"I have a question about MoAI-ADK"
"How do I [specific task]?"
"Why is [feature] not working?"
"Show me examples of [use case]"
```

### Check Logs

```bash
# Installation logs
cat ~/.moai/logs/installer.log

# Application logs
cat ~/.moai/logs/moai.log

# Debug logs
tail -f ~/.moai/logs/moai.log
```

### Community Resources

- MoAI-ADK GitHub repository
- Documentation website
- Example projects
- Community forums (if available)

## Conclusion

You've successfully completed MoAI-ADK installation!

**Key achievements:**
- ✓ MoAI-ADK installed and verified
- ✓ Environment configured
- ✓ Korean support (if applicable)
- ✓ Ready to build AI applications

**Next steps:**
1. Create your first agent
2. Experiment with mixtures
3. Build a project
4. Explore Korean NLP features

**Remember:**
- Ask Claude for help anytime
- Check documentation regularly
- Experiment with different approaches
- Share your creations!

---

**Happy building with MoAI-ADK! 🚀**
