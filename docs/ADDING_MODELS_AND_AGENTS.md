# Guide: Adding Models and Customizing Agents

## Part 1: Adding New Models

### Step 1: Add Model to `config/models.yaml`

#### Adding a Local Model (via Ollama)

```yaml
local_models:
  # Example: Adding Mistral
  mistral-7b:
    provider: "ollama"
    endpoint: "http://localhost:11434"
    model_name: "mistral:7b"
    max_tokens: 4096
    context_window: 8192
    cost_per_token: 0.0
    enabled: true
    description: "Mistral 7B for general tasks"

  # Example: Adding CodeLlama
  codellama:
    provider: "ollama"
    endpoint: "http://localhost:11434"
    model_name: "codellama:13b"
    max_tokens: 4096
    context_window: 16384
    cost_per_token: 0.0
    enabled: true
    description: "Code Llama for coding tasks"

  # Example: Adding Llama 3
  llama3:
    provider: "ollama"
    endpoint: "http://localhost:11434"
    model_name: "llama3:8b"
    max_tokens: 4096
    context_window: 8192
    cost_per_token: 0.0
    enabled: true
    description: "Llama 3 for general reasoning"
```

#### Adding a Cloud Model

```yaml
cloud_models:
  # Example: Adding GPT-4
  gpt-4:
    provider: "openai"
    model_name: "gpt-4-turbo-preview"
    api_key_env: "OPENAI_API_KEY"
    max_tokens: 4096
    context_window: 128000
    cost_per_1m_input_tokens: 10.00
    cost_per_1m_output_tokens: 30.00
    enabled: true
    description: "GPT-4 Turbo for complex reasoning"

  # Example: Adding GPT-3.5
  gpt-3.5:
    provider: "openai"
    model_name: "gpt-3.5-turbo"
    api_key_env: "OPENAI_API_KEY"
    max_tokens: 4096
    context_window: 16384
    cost_per_1m_input_tokens: 0.50
    cost_per_1m_output_tokens: 1.50
    enabled: true
    description: "GPT-3.5 Turbo for fast tasks"
```

### Step 2: Update `agents/base_agent.py` Model Mapping (if needed)

If your model needs special handling, update the `_get_llm_config()` method:

```python
def _get_llm_config(self) -> str:
    model_name = self.config.model

    # Local models (Ollama)
    if "deepseek" in model_name.lower() or "mistral" in model_name.lower() or "llama" in model_name.lower() or ":" in model_name:
        return f"ollama/{model_name}"

    # Anthropic Claude
    elif "claude" in model_name.lower():
        model_mapping = {
            "claude-sonnet-4": "claude-sonnet-4-5-20250929",
            "claude-opus-4": "claude-opus-4-1-20250805",
            "claude-haiku-4": "claude-haiku-4-5-20251001"
        }
        return model_mapping.get(model_name, model_name)

    # OpenAI GPT
    elif "gpt" in model_name.lower():
        return model_name

    # Google Gemini
    elif "gemini" in model_name.lower():
        return model_name

    # Default
    else:
        return model_name
```

### Step 3: Set Up API Keys (for cloud models)

Add to your `.env` file:

```bash
# Anthropic
ANTHROPIC_API_KEY=your_key_here

# OpenAI
OPENAI_API_KEY=your_key_here

# Google
GOOGLE_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

## Part 2: Creating New Agent Roles

### Step 1: Create New Agent Class

Create a new file: `agents/roles/tester.py`

```python
"""
Tester Agent
Responsible for creating and running tests.
"""

from typing import Any, Dict, List, Optional
import asyncio

from ..base_agent import BaseAgent, AgentConfig


class TesterAgent(BaseAgent):
    """
    Tester agent specializes in:
    - Writing unit tests
    - Writing integration tests
    - Running test suites
    - Analyzing test coverage
    """

    def __init__(self, config: AgentConfig):
        """Initialize Tester agent."""
        # Set default configuration if not provided
        if not config.role:
            config.role = "Quality Assurance and Testing Specialist"

        if not config.goal:
            config.goal = (
                "Create comprehensive test suites that ensure code quality "
                "and catch bugs early. Validate that implementations meet "
                "specifications."
            )

        if not config.backstory:
            config.backstory = (
                "You are a meticulous QA engineer with expertise in test-driven "
                "development. You write tests that are thorough, maintainable, "
                "and catch edge cases. You understand the importance of test "
                "coverage and always validate against specifications."
            )

        super().__init__(config)

    async def execute(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute a testing task.

        Args:
            task_description: Description of the testing task
            context: Optional context (e.g., code to test, specification)

        Returns:
            Result containing test code and analysis
        """
        context = context or {}

        # Create the task for this agent
        task = self.create_task(
            description=task_description,
            expected_output=(
                "Test implementation with:\n"
                "1. Unit tests for all functions\n"
                "2. Integration tests for workflows\n"
                "3. Edge case coverage\n"
                "4. Test execution results\n"
                "5. Coverage report"
            ),
            context=context.get("previous_tasks", [])
        )

        # Execute the task using CrewAI
        result = self.execute_task_sync(task)

        return result

    async def create_tests(
        self,
        specification: str,
        code: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create tests based on specification and code.

        Args:
            specification: The specification to test against
            code: The code to test
            context: Optional context

        Returns:
            Dictionary containing test results
        """
        context = context or {}

        task_description = f"""
        Create comprehensive tests for the following code based on this specification:

        SPECIFICATION:
        {specification}

        CODE TO TEST:
        {code}

        CRITICAL INSTRUCTIONS:
        1. You MUST use the write_file tool to create actual test files
        2. Create test files in the tests/ directory
        3. Write complete, working test code - not pseudocode
        4. Include all necessary imports and setup

        YOUR TESTS SHOULD INCLUDE:
        1. Unit tests for each function
        2. Edge case testing
        3. Error condition testing
        4. Integration tests if applicable
        5. Test data setup and teardown

        REQUIRED TOOLS USAGE:
        - Use write_file(file_path="tests/test_<name>.py", content="full test code")
        - Include pytest or unittest imports
        - Add docstrings explaining what each test validates

        Remember: ACTUALLY USE THE write_file TOOL - don't just describe tests!
        """

        result = await self.execute(task_description, context)

        return {
            "test_files": self._extract_test_files(result),
            "summary": result,
            "coverage_notes": self._extract_coverage_notes(result)
        }

    def _extract_test_files(self, result: str) -> List[str]:
        """Extract list of test files from result."""
        files = []
        for line in result.split('\n'):
            if 'test_' in line and '.py' in line:
                files.append(line.strip().lstrip('-* '))
        return files

    def _extract_coverage_notes(self, result: str) -> str:
        """Extract coverage notes from result."""
        # Simple extraction - can be enhanced
        if "coverage" in result.lower():
            lines = result.split('\n')
            for i, line in enumerate(lines):
                if "coverage" in line.lower():
                    return '\n'.join(lines[i:i+5])
        return ""
```

### Step 2: Register Agent in `agents/__init__.py`

```python
from .base_agent import BaseAgent, AgentConfig
from .roles.project_manager import ProjectManagerAgent
from .roles.coder import CoderAgent
from .roles.tester import TesterAgent  # Add this

__all__ = [
    'BaseAgent',
    'AgentConfig',
    'ProjectManagerAgent',
    'CoderAgent',
    'TesterAgent'  # Add this
]
```

### Step 3: Add Agent Configuration to `config/agents.yaml`

```yaml
agents:
  # ... existing agents ...

  tester:
    model: "deepseek-coder-v2:16b"  # Or any model you want
    temperature: 0.3
    max_tokens: 4096
    role: "Quality Assurance and Testing Specialist"
    description: "Creates tests, runs test suites, validates implementation"
    tools:
      - code_editor
      - testing
    fallback_model: null
    enabled: true  # Set to false to disable
```

### Step 4: Update `main.py` to Initialize New Agent

```python
def _initialize_agent(self, agent_name: str, agent_config: dict) -> Optional[object]:
    """Initialize a specific agent."""
    try:
        config = AgentConfig(
            name=agent_name,
            role=agent_config.get('role', ''),
            goal=agent_config.get('goal', ''),
            backstory=agent_config.get('backstory', ''),
            model=agent_config.get('model', 'deepseek-coder-v2:16b'),
            temperature=agent_config.get('temperature', 0.7),
            tools=agent_config.get('tools', []),
            fallback_model=agent_config.get('fallback_model')
        )

        # Initialize the appropriate agent class
        if agent_name == "project_manager":
            return ProjectManagerAgent(config)
        elif agent_name == "coder":
            return CoderAgent(config)
        elif agent_name == "tester":  # Add this
            return TesterAgent(config)
        else:
            logger.warning(f"Unknown agent type: {agent_name}")
            return None

    except Exception as e:
        logger.error(f"Error initializing agent {agent_name}: {e}")
        return None
```

## Part 3: Customizing Agent Prompts

### Method 1: Modify Agent Class Directly

Edit the agent file (e.g., `agents/roles/coder.py`):

```python
def __init__(self, config: AgentConfig):
    """Initialize Coder agent."""

    # CUSTOMIZE THESE:
    if not config.role:
        config.role = "Your Custom Role Description"

    if not config.goal:
        config.goal = (
            "Your custom goal for this agent. "
            "What should it accomplish?"
        )

    if not config.backstory:
        config.backstory = (
            "Your custom backstory that shapes how the agent thinks. "
            "This influences its behavior and decision-making. "
            "Be specific about expertise, approach, and values."
        )

    super().__init__(config)
```

### Method 2: Configure via YAML

Add custom prompts to `config/agents.yaml`:

```yaml
agents:
  coder:
    model: "deepseek-coder-v2:16b"
    temperature: 0.2
    max_tokens: 4096

    # CUSTOM PROMPTS:
    role: "Senior Python Developer specializing in clean architecture"

    goal: >
      Write production-ready Python code following SOLID principles.
      Focus on maintainability, testability, and performance.
      Always include comprehensive docstrings and type hints.

    backstory: >
      You are a senior Python developer with 10+ years of experience
      building scalable applications. You have deep expertise in:
      - Clean architecture and design patterns
      - Test-driven development
      - Performance optimization
      - Modern Python best practices (type hints, async/await)

      Your code is known for being:
      - Well-documented with clear docstrings
      - Properly type-annotated
      - Thoroughly tested
      - Easy to maintain and extend

      You always consider edge cases and error handling.
      You write code that other developers love to work with.

    tools:
      - code_editor
      - specification
```

Then update the agent initialization to use these values:

```python
def _initialize_agent(self, agent_name: str, agent_config: dict) -> Optional[object]:
    config = AgentConfig(
        name=agent_name,
        role=agent_config.get('role', ''),  # Uses YAML value
        goal=agent_config.get('goal', ''),  # Uses YAML value
        backstory=agent_config.get('backstory', ''),  # Uses YAML value
        model=agent_config.get('model', 'deepseek-coder-v2:16b'),
        temperature=agent_config.get('temperature', 0.7),
        tools=agent_config.get('tools', []),
        fallback_model=agent_config.get('fallback_model')
    )
    # ... rest of initialization
```

### Method 3: Task-Specific Prompts

Customize prompts for specific tasks in the workflow methods:

```python
async def implement_feature(self, specification: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Implement a feature based on specification."""

    # CUSTOMIZE THIS TASK DESCRIPTION:
    task_description = f"""
    YOUR CUSTOM INSTRUCTIONS HERE:

    Implement the following feature: {specification}

    SPECIFIC REQUIREMENTS:
    1. Use Python 3.10+ features
    2. Add type hints to all functions
    3. Write docstrings in Google style
    4. Include error handling with custom exceptions
    5. Create a __main__ block for testing
    6. Add logging statements at INFO level

    CODE STYLE:
    - Maximum line length: 88 characters (Black style)
    - Use f-strings for formatting
    - Prefer list comprehensions when readable
    - Add comments for complex logic only

    ACTUAL FILE CREATION:
    You MUST use write_file() tool to create files.
    Example: write_file(file_path="src/module.py", content="...full code...")
    """

    result = await self.execute(task_description, context)
    return result
```

## Part 4: Examples

### Example 1: Adding a Code Reviewer Agent with GPT-4

**Step 1:** Add to `config/agents.yaml`
```yaml
reviewer:
  model: "gpt-4"
  temperature: 0.3
  max_tokens: 8192
  role: "Senior Code Reviewer"
  goal: "Provide constructive code reviews focusing on quality, security, and maintainability"
  backstory: >
    You are a senior code reviewer with expertise in identifying bugs,
    security vulnerabilities, and design issues. You provide actionable
    feedback that helps developers improve their code.
  tools:
    - code_editor
    - specification
  enabled: true
```

**Step 2:** Create `agents/roles/reviewer.py` (similar structure to tester example above)

**Step 3:** Add to workflow in `config/workflows.yaml`
```yaml
workflows:
  feature_implementation:
    steps:
      # ... existing steps ...
      - name: Code Review
        agent: reviewer
        requires: [Implementation]
```

### Example 2: Using Mistral for Documentation

```yaml
documentation_writer:
  model: "mistral:7b"
  temperature: 0.7
  max_tokens: 4096
  role: "Technical Documentation Specialist"
  goal: "Create clear, comprehensive documentation for developers"
  tools:
    - code_editor
    - specification
```

## Tips and Best Practices

1. **Temperature Settings:**
   - Low (0.1-0.3): Deterministic, focused tasks (coding, testing)
   - Medium (0.4-0.7): Balanced (planning, review)
   - High (0.8-1.0): Creative tasks (brainstorming, documentation)

2. **Model Selection:**
   - **Claude**: Best for complex reasoning, planning
   - **GPT-4**: Strong all-rounder, good for reviews
   - **DeepSeek/CodeLlama**: Excellent for code generation
   - **Mistral/Llama**: Good for general tasks, documentation

3. **Prompt Engineering:**
   - Be specific about output format
   - Include examples when possible
   - Use role-playing (backstory) to shape behavior
   - Emphasize using tools (write_file, etc.)

4. **Tool Assignment:**
   - Only give agents tools they need
   - `code_editor`: For file operations
   - `specification`: For docs
   - `testing`: For test execution

5. **Enable/Disable Agents:**
   - Use `enabled: false` to temporarily disable
   - Useful for testing specific workflows
