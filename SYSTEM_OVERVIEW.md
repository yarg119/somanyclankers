# Automated Coding Agent Network - System Overview

## What We Built

A multi-agent system that automatically generates working code from natural language requirements.

## Architecture

### Agents
1. **Project Manager** (Claude Sonnet 4.5)
   - Analyzes requirements
   - Creates detailed specifications
   - Asks clarifying questions
   - Documents risks and dependencies

2. **Coder** (DeepSeek Coder V2 - Local)
   - Implements features from specifications
   - Writes clean, documented code
   - Includes error handling
   - Creates test files

### Workflow Pipeline

```
User Input
  ↓
Project Manager (Claude) → Detailed Specification
  ↓
Coder (DeepSeek) → Code Description
  ↓
Post-Processor → Extract & Create Files
  ↓
Working Code + Tests
```

### Key Components

**1. Tools System** (`tools/`)
- `simple_tools.py` - File operations for agents
- `code_extractor.py` - Post-processor that extracts code from DeepSeek output
- Protected file list prevents overwriting system files

**2. Agent Framework** (`agents/`)
- `base_agent.py` - Common agent functionality
- `roles/project_manager.py` - Specification creation
- `roles/coder.py` - Code implementation

**3. Configuration** (`config/`)
- `agents.yaml` - Agent definitions and model assignments
- `models.yaml` - LLM model configurations
- `workflows.yaml` - Multi-agent workflows

## Hybrid LLM Strategy

**Cost Optimization:**
- **Claude Sonnet 4.5**: Planning & specifications (cloud, paid)
- **DeepSeek Coder V2**: Implementation (local, free)

**Benefits:**
- Leverages Claude's superior reasoning for planning
- Uses local DeepSeek for cost-free code generation
- Post-processor bridges the gap

## Example Workflow Run

### Input
```
"Create a simple calculator with add, subtract, multiply, divide functions"
```

### Output Files Created
1. **`src/calculator_main.py`** - Main calculator implementation
   - `add(x, y)` function
   - `subtract(x, y)` function
   - `multiply(x, y)` function
   - `divide(x, y)` function with zero-division handling
   - Interactive calculate() function

2. **`utils.py`** - Input validation
   - `validate_input()` - Ensures numeric input

3. **`tests/test_calculator.py`** - Complete test suite
   - Tests for all operations
   - Edge case testing
   - Division by zero error handling

4. **`specifications/simple_calculator_specification.md`** - Full specification
   - Functional requirements (FR1-FR8)
   - Non-functional requirements (NFR1-NFR7)
   - Architecture overview
   - Implementation plan
   - Acceptance criteria
   - Risk analysis

## Usage

### Run a Workflow
```bash
python main.py run --workflow feature_implementation --input "Your requirement here"
```

### Check System Status
```bash
python main.py status
```

### Initialize System
```bash
python main.py init
```

## Technical Details

### Tools Available to Agents
- **Project Manager**: `create_specification`, `read_specification`
- **Coder**: `write_file`, `read_file`, `list_directory`

### Post-Processing
The code extractor uses multiple strategies to extract code:
1. Direct `write_file()` function calls
2. Markdown code blocks with file paths
3. Section headers with filenames

### Protected Files
System prevents overwriting critical files:
- `main.py` (orchestrator)
- Agent code files
- Configuration files
- Tool implementations

## Success Metrics

✅ End-to-end code generation from natural language
✅ Specification → Implementation workflow
✅ Automatic file creation
✅ Test generation
✅ Error handling
✅ Cost optimization (local + cloud hybrid)

## Future Enhancements

Potential additions:
- Tester agent (run tests, validate)
- Reviewer agent (code quality checks)
- Architect agent (system design)
- GitHub integration (PR creation)
- Interactive mode
- Cost tracking dashboard

## Key Innovation

**The Post-Processor Pattern**

DeepSeek (and many local models) struggle with tool calling but excel at generating code descriptions. Our post-processor extracts the described code and creates actual files, bridging the gap between local model capabilities and required functionality.

This pattern enables:
- Using cheaper/faster local models for implementation
- Leveraging their code generation strengths
- Working around tool-calling limitations
- Maintaining the benefits of multi-agent orchestration
