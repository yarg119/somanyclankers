# Interactive Wizard Guide - Clanker Inc

## Overview

The **Interactive Wizard** provides a beautiful, guided experience for setting up projects with customized AI agent behaviors. Instead of manually configuring agents or writing complex prompts, simply answer questions and let the wizard customize your development team.

## Quick Start

Run the interactive wizard:

```bash
python main.py clanker
```

That's it! The wizard will guide you through everything.

## What the Wizard Does

### 1. Project Setup
- Asks about your project name, type, and description
- Gathers technology stack preferences (language, framework, database)
- Understands your coding style preferences
- Learns your testing requirements
- Configures security and performance priorities

### 2. Agent Customization
Based on your answers, the wizard **automatically customizes each agent**:

- **Coder Agent**: Tailored to your language, framework, and coding style
- **Architect Agent**: Specialized for your project type and requirements
- **Tester Agent**: Configured for your testing approach and coverage targets
- **Reviewer Agent**: Focused on your security and quality standards

### 3. Workflow Execution
After gathering preferences, the wizard:
- Initializes agents with custom prompts
- Runs the full `feature_implementation` workflow
- Creates actual code files matching your specifications

## The Wizard Steps

### Step 1: Project Information
```
What is your project name?
Provide a brief description:
What type of project? (Web App, API, CLI, etc.)
```

### Step 2: Technology Stack
```
Primary programming language?
Which framework/library? (context-aware based on your project type)
Database preference?
```

**Smart Framework Selection**: The wizard shows relevant frameworks based on your language and project type. For example:
- Python + Web App → FastAPI, Django, Flask
- Python + CLI → Click, Typer, Argparse
- TypeScript + API → NestJS, Express

### Step 3: Code Style & Quality
```
Preferred code style approach?
  - Conservative (defensive programming, lots of validation)
  - Balanced (pragmatic, standard best practices)
  - Modern (latest features, cutting-edge patterns)
  - Minimal (simple, YAGNI principle)
  - Enterprise (extensive documentation, patterns)

Documentation detail level?
Type safety / type hints?
Code comments preference?
```

### Step 4: Testing Requirements
```
Testing approach?
  - TDD (Test-Driven Development)
  - Comprehensive (unit + integration + e2e)
  - Standard (unit + integration)
  - Basic (unit tests only)
  - Minimal (critical paths only)

Test coverage target? (90%+, 80%+, 70%+, etc.)
```

### Step 5: Security & Performance
```
Security focus level?
  - Maximum (financial/healthcare grade)
  - High (user data, authentication)
  - Standard (basic security practices)
  - Basic (common vulnerabilities only)

Performance priority?
Error handling approach?
```

### Step 6: Development Workflow
```
Which agents should work on this project?
  ☑ Project Manager (requirements & specs)
  ☑ Architect (system design)
  ☑ Coder (implementation)
  ☑ Tester (test creation)
  ☑ Reviewer (code review)

Use premium models (Claude/GPT-4) for better quality?
```

## Example Session

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    🤖 CLANKER INC 🤖                         ║
║                                                              ║
║            Automated Coding Agent Network                    ║
║        AI-Powered Software Development at Scale              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

What is your project name?
> Task Manager API

Provide a brief description:
> A REST API for managing tasks with user authentication

What type of project are you building?
❯ REST API / Backend Service

Primary programming language?
❯ Python

Which framework/library would you like to use?
❯ FastAPI

Database preference?
❯ PostgreSQL

Preferred code style approach?
❯ Modern (latest features, cutting-edge patterns)

Documentation detail level?
❯ Comprehensive (full API docs, examples, guides)

Testing approach?
❯ Comprehensive (unit + integration + e2e)

Test coverage target?
❯ 80%+ (high coverage)

Security focus level?
❯ High (user data, authentication)

Performance priority?
❯ High (performance-first approach)
```

## How Agent Customization Works

### Before Wizard (Generic)
```python
# Generic Coder prompt
"You are a senior software engineer who writes clean code..."
```

### After Wizard (Customized)
```python
# Customized based on your choices:
"You are an expert Python developer specializing in FastAPI.
You use the latest Python features and cutting-edge patterns.
You write detailed docstrings, README files, and usage examples.
You add comprehensive type hints to all functions and use strict type checking.
You are security-conscious and implement proper input validation..."
```

## Benefits

### 1. **Zero Configuration**
No need to manually edit YAML files or agent prompts. Just answer questions.

### 2. **Intelligent Defaults**
The wizard makes smart suggestions based on your previous choices.

### 3. **Consistent Quality**
Agents work together with aligned understanding of your requirements.

### 4. **Reproducible**
Your choices create a consistent development approach across all agents.

### 5. **Time Saving**
5 minutes of questions vs. hours of manual configuration.

## Advanced Usage

### Combining with Direct Commands

After using the wizard once, you can use the standard commands for quick iterations:

```bash
# Full wizard experience
python main.py clanker

# Quick command for small tasks
python main.py run --workflow feature_implementation --input "Add email validation"

# Just review existing code
python main.py run --workflow code_review --input "Review src/auth.py"
```

### Future: Save & Reuse Configurations

*Coming soon: Save your wizard configurations as templates*

```bash
# Save configuration
python main.py clanker --save-template enterprise-web-app

# Reuse later
python main.py clanker --template enterprise-web-app
```

### Future: Spec-Kit Integration

*Planned: Integration with GitHub's spec-kit for advanced documentation*

The wizard will support:
- Generating spec-kit compatible project specifications
- Auto-generating architecture diagrams
- Creating comprehensive API documentation
- Building detailed technical specs

## Tips for Best Results

### 1. Be Specific in Project Description
Instead of: "A web app"
Better: "A task management web app with teams, projects, and real-time collaboration"

### 2. Match Your Actual Needs
Don't choose "Maximum security" for a personal todo app. Be realistic.

### 3. Start Balanced, Then Iterate
Use "Balanced" or "Standard" options first. You can always refine later.

### 4. Use Premium Models for Complex Projects
For production systems, using Claude/GPT-4 provides significantly better quality.

### 5. Review the Summary Carefully
The wizard shows a configuration summary before proceeding. Review it!

## Troubleshooting

### Wizard Crashes or Errors

```bash
# Check Python version (need 3.10+)
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Check terminal encoding
# On Windows, use Windows Terminal or enable UTF-8
```

### Agents Not Customizing

The wizard creates dynamic prompts that override the default YAML configurations. If agents seem to ignore your preferences:

1. Check that agents initialized successfully
2. Look for "Initializing agents..." messages
3. Verify no errors in the log output

### Can't See Interactive Prompts

If you don't see the interactive selections:
- Use a modern terminal (Windows Terminal, iTerm2, etc.)
- Don't redirect output (don't use `python main.py clanker > file.txt`)
- Ensure terminal supports ANSI colors

## Command Reference

```bash
# Start interactive wizard
python main.py clanker

# Show system status
python main.py status

# List all workflows
python main.py list-workflows

# List all agents
python main.py list-agents

# Run workflow directly (skip wizard)
python main.py run --workflow WORKFLOW_NAME --input "description"
```

## What Gets Created

After running the wizard, you'll find:

```
automated-coding-agent-network/
├── specifications/
│   └── [project_name]_specification.md    # Detailed project spec
├── src/
│   └── [implementation files]              # Your code
├── tests/
│   └── test_[files].py                     # Comprehensive tests
└── [other project files]
```

## Next Steps

After completing the wizard:

1. **Review the Generated Spec**: Check `specifications/` folder
2. **Examine the Code**: Look at `src/` implementation
3. **Run the Tests**: Execute `pytest tests/`
4. **Iterate**: Run additional workflows for enhancements
5. **Review**: Use `code_review` workflow for final check

---

**Welcome to Clanker Inc - Where AI Agents Build Your Dreams! 🤖**
