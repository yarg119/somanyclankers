# Quick Start Guide

Welcome to the Automated Coding Agent Network! This guide will help you get started quickly.

## Current Status

The system is now set up with:

- ✅ Project structure created
- ✅ Python virtual environment with dependencies installed
- ✅ DeepSeek-Coder-V2 (16B) model running locally via Ollama
- ✅ Configuration system (YAML files in `/config`)
- ✅ MCP servers for specification and code editing
- ✅ Two working agents: ProjectManager and Coder
- ✅ CLI interface (`main.py`)
- ✅ Workflow definitions

## Prerequisites Completed

- [x] Python 3.13.7 installed
- [x] Virtual environment created
- [x] Dependencies installed (CrewAI, Anthropic, Ollama client, etc.)
- [x] Ollama running with DeepSeek-Coder-V2 16B model on F: drive
- [x] spec-kit installed

## Next Steps to Use the System

### 1. Set Up API Keys (Required for Cloud Models)

Edit the `.env` file and add your API keys:

```bash
# For Claude models (ProjectManager agent)
ANTHROPIC_API_KEY=your_api_key_here

# Optional: For OpenAI models
OPENAI_API_KEY=your_openai_key_here

# GitHub integration (optional, for PR creation)
GITHUB_TOKEN=your_github_token_here
```

**Note:** The Coder agent uses DeepSeek (local model via Ollama) and doesn't require an API key. The ProjectManager agent is configured to use Claude Sonnet 4, which requires an Anthropic API key.

### 2. Start Ollama (If Not Running)

Make sure Ollama is running:

```bash
ollama serve
```

Verify the DeepSeek model is available:

```bash
ollama list
```

You should see `deepseek-coder-v2:16b` in the list.

### 3. Test the System

Check system status:

```bash
python main.py status
```

You should see:
- 2 initialized agents (project_manager, coder)
- 4 available workflows

### 4. Run Your First Workflow

Try the feature implementation workflow:

```bash
python main.py run --workflow feature_implementation --input "Create a simple calculator function that can add, subtract, multiply, and divide two numbers"
```

## Available Commands

```bash
# Initialize and verify configuration
python main.py init

# Display system status
python main.py status

# Run a workflow
python main.py run --workflow <workflow_name> --input "<your requirement>"

# Interactive mode (coming soon)
python main.py interactive

# Cost report (coming soon)
python main.py cost-report
```

## Available Workflows

1. **feature_implementation**: Complete feature from spec to implementation
   - Agents: project_manager, architect, coder, tester, reviewer
   - Best for: New features

2. **bug_fix**: Analyze and fix bugs
   - Agents: project_manager, coder, tester, reviewer
   - Best for: Debugging issues

3. **refactoring**: Refactor code safely
   - Agents: architect, coder, tester, reviewer
   - Best for: Code improvements

4. **code_review**: Review existing code
   - Agents: reviewer
   - Best for: Code quality checks

## Configuration

All configuration is in the `/config` directory:

- `agents.yaml` - Agent definitions and model assignments
- `models.yaml` - LLM model configuration (local and cloud)
- `workflows.yaml` - Workflow definitions
- `settings.yaml` - Global system settings

## Cost Management

The system is designed for cost-efficient operation:

- **Local Model (DeepSeek):** $0 cost - Used by Coder agent (70% of tasks)
- **Cloud Models (Claude):** Pay-per-use - Used by ProjectManager for complex analysis

Monitor your cost in the `.env` file:
```bash
DAILY_BUDGET_USD=50.0
```

## Example Usage

### Example 1: Implement a New Feature

```bash
python main.py run --workflow feature_implementation \
  --input "Add JWT-based authentication with refresh tokens"
```

The system will:
1. ProjectManager creates a detailed specification
2. Architect designs the architecture (when implemented)
3. Coder implements the code
4. Tester writes and runs tests (when implemented)
5. Reviewer checks code quality (when implemented)

### Example 2: Fix a Bug

```bash
python main.py run --workflow bug_fix \
  --input "Fix issue where user login fails with special characters in password"
```

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not found"

**Solution:** Add your Anthropic API key to the `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Issue: "Ollama connection failed"

**Solution:** Make sure Ollama is running:
```bash
ollama serve
```

### Issue: "Model not found"

**Solution:** Pull the DeepSeek model:
```bash
ollama pull deepseek-coder-v2:16b
```

### Issue: Agent not initializing

**Solution:** Check the logs:
```bash
cat logs/agent_system.log
```

## What's Next?

### Phase 1 (Current)
- [x] Project structure
- [x] Configuration system
- [x] Local LLM setup (DeepSeek)
- [x] Basic MCP servers
- [x] ProjectManager and Coder agents
- [ ] Architect, Tester, Reviewer agents (to be implemented)
- [ ] Full MCP server integration

### Phase 2 (Upcoming)
- [ ] Remaining agents (Architect, Tester, Reviewer)
- [ ] Full MCP server integration with CrewAI tools
- [ ] Cost tracking and dashboard
- [ ] GitHub integration (PR creation, issue management)
- [ ] Testing framework integration

### Phase 3 (Future)
- [ ] Temporal workflow engine
- [ ] Advanced routing and optimization
- [ ] RAG/memory system
- [ ] Production deployment tools

## Getting Help

- Check the logs in `logs/agent_system.log`
- Review configuration files in `/config`
- Read the full [README.md](README.md) for detailed documentation
- Check [Architecture Documentation](docs/architecture.md) for system design

## Tips for Best Results

1. **Be Specific:** Provide clear, detailed requirements for better results
2. **Start Small:** Test with simple features first
3. **Review Specs:** Check the generated specifications before implementation
4. **Monitor Costs:** Keep an eye on API usage for cloud models
5. **Use Local Models:** DeepSeek handles most coding tasks well at $0 cost

---

**You're ready to go!** Start with `python main.py status` to verify everything is working.
