# Automated Coding Agent Network - Project Structure

## Overview

This project implements a multi-agent system for automated software development using:
- **Spec-Driven Development** (GitHub spec-kit)
- **Model Context Protocol (MCP)** for agent-agnostic tool integration
- **Multi-Agent Orchestration** (CrewAI)
- **Hybrid LLM Strategy** (Local DeepSeek + Cloud Claude)

---

## Directory Structure

```
automated-coding-agent-network/
├── agents/                          # Agent definitions and roles
│   ├── roles/                       # Specialized agent roles
│   │   ├── project_manager.py       # Requirements analysis agent
│   │   ├── architect.py             # System design agent
│   │   ├── coder.py                 # Implementation agent
│   │   ├── tester.py                # Testing and validation agent
│   │   └── reviewer.py              # Code review agent
│   ├── base_agent.py                # Base agent class
│   └── agent_factory.py             # Agent creation and configuration
│
├── mcp_servers/                     # MCP server implementations
│   ├── specification/               # Spec-kit integration server
│   │   ├── server.py                # Main MCP server
│   │   ├── tools.py                 # Specification tools
│   │   └── resources.py             # Specification resources
│   ├── code_editor/                 # Code manipulation server (Aider integration)
│   │   ├── server.py
│   │   ├── tools.py
│   │   └── resources.py
│   ├── testing/                     # Testing and validation server
│   │   ├── server.py
│   │   ├── tools.py
│   │   └── resources.py
│   └── github/                      # GitHub integration server
│       ├── server.py
│       ├── tools.py
│       └── resources.py
│
├── workflows/                       # Workflow orchestration
│   ├── templates/                   # Workflow templates
│   │   ├── feature_implementation.py
│   │   ├── bug_fix.py
│   │   └── refactoring.py
│   ├── orchestrator.py              # Main workflow orchestrator
│   └── task_router.py               # Intelligent task routing
│
├── specifications/                  # Project specifications (spec-kit)
│   ├── constitution/                # Project principles
│   ├── requirements/                # Feature requirements
│   ├── plans/                       # Technical plans
│   └── tasks/                       # Implementation tasks
│
├── config/                          # Configuration files
│   ├── agents.yaml                  # Agent configuration
│   ├── models.yaml                  # LLM model configuration
│   ├── mcp_servers.yaml             # MCP server configuration
│   ├── workflows.yaml               # Workflow configuration
│   └── settings.yaml                # Global settings
│
├── tests/                           # Test suite
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   └── e2e/                         # End-to-end tests
│
├── docs/                            # Documentation
│   ├── architecture.md              # System architecture
│   ├── agent_guide.md               # Agent development guide
│   ├── mcp_guide.md                 # MCP server guide
│   └── user_guide.md                # User documentation
│
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore file
├── requirements.txt                 # Python dependencies
├── setup.py                         # Package setup
├── README.md                        # Project README
└── main.py                          # Main entry point
```

---

## Component Responsibilities

### 1. Agents (`/agents`)

**Purpose**: Define specialized AI agents for different development tasks

**Key Agents**:
- **ProjectManager**: Analyzes requirements, asks clarifying questions
- **Architect**: Designs system architecture and technical plans
- **Coder**: Implements features using MCP tools
- **Tester**: Creates and runs tests, validates implementation
- **Reviewer**: Reviews code quality and adherence to specifications

**Configuration**: `config/agents.yaml`

---

### 2. MCP Servers (`/mcp_servers`)

**Purpose**: Expose capabilities as standardized MCP tools and resources

**Specification Server**:
- Tools: `create_spec`, `refine_spec`, `validate_spec`
- Resources: `specifications/*`, `constitution`, `task_lists/*`

**Code Editor Server**:
- Tools: `edit_code`, `refactor_code`, `add_tests`, `fix_linting`
- Resources: `codebase_map`, `file_contents/*`, `git_history`

**Testing Server**:
- Tools: `run_unit_tests`, `run_integration_tests`, `check_coverage`
- Resources: `test_results`, `coverage_report`

**GitHub Server**:
- Tools: `create_issue`, `create_pr`, `review_pr`
- Resources: `repository_info`, `issues/*`, `pull_requests/*`

**Configuration**: `config/mcp_servers.yaml`

---

### 3. Workflows (`/workflows`)

**Purpose**: Orchestrate multi-agent collaboration for complex tasks

**Workflow Types**:
1. **Feature Implementation**: Spec → Design → Code → Test → Review → PR
2. **Bug Fix**: Issue Analysis → Root Cause → Fix → Test → PR
3. **Refactoring**: Analysis → Plan → Refactor → Test → Review

**Configuration**: `config/workflows.yaml`

---

### 4. Specifications (`/specifications`)

**Purpose**: Store project specifications using spec-kit format

**Structure**:
- `constitution/`: Project principles and guidelines
- `requirements/`: Feature and requirement specifications
- `plans/`: Technical architecture and implementation plans
- `tasks/`: Broken down implementation tasks with dependencies

**Managed by**: Specification MCP Server

---

### 5. Configuration (`/config`)

**Purpose**: User-configurable settings for all system components

**Configuration Files**:

**`agents.yaml`**: Agent definitions
```yaml
agents:
  project_manager:
    model: claude-sonnet-4
    temperature: 0.7
    role: "Requirements analyst and clarification specialist"

  architect:
    model: claude-opus-4
    temperature: 0.3
    role: "System architecture and technical design"

  coder:
    model: deepseek-coder-v2:16b
    temperature: 0.2
    role: "Code implementation specialist"

  tester:
    model: deepseek-coder-v2:16b
    temperature: 0.3
    role: "Testing and validation specialist"

  reviewer:
    model: claude-sonnet-4
    temperature: 0.4
    role: "Code quality and review specialist"
```

**`models.yaml`**: LLM configuration
```yaml
models:
  local:
    deepseek-coder-v2:
      endpoint: "http://localhost:11434"
      model_name: "deepseek-coder-v2:16b"
      max_tokens: 4096

  cloud:
    claude-sonnet-4:
      provider: "anthropic"
      model_name: "claude-sonnet-4-20250514"
      api_key_env: "ANTHROPIC_API_KEY"
      max_tokens: 8192

    claude-opus-4:
      provider: "anthropic"
      model_name: "claude-opus-4-20250514"
      api_key_env: "ANTHROPIC_API_KEY"
      max_tokens: 8192
```

**`mcp_servers.yaml`**: MCP server configuration
```yaml
mcp_servers:
  specification:
    command: "python"
    args: ["mcp_servers/specification/server.py"]
    enabled: true

  code_editor:
    command: "python"
    args: ["mcp_servers/code_editor/server.py"]
    enabled: true

  testing:
    command: "python"
    args: ["mcp_servers/testing/server.py"]
    enabled: true

  github:
    command: "python"
    args: ["mcp_servers/github/server.py"]
    enabled: true
```

**`workflows.yaml`**: Workflow configuration
```yaml
workflows:
  feature_implementation:
    enabled: true
    agents:
      - project_manager
      - architect
      - coder
      - tester
      - reviewer
    steps:
      - name: "Requirements Analysis"
        agent: "project_manager"
        tools: ["specification"]
      - name: "Technical Design"
        agent: "architect"
        tools: ["specification"]
      - name: "Implementation"
        agent: "coder"
        tools: ["code_editor", "specification"]
      - name: "Testing"
        agent: "tester"
        tools: ["testing", "code_editor"]
      - name: "Review"
        agent: "reviewer"
        tools: ["code_editor", "github"]
```

**`settings.yaml`**: Global settings
```yaml
system:
  project_root: "."
  log_level: "INFO"
  max_concurrent_tasks: 5

cost_management:
  daily_budget_usd: 50
  enable_cost_tracking: true
  alert_threshold: 0.8

routing:
  prefer_local: true
  local_fallback: true
  timeout_seconds: 300

git:
  auto_commit: true
  commit_message_template: "feat: {description}\n\nGenerated by AI Agent System"
```

---

## Workflow Execution Flow

```
User Request
    ↓
[Task Router] ← config/workflows.yaml
    ↓
[Workflow Orchestrator]
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│                 │                 │                 │
[Project Manager] [Architect]      [Coder]
│                 │                 │
└─────→ MCP: Specification Server ←─────┘
                  │
        [Spec-kit Integration]
                  ↓
            specifications/
```

---

## Data Flow

1. **User Request** → Task Router
2. **Task Router** → Selects workflow template
3. **Workflow Orchestrator** → Initializes agents
4. **Agents** → Call MCP servers for tools
5. **MCP Servers** → Execute operations (spec-kit, aider, tests)
6. **Results** → Flow back to agents
7. **Agents** → Collaborate via workflow
8. **Final Output** → PR, documentation, etc.

---

## Configuration System

### User-Facing Configuration

Users can customize the system by editing YAML files in `/config`:

1. **Choose which agents to use** (`agents.yaml`)
2. **Configure LLM models** (`models.yaml`)
3. **Enable/disable MCP servers** (`mcp_servers.yaml`)
4. **Customize workflows** (`workflows.yaml`)
5. **Set global preferences** (`settings.yaml`)

### Environment Variables

Create `.env` file for sensitive data:
```
ANTHROPIC_API_KEY=your_api_key_here
OPENAI_API_KEY=your_api_key_here
GITHUB_TOKEN=your_github_token_here
OLLAMA_HOST=http://localhost:11434
```

---

## Agent-to-Agent Communication

Agents communicate through:
1. **Shared Context**: Via workflow orchestrator
2. **MCP Resources**: Read specifications, code, test results
3. **MCP Tools**: Trigger actions for other agents
4. **Workflow State**: Track progress and handoffs

Example:
```
ProjectManager creates spec → MCP spec server stores it
    ↓
Architect reads spec → MCP spec server retrieves it
    ↓
Architect creates plan → MCP spec server stores it
    ↓
Coder reads plan → MCP spec server retrieves it
    ↓
Coder implements → MCP code server edits files
```

---

## Extensibility

### Adding New Agents
1. Create agent class in `agents/roles/`
2. Add configuration to `config/agents.yaml`
3. Update workflows to use new agent

### Adding New MCP Servers
1. Create server in `mcp_servers/new_server/`
2. Implement tools and resources
3. Add configuration to `config/mcp_servers.yaml`

### Adding New Workflows
1. Create workflow template in `workflows/templates/`
2. Add configuration to `config/workflows.yaml`
3. Define agent sequence and tool usage

---

## Next Steps

1. ✅ Project structure created
2. ⬜ Install spec-kit and initialize
3. ⬜ Set up Python environment and dependencies
4. ⬜ Install CrewAI for agent orchestration
5. ⬜ Implement first MCP server (Specification)
6. ⬜ Create base agent classes
7. ⬜ Build simple workflow for testing
8. ⬜ Add configuration loading system
9. ⬜ Implement cost tracking and routing
10. ⬜ Full system integration

---

## Design Principles

1. **Agent-Agnostic**: MCP ensures any AI can use the tools
2. **User-Configurable**: YAML configs for all settings
3. **Modular**: Each component is independent and replaceable
4. **Cost-Efficient**: Intelligent routing between local/cloud
5. **Quality-Focused**: DeepSeek for reliability over speed
6. **Spec-Driven**: Specifications guide all development
7. **Testable**: Comprehensive test coverage
8. **Observable**: Logging, monitoring, cost tracking
