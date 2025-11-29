# Specialized Development Agents

> Domain-specific development agents for specialized tasks

## Overview

MoAI-Flow has 8 specialized development agents. These map well to MoAI's expert tier agents.

---

## Agent: `backend-dev`

### Purpose
Backend development specialist.

### Capabilities
- Server-side code
- API development
- Database integration
- Authentication/authorization

### Tech Stack Focus
- Node.js/Express
- Python/FastAPI
- Go
- Database ORMs

### MoAI Equivalent
`expert-backend` - Strong match

---

## Agent: `mobile-dev`

### Purpose
Mobile application development.

### Capabilities
- iOS development
- Android development
- Cross-platform (React Native, Flutter)
- Mobile-specific patterns

### MoAI Gap
No dedicated mobile agent. Would use `expert-frontend` + context.

---

## Agent: `ml-developer`

### Purpose
Machine learning development.

### Capabilities
- Model training
- Data preprocessing
- Feature engineering
- Model deployment

### Tech Focus
- TensorFlow/PyTorch
- scikit-learn
- MLOps patterns

### MoAI Gap
No dedicated ML agent. Could be added as `expert-ml`.

---

## Agent: `cicd-engineer`

### Purpose
CI/CD pipeline development.

### Capabilities
- Pipeline configuration
- Build optimization
- Deployment automation
- Environment management

### Platforms
- GitHub Actions
- GitLab CI
- Jenkins
- CircleCI

### MoAI Equivalent
`expert-devops` - Covers CI/CD

---

## Agent: `api-docs`

### Purpose
API documentation specialist.

### Capabilities
- OpenAPI/Swagger specs
- Documentation generation
- Example creation
- SDK documentation

### Outputs
- API reference docs
- Integration guides
- Postman collections

### MoAI Equivalent
`manager-docs` - Handles documentation generally

---

## Agent: `system-architect`

### Purpose
System architecture design.

### Capabilities
- High-level design
- System boundaries
- Integration patterns
- Scalability planning

### Outputs
- Architecture diagrams
- Decision records (ADRs)
- Component specs

### MoAI Equivalent
`manager-strategy` + `expert-backend` for architecture

---

## Agent: `code-analyzer`

### Purpose
Static code analysis.

### Capabilities
- Code quality metrics
- Pattern detection
- Dependency analysis
- Security scanning

### Outputs
- Quality reports
- Improvement suggestions
- Risk assessments

### MoAI Equivalent
`manager-quality` + `expert-security`

---

## Agent: `base-template-generator`

### Purpose
Generate project templates and boilerplate.

### Capabilities
- Project scaffolding
- Boilerplate generation
- Configuration templates
- Best practice templates

### MoAI Equivalent
`builder-*` tier handles meta-generation

---

## Comparison Table

| MoAI-Flow | MoAI Equivalent | Match Level |
|-------------|-----------------|-------------|
| `backend-dev` | `expert-backend` | Strong |
| `mobile-dev` | - | Gap |
| `ml-developer` | - | Gap |
| `cicd-engineer` | `expert-devops` | Strong |
| `api-docs` | `manager-docs` | Partial |
| `system-architect` | `manager-strategy` | Partial |
| `code-analyzer` | `manager-quality` | Partial |
| `base-template-generator` | `builder-*` | Partial |

---

## MoAI Strengths

MoAI has additional experts not in MoAI-Flow:

| MoAI Agent | Purpose | MoAI-Flow Equivalent |
|------------|---------|------------------------|
| `expert-frontend` | Frontend development | `coder` (general) |
| `expert-database` | Database design | `backend-dev` (partial) |
| `expert-security` | Security analysis | `security-manager` |
| `expert-uiux` | UI/UX design | - |
| `expert-debug` | Debugging | - |

---

## Recommendations

### Add to MoAI
1. `expert-mobile` - Mobile development
2. `expert-ml` - Machine learning

### Keep MoAI Advantage
- Domain-specialized experts
- Clear `expert-*` naming
- 5-tier hierarchy

---

## Coverage Analysis

| Domain | MoAI-Flow | MoAI |
|--------|-------------|------|
| Backend | Yes | Yes |
| Frontend | Partial | Yes |
| Mobile | Yes | No |
| ML/AI | Yes | No |
| Database | Partial | Yes |
| DevOps | Yes | Yes |
| Security | Yes | Yes |
| UI/UX | No | Yes |
| Debug | No | Yes |
