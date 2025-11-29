# MoAI-ADK API Reference

**Version**: 1.0.0
**Last Updated**: November 29, 2025

## 📋 Overview

MoAI-ADK (Mixture of Agents - Agent Development Kit) provides a comprehensive SPEC-First/TDD development framework with 26 specialized agents and Korean language support.

**Core Capabilities**:
- 🔧 SPEC-First methodology (phases 0-4)
- 🧪 Test-Driven Development workflow (phases 10-14)
- 👨‍💻 Full-stack development agents (phases 20-24)
- 📊 Code analysis and refactoring (phases 30-34)
- 🇰🇷 Korean language support (optional)

---

## 🎯 Quick Reference

### **Command Structure**

```bash
./moai.sh [COMMAND] [ARGUMENTS]
```

### **Agent Phases**

| Phase Range | Category | Description |
|-------------|----------|-------------|
| `/moai:0-4` | SPEC-First | Specification to completion workflow |
| `/moai:10-14` | TDD | Test-driven development workflow |
| `/moai:20-24` | Development | Full-stack development agents |
| `/moai:30-34` | Analysis | Code review, security, refactoring |

---

## 📖 Core Commands

### **/moai:list**

List all available agents with descriptions.

**Usage**:
```bash
./moai.sh /moai:list
```

**Output**:
```
Available MoAI-ADK Agents (26 total):

SPEC-First Workflow (0-4):
  /moai:0  - Specification Agent
  /moai:1  - Pseudocode Agent
  /moai:2  - Architecture Agent
  /moai:3  - Refinement Agent
  /moai:4  - Completion Agent

TDD Workflow (10-14):
  /moai:10 - Test Specification Agent
  /moai:11 - Test Implementation Agent
  /moai:12 - Code Implementation Agent
  /moai:13 - Test Validation Agent
  /moai:14 - Integration Agent

[... continues with all 26 agents ...]
```

---

### **/moai:help**

Display detailed help and usage information.

**Usage**:
```bash
./moai.sh /moai:help
./moai.sh /moai:help [AGENT_NUMBER]
```

**Examples**:
```bash
# General help
./moai.sh /moai:help

# Specific agent help
./moai.sh /moai:help 0
./moai.sh /moai:help 10
```

---

### **/moai:version**

Display MoAI-ADK version information.

**Usage**:
```bash
./moai.sh /moai:version
```

**Output**:
```
MoAI-ADK Version: 1.0.0
Python: 3.13.0
LangChain: 0.1.0
Korean Support: Enabled
```

---

## 🔧 SPEC-First Agents (0-4)

The SPEC-First methodology provides systematic development from specification to completion.

### **/moai:0 - Specification Agent**

Creates detailed project specifications from requirements.

**Purpose**: Transform user requirements into formal specifications.

**Usage**:
```bash
./moai.sh /moai:0 "REQUIREMENTS_TEXT"
./moai.sh /moai:0 "$(cat requirements.txt)"
```

**Examples**:
```bash
# Simple specification
./moai.sh /moai:0 "Create a todo list web application"

# Detailed specification
./moai.sh /moai:0 "Build a REST API for user management with authentication, CRUD operations, and role-based access control"

# From file
./moai.sh /moai:0 "$(cat docs/requirements.md)"

# Korean input
./moai.sh /moai:0 "사용자 관리 REST API 생성"
```

**Output Format**:
```markdown
# Project Specification

## Overview
[Project summary]

## Requirements
### Functional Requirements
- [Requirement 1]
- [Requirement 2]

### Non-Functional Requirements
- [Performance requirements]
- [Security requirements]

## User Stories
1. As a [user], I want [feature] so that [benefit]

## Acceptance Criteria
- [Criterion 1]
- [Criterion 2]

## Technical Constraints
[Constraints and limitations]
```

**Best Practices**:
- Be specific about requirements
- Include both functional and non-functional needs
- Mention target platform/technology if known
- Specify user types and roles

---

### **/moai:1 - Pseudocode Agent**

Generates algorithmic pseudocode from specifications.

**Purpose**: Create high-level algorithm design before implementation.

**Usage**:
```bash
./moai.sh /moai:1 "SPECIFICATION_TEXT"
./moai.sh /moai:1 "$(cat outputs/specification.txt)"
```

**Examples**:
```bash
# From specification
./moai.sh /moai:1 "$(./moai.sh /moai:0 'Create user authentication system')"

# Direct pseudocode request
./moai.sh /moai:1 "Design algorithm for binary search tree insertion"
```

**Output Format**:
```
ALGORITHM UserAuthentication

INPUT: username, password
OUTPUT: authToken OR error

PROCEDURE:
1. VALIDATE input parameters
   IF username is empty OR password is empty
      RETURN error "Invalid credentials"

2. QUERY database for user
   user = findUserByUsername(username)
   IF user not found
      RETURN error "User not found"

3. VERIFY password
   IF NOT comparePasswords(password, user.hashedPassword)
      RETURN error "Invalid password"

4. GENERATE authentication token
   token = generateJWT(user.id, user.roles)

5. RETURN token

END PROCEDURE
```

---

### **/moai:2 - Architecture Agent**

Designs system architecture and component structure.

**Purpose**: Create architectural blueprints and design decisions.

**Usage**:
```bash
./moai.sh /moai:2 "SPECIFICATION_TEXT"
```

**Examples**:
```bash
# Architecture from specification
./moai.sh /moai:2 "$(cat outputs/specification.txt)"

# Microservices architecture
./moai.sh /moai:2 "Design microservices architecture for e-commerce platform"
```

**Output Format**:
```markdown
# System Architecture

## Architecture Overview
[High-level architectural description]

## Component Diagram
```
[Frontend] <--> [API Gateway] <--> [Backend Services]
                                     - Auth Service
                                     - User Service
                                     - Data Service

[Backend] <--> [Database]
[Backend] <--> [Cache]
```

## Technology Stack
- Frontend: React + TypeScript
- Backend: Node.js + Express
- Database: PostgreSQL
- Cache: Redis
- Authentication: JWT

## Data Flow
1. Client request → API Gateway
2. API Gateway → Authentication middleware
3. Authenticated request → Business logic
4. Business logic → Database
5. Response → Client

## Design Patterns
- Repository pattern for data access
- Factory pattern for object creation
- Observer pattern for event handling

## Security Considerations
[Security architecture details]
```

---

### **/moai:3 - Refinement Agent**

Refines and improves existing specifications or designs.

**Purpose**: Enhance clarity, completeness, and quality.

**Usage**:
```bash
./moai.sh /moai:3 "CONTENT_TO_REFINE"
```

**Examples**:
```bash
# Refine specification
./moai.sh /moai:3 "$(cat outputs/specification.txt)"

# Improve architecture
./moai.sh /moai:3 "$(cat outputs/architecture.txt)"
```

**Refinement Areas**:
- Clarity and readability
- Completeness of requirements
- Edge case identification
- Performance considerations
- Security enhancements
- Scalability improvements

---

### **/moai:4 - Completion Agent**

Finalizes and validates complete specifications.

**Purpose**: Ensure specification completeness and readiness for implementation.

**Usage**:
```bash
./moai.sh /moai:4 "SPECIFICATION_TEXT"
```

**Output**:
- Completeness checklist
- Missing components identification
- Implementation readiness score
- Recommended next steps

---

## 🧪 TDD Agents (10-14)

Test-Driven Development workflow agents.

### **/moai:10 - Test Specification Agent**

Creates detailed test specifications.

**Usage**:
```bash
./moai.sh /moai:10 "FEATURE_DESCRIPTION"
```

**Examples**:
```bash
# Test specification for feature
./moai.sh /moai:10 "User login functionality"

# Test specification from spec
./moai.sh /moai:10 "$(cat outputs/specification.txt)"
```

**Output Format**:
```markdown
# Test Specification

## Test Suite: User Login

### Unit Tests
1. Test valid login
   - Input: valid username, valid password
   - Expected: authentication token
   - Assertions: token is not null, token contains user ID

2. Test invalid username
   - Input: invalid username, any password
   - Expected: error "User not found"

### Integration Tests
[Integration test specifications]

### Edge Cases
[Edge case test specifications]

### Performance Tests
[Performance test requirements]
```

---

### **/moai:11 - Test Implementation Agent**

Generates actual test code from specifications.

**Usage**:
```bash
./moai.sh /moai:11 "TEST_SPECIFICATION"
```

**Examples**:
```bash
# Generate tests
./moai.sh /moai:11 "$(cat outputs/test-specification.txt)"
```

**Output**: Complete test code (Jest, Pytest, etc.)

---

### **/moai:12 - Code Implementation Agent**

Implements code to pass the tests (TDD approach).

**Usage**:
```bash
./moai.sh /moai:12 "TEST_CODE"
```

---

### **/moai:13 - Test Validation Agent**

Validates test coverage and quality.

**Usage**:
```bash
./moai.sh /moai:13 "TEST_CODE"
```

---

### **/moai:14 - Integration Agent**

Handles integration testing and system validation.

**Usage**:
```bash
./moai.sh /moai:14 "INTEGRATION_REQUIREMENTS"
```

---

## 👨‍💻 Development Agents (20-24)

Full-stack development specialized agents.

### **/moai:20 - Frontend Developer**

Builds frontend components and UI.

**Usage**:
```bash
./moai.sh /moai:20 "FRONTEND_REQUIREMENTS"
```

**Specializations**:
- React/Vue/Angular components
- UI/UX implementation
- State management
- Responsive design

---

### **/moai:21 - Backend Developer**

Implements server-side logic and APIs.

**Usage**:
```bash
./moai.sh /moai:21 "BACKEND_REQUIREMENTS"
```

**Specializations**:
- REST API development
- Business logic implementation
- Authentication/Authorization
- Middleware and routing

---

### **/moai:22 - API Developer**

Designs and implements APIs.

**Usage**:
```bash
./moai.sh /moai:22 "API_REQUIREMENTS"
```

**Specializations**:
- REST API design
- GraphQL schemas
- API documentation (OpenAPI/Swagger)
- Versioning strategies

---

### **/moai:23 - Database Developer**

Designs database schemas and queries.

**Usage**:
```bash
./moai.sh /moai:23 "DATABASE_REQUIREMENTS"
```

**Specializations**:
- Schema design
- Query optimization
- Migrations
- Data modeling

---

### **/moai:24 - DevOps Engineer**

Handles deployment and infrastructure.

**Usage**:
```bash
./moai.sh /moai:24 "DEVOPS_REQUIREMENTS"
```

**Specializations**:
- CI/CD pipelines
- Docker containerization
- Kubernetes orchestration
- Infrastructure as Code

---

## 📊 Analysis Agents (30-34)

Code analysis, review, and refactoring agents.

### **/moai:30 - Code Reviewer**

Performs comprehensive code review.

**Usage**:
```bash
./moai.sh /moai:30 "CODE_TO_REVIEW"
./moai.sh /moai:30 "$(cat src/app.js)"
```

**Review Areas**:
- Code quality
- Best practices
- Design patterns
- Maintainability
- Documentation

---

### **/moai:31 - Security Analyst**

Analyzes code for security vulnerabilities.

**Usage**:
```bash
./moai.sh /moai:31 "CODE_TO_ANALYZE"
```

**Security Checks**:
- SQL injection vulnerabilities
- XSS attack vectors
- Authentication issues
- Authorization flaws
- Sensitive data exposure

---

### **/moai:32 - Performance Analyst**

Analyzes and optimizes performance.

**Usage**:
```bash
./moai.sh /moai:32 "CODE_TO_ANALYZE"
```

**Performance Areas**:
- Algorithm complexity
- Memory usage
- Database query optimization
- Caching strategies
- Bottleneck identification

---

### **/moai:33 - Refactoring Agent**

Suggests and implements code refactoring.

**Usage**:
```bash
./moai.sh /moai:33 "CODE_TO_REFACTOR"
```

**Refactoring Types**:
- Code smell elimination
- Design pattern application
- DRY principle enforcement
- SOLID principles
- Clean code practices

---

### **/moai:34 - Documentation Agent**

Generates comprehensive documentation.

**Usage**:
```bash
./moai.sh /moai:34 "CODE_OR_PROJECT"
```

**Documentation Types**:
- API documentation
- Code comments
- README files
- Architecture documentation
- User guides

---

## 🇰🇷 Korean Language Support

All agents support Korean input and output when Korean locale is configured.

### **Korean Command Examples**

```bash
# SPEC-First in Korean
./moai.sh /moai:0 "간단한 할 일 목록 웹 애플리케이션 만들기"

# TDD in Korean
./moai.sh /moai:10 "사용자 로그인 기능 테스트 명세서 작성"

# Code Review in Korean
./moai.sh /moai:30 "$(cat src/app.js)" --lang ko

# Mixed Korean-English
./moai.sh /moai:0 "Create REST API for 사용자 관리"
```

### **Korean Output Configuration**

```bash
# Set Korean output preference
export MOAI_LANG=ko_KR
export MOAI_OUTPUT_LANGUAGE=korean

# Or in config file
cat > config/language.yaml << 'EOF'
language:
  input: auto-detect  # Automatically detect Korean/English
  output: ko_KR       # Force Korean output
  encoding: utf-8
EOF
```

---

## ⚙️ Configuration

### **Environment Variables**

```bash
# Core configuration
export MOAI_HOME="/path/to/moai-adk"
export MOAI_OUTPUT_DIR="outputs"
export MOAI_LOG_LEVEL="INFO"

# Agent configuration
export MOAI_MAX_CONCURRENT_AGENTS=5
export MOAI_AGENT_TIMEOUT=300

# Language configuration
export MOAI_LANG=ko_KR
export PYTHONUTF8=1

# API keys (optional, for AI-powered agents)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### **Configuration File**

Create `config/moai.yaml`:

```yaml
# MoAI-ADK Configuration

general:
  output_directory: outputs
  log_level: INFO
  cache_enabled: true

agents:
  max_concurrent: 5
  timeout: 300
  retry_attempts: 3

language:
  default_locale: ko_KR.UTF-8
  input_encoding: utf-8
  output_encoding: utf-8

spec_first:
  phases:
    - specification
    - pseudocode
    - architecture
    - refinement
    - completion

tdd:
  test_framework: jest
  coverage_threshold: 80

# AI providers (optional)
ai:
  provider: openai
  model: gpt-4
  temperature: 0.7
```

---

## 📤 Output Formats

### **Default Output**

By default, agents output to stdout:

```bash
./moai.sh /moai:0 "test"
# Prints specification to terminal
```

### **File Output**

Redirect to file:

```bash
./moai.sh /moai:0 "test" > outputs/specification.txt
./moai.sh /moai:1 "$(cat outputs/specification.txt)" > outputs/pseudocode.txt
```

### **Structured Output**

Use `--format` flag:

```bash
# JSON output
./moai.sh /moai:0 "test" --format json > spec.json

# YAML output
./moai.sh /moai:2 "test" --format yaml > architecture.yaml

# Markdown output (default)
./moai.sh /moai:0 "test" --format markdown > spec.md
```

---

## 🔗 Workflow Examples

### **Complete SPEC-First Workflow**

```bash
# Phase 0: Specification
./moai.sh /moai:0 "Create user authentication system" > spec.txt

# Phase 1: Pseudocode
./moai.sh /moai:1 "$(cat spec.txt)" > pseudocode.txt

# Phase 2: Architecture
./moai.sh /moai:2 "$(cat spec.txt)" > architecture.txt

# Phase 3: Refinement
./moai.sh /moai:3 "$(cat spec.txt)" > refined-spec.txt

# Phase 4: Completion check
./moai.sh /moai:4 "$(cat refined-spec.txt)" > completion-report.txt
```

### **TDD Workflow**

```bash
# Generate test specification
./moai.sh /moai:10 "User login feature" > test-spec.txt

# Implement tests
./moai.sh /moai:11 "$(cat test-spec.txt)" > tests/login.test.js

# Implement code to pass tests
./moai.sh /moai:12 "$(cat tests/login.test.js)" > src/login.js

# Validate tests
./moai.sh /moai:13 "$(cat tests/login.test.js)"
```

### **Full-Stack Development**

```bash
# Backend API
./moai.sh /moai:21 "REST API for user management" > backend/api.js

# Frontend UI
./moai.sh /moai:20 "User management UI with React" > frontend/UserManagement.jsx

# Database schema
./moai.sh /moai:23 "User database schema" > database/users-schema.sql

# DevOps setup
./moai.sh /moai:24 "Docker setup for the application" > Dockerfile
```

---

## 🎯 Best Practices

### **1. Start with Specification**

Always begin with `/moai:0` to create a solid foundation:

```bash
./moai.sh /moai:0 "Detailed project requirements here"
```

### **2. Use Piping for Workflows**

Chain agents together:

```bash
./moai.sh /moai:0 "requirements" | ./moai.sh /moai:1
```

### **3. Save Intermediate Results**

Store outputs for reference:

```bash
mkdir -p outputs/{spec,tests,code,docs}
./moai.sh /moai:0 "req" > outputs/spec/initial.txt
```

### **4. Validate with Multiple Agents**

Use different agents for validation:

```bash
# Review code with multiple agents
./moai.sh /moai:30 "$(cat src/app.js)" > reviews/code-review.txt
./moai.sh /moai:31 "$(cat src/app.js)" > reviews/security.txt
./moai.sh /moai:32 "$(cat src/app.js)" > reviews/performance.txt
```

### **5. Korean-English Mixing**

You can mix languages naturally:

```bash
./moai.sh /moai:0 "Create REST API for 사용자 관리 with JWT authentication and role-based 권한 관리"
```

---

## 📞 Support & Resources

- **Installation**: See `docs/00-INSTALL-STEPS.md`
- **Verification**: See `docs/04-VERIFICATION.md`
- **Troubleshooting**: See `docs/05-TROUBLESHOOTING.md`
- **Korean Setup**: See `docs/03-KOREAN-SETUP.md`

---

**MoAI-ADK Version 1.0.0** - Built with SPEC-First methodology and Korean language support 🇰🇷
