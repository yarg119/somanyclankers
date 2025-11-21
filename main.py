"""
Automated Coding Agent Network - Main Orchestrator
Multi-agent system for automated software development.
"""

import os
import asyncio
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import typer
import logging

# Load environment variables FIRST
load_dotenv()

# Import agents
from agents import (
    BaseAgent,
    AgentConfig,
    ProjectManagerAgent,
    ArchitectAgent,
    CoderAgent,
    TesterAgent,
    ReviewerAgent
)

# Import tools
from tools.code_extractor import process_coder_output

# Import interactive wizard
from interactive_wizard import ProjectWizard

# Import project manager
from project_manager import ProjectManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Rich console
console = Console()

# Initialize Typer CLI app
app = typer.Typer(
    name="acan",
    help="Automated Coding Agent Network - Multi-agent software development system",
    add_completion=False
)


class AgentOrchestrator:
    """Orchestrates multiple AI agents for software development tasks."""

    def __init__(self, config_dir: str = "config", project_path: Optional[str] = None):
        """Initialize the orchestrator with configuration."""
        self.config_dir = Path(config_dir)
        self.project_path = Path(project_path) if project_path else Path(".")
        self.agents: Dict[str, Any] = {}
        self.workflows: Dict[str, Any] = {}
        self.config = {}

        # Load configurations
        self._load_config()

    def _load_config(self):
        """Load all configuration files."""
        try:
            # Load agent configurations
            agents_config_path = self.config_dir / "agents.yaml"
            with open(agents_config_path, 'r') as f:
                agents_config = yaml.safe_load(f)
                self.config['agents'] = agents_config.get('agents', {})

            # Load workflow configurations
            workflows_config_path = self.config_dir / "workflows.yaml"
            with open(workflows_config_path, 'r') as f:
                workflows_config = yaml.safe_load(f)
                self.config['workflows'] = workflows_config.get('workflows', {})

            logger.info("Configuration loaded successfully")

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise

    def _initialize_agent(self, agent_name: str, agent_config: dict, customizations: Optional[Dict[str, Any]] = None) -> Optional[object]:
        """Initialize a specific agent with optional customizations."""
        try:
            # Apply customizations if provided
            if customizations and agent_name in customizations:
                custom = customizations[agent_name]
                if 'backstory' in custom:
                    agent_config['backstory'] = custom['backstory']
                if 'goal' in custom:
                    agent_config['goal'] = custom['goal']
                if 'role' in custom:
                    agent_config['role'] = custom['role']

            config = AgentConfig(
                name=agent_name,
                role=agent_config.get('role', ''),
                goal=agent_config.get('goal', ''),
                backstory=agent_config.get('backstory', ''),
                model=agent_config.get('model', 'deepseek-coder-v2:16b'),
                temperature=agent_config.get('temperature', 0.7),
                tools=agent_config.get('tools', []),
                fallback_model=agent_config.get('fallback_model'),
                base_directory=str(self.project_path) if self.project_path != Path(".") else None
            )

            # Initialize the appropriate agent class
            agent = None
            if agent_name == "project_manager":
                agent = ProjectManagerAgent(config)
            elif agent_name == "architect":
                agent = ArchitectAgent(config)
            elif agent_name == "coder":
                agent = CoderAgent(config)
                # Setup Aider integration if enabled
                if agent_config.get('use_aider', False):
                    agent.setup_aider(
                        project_path=str(self.project_path),
                        use_aider=True,
                        aider_settings=agent_config.get('aider_settings', {})
                    )
            elif agent_name == "tester":
                agent = TesterAgent(config)
            elif agent_name == "reviewer":
                agent = ReviewerAgent(config)
            else:
                logger.warning(f"Unknown agent type: {agent_name}")
                return None

            return agent

        except Exception as e:
            logger.error(f"Error initializing agent {agent_name}: {e}")
            return None

    def initialize_agents(self, customizations: Optional[Dict[str, Any]] = None):
        """Initialize all enabled agents with optional customizations."""
        console.print("\n[cyan]Initializing agents...[/cyan]")

        for agent_name, agent_config in self.config['agents'].items():
            # Skip disabled agents
            if not agent_config.get('enabled', True):
                console.print(f"  - Skipping {agent_name} (disabled)")
                continue

            console.print(f"  - Initializing {agent_name}...")

            agent = self._initialize_agent(agent_name, agent_config, customizations)
            if agent:
                self.agents[agent_name] = agent
                logger.info(f"Agent {agent_name} initialized successfully")

        console.print(f"\n[green]Initialized {len(self.agents)} agents[/green]")

    async def execute_workflow_step(
        self,
        step_name: str,
        agent_name: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute a single workflow step."""
        console.print(f"\n[bold cyan]Step:[/bold cyan] {step_name}")
        console.print(f"[cyan]Agent:[/cyan] {agent_name}")

        # Get the agent
        agent = self.agents.get(agent_name)
        if not agent:
            console.print(f"[yellow]Agent '{agent_name}' not initialized[/yellow]")
            return None

        try:
            # Execute based on agent type
            result = None

            if agent_name == "project_manager":
                if 'user_requirement' in context:
                    result = await agent.analyze_requirements(context['user_requirement'])

            elif agent_name == "architect":
                if 'specification' in context:
                    result = await agent.design_architecture(context['specification'])

            elif agent_name == "coder":
                if 'specification' in context:
                    result = await agent.implement_feature(context['specification'])

                    # Post-process to extract and create files
                    console.print(f"\n[cyan]Post-processing code extraction...[/cyan]")
                    extraction_result = process_coder_output(result['summary'])

                    result['files_created'] = extraction_result['files_created']
                    result['files_modified'] = extraction_result['files_modified']
                    result['extraction_summary'] = extraction_result['summary']

                    console.print(f"\n[green]Implementation complete[/green]")
                    console.print(extraction_result['summary'])
                else:
                    console.print("[yellow]Skipping - no specification available[/yellow]")
                    return None

            elif agent_name == "tester":
                if 'specification' in context and 'code' in context:
                    result = await agent.create_tests(
                        context['specification'],
                        context['code']
                    )

            elif agent_name == "reviewer":
                if 'specification' in context and 'code' in context:
                    result = await agent.review_code(
                        context['code'],
                        context['specification']
                    )

            return result

        except Exception as e:
            logger.error(f"Error executing step {step_name}: {e}")
            console.print(f"[red]Error:[/red] {e}")
            return None

    async def run_workflow(self, workflow_name: str, input_data: str):
        """Run a complete workflow."""
        workflow = self.config['workflows'].get(workflow_name)
        if not workflow:
            console.print(f"[red]Workflow '{workflow_name}' not found[/red]")
            return

        # Display workflow info
        table = Table(title=f"Running Workflow: {workflow_name}", show_header=False)
        table.add_row("Input:", input_data)
        console.print(table)

        # Initialize context with user input
        context = {
            'user_requirement': input_data,
            'workflow_results': {}
        }

        # Execute workflow steps
        for step in workflow.get('steps', []):
            step_name = step.get('name')
            agent_name = step.get('agent')

            result = await self.execute_workflow_step(step_name, agent_name, context)

            if result:
                # Update context with results
                context['workflow_results'][step_name] = result

                # Extract key data for next steps
                if 'specification' in result:
                    context['specification'] = result['specification']
                if 'architecture' in result:
                    context['architecture'] = result['architecture']
                if 'code' in result or 'summary' in result:
                    context['code'] = result.get('code', result.get('summary', ''))

        console.print("\n[green]Workflow completed![/green]")

    def show_status(self):
        """Display system status."""
        # Header
        console.print(Panel.fit(
            "[bold cyan]Automated Coding Agent Network[/bold cyan]\n"
            "Multi-agent system for automated software development",
            border_style="cyan"
        ))

        # Agents table
        agents_table = Table(title="Initialized Agents", show_header=True)
        agents_table.add_column("Agent", style="cyan")
        agents_table.add_column("Model", style="green")
        agents_table.add_column("Status", style="yellow")

        for agent_name in self.config['agents'].keys():
            agent_config = self.config['agents'][agent_name]
            if not agent_config.get('enabled', True):
                continue

            status = "[OK] Ready" if agent_name in self.agents else "[X] Not initialized"
            model = agent_config.get('model', 'N/A')
            agents_table.add_row(agent_name, model, status)

        console.print(agents_table)

        # Workflows table
        workflows_table = Table(title="Available Workflows", show_header=True)
        workflows_table.add_column("Workflow", style="cyan")
        workflows_table.add_column("Steps", style="green")

        for workflow_name, workflow_config in self.config['workflows'].items():
            steps_count = len(workflow_config.get('steps', []))
            workflows_table.add_row(workflow_name, str(steps_count))

        console.print(workflows_table)


# CLI Commands

@app.command()
def status():
    """Show system status and available agents/workflows."""
    orchestrator = AgentOrchestrator()
    orchestrator.initialize_agents()
    orchestrator.show_status()


@app.command()
def run(
    workflow: str = typer.Option(..., "--workflow", "-w", help="Workflow to run"),
    input: str = typer.Option(..., "--input", "-i", help="Input requirement/description")
):
    """Run a workflow with the given input."""
    orchestrator = AgentOrchestrator()
    orchestrator.initialize_agents()

    # Run workflow
    asyncio.run(orchestrator.run_workflow(workflow, input))


@app.command()
def list_workflows():
    """List all available workflows."""
    config_path = Path("config/workflows.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    table = Table(title="Available Workflows")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Steps", style="yellow")

    for name, workflow in config.get('workflows', {}).items():
        description = workflow.get('description', 'N/A')
        steps = len(workflow.get('steps', []))
        table.add_row(name, description, str(steps))

    console.print(table)


@app.command()
def list_agents():
    """List all available agents."""
    config_path = Path("config/agents.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    table = Table(title="Available Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Role", style="green")
    table.add_column("Model", style="yellow")
    table.add_column("Enabled", style="magenta")

    for name, agent in config.get('agents', {}).items():
        role = agent.get('role', 'N/A')
        model = agent.get('model', 'N/A')
        enabled = "Yes" if agent.get('enabled', True) else "No"
        table.add_row(name, role, model, enabled)

    console.print(table)


@app.command()
def results(project: Optional[str] = typer.Option(None, "--project", "-p", help="Show results for specific project")):
    """
    Show all generated files and results from agent workflows.

    Displays specifications, code files, tests, and other artifacts
    created by the agent team.
    """
    from pathlib import Path
    import os

    # Determine base directory
    if project:
        pm = ProjectManager()
        base_path = pm.get_project(project)
        if not base_path:
            console.print(f"\n[red]Project '{project}' not found.[/red]")
            console.print("[cyan]List projects with:[/cyan] python main.py list-projects\n")
            return
        console.print(f"\n[bold cyan]Results for Project: {project}[/bold cyan]\n")
    else:
        base_path = Path(".")
        console.print("\n[bold cyan]Agent Workflow Results[/bold cyan]\n")

    # Check specifications
    spec_dir = base_path / "specifications"
    if spec_dir.exists() and list(spec_dir.glob("*.md")):
        console.print("[bold][SPEC] Specifications:[/bold]")
        for file in sorted(spec_dir.glob("*.md"), key=os.path.getmtime, reverse=True):
            size = file.stat().st_size / 1024  # KB
            console.print(f"  - {file.name} ({size:.1f} KB)")
        console.print()

    # Check source code
    src_dir = base_path / "src"
    if src_dir.exists() and any(src_dir.rglob("*")):
        console.print("[bold][CODE] Source Code:[/bold]")
        for ext in ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.java", "*.go"]:
            files = list(src_dir.rglob(ext))
            for file in sorted(files):
                console.print(f"  - {file.relative_to(base_path)}")
        console.print()

    # Check tests
    test_dirs = [base_path / "tests", base_path / "test", base_path / "__tests__"]
    test_files_found = False
    for test_dir in test_dirs:
        if test_dir.exists() and any(test_dir.rglob("*")):
            if not test_files_found:
                console.print("[bold][TEST] Tests:[/bold]")
                test_files_found = True
            for file in sorted(test_dir.rglob("*")):
                if file.is_file():
                    console.print(f"  - {file.relative_to(base_path)}")
    if test_files_found:
        console.print()

    # Check other important files
    important_files = ["README.md", "package.json", "requirements.txt", ".env.example"]
    found_files = [f for f in important_files if (base_path / f).exists()]
    if found_files:
        console.print("[bold][FILE] Other Files:[/bold]")
        for file in found_files:
            console.print(f"  - {file}")
        console.print()

    # Quick stats
    console.print("[bold cyan]Quick Stats:[/bold cyan]")
    spec_count = len(list(spec_dir.glob("*.md"))) if spec_dir.exists() else 0
    src_count = len(list(src_dir.rglob("*"))) if src_dir.exists() else 0
    test_count = sum(len(list(td.rglob("*"))) for td in test_dirs if td.exists())

    console.print(f"  - Specifications: {spec_count}")
    console.print(f"  - Source files: {src_count}")
    console.print(f"  - Test files: {test_count}\n")

    # Tips
    console.print("[bold][TIP] Tips:[/bold]")
    console.print("  • View specs: [cyan]cat specifications/<filename>[/cyan]")
    console.print("  • Open code: [cyan]code src/[/cyan] (if using VS Code)")
    console.print("  • Run tests: [cyan]pytest tests/[/cyan] or [cyan]npm test[/cyan]\n")


@app.command()
def list_projects():
    """
    List all projects created with Clanker.

    Shows project names, creation dates, and iteration counts.
    """
    pm = ProjectManager()
    projects = pm.list_projects()

    if not projects:
        console.print("\n[yellow]No projects found.[/yellow]")
        console.print("[cyan]Create your first project with:[/cyan] python main.py clanker\n")
        return

    console.print("\n[bold cyan]Your Projects:[/bold cyan]\n")

    table = Table(show_header=True)
    table.add_column("Project Name", style="cyan")
    table.add_column("Created", style="green")
    table.add_column("Iterations", style="yellow")
    table.add_column("Path", style="dim")

    for project in projects:
        table.add_row(
            project['name'],
            project.get('created_at', 'Unknown')[:10] if project.get('created_at') else 'Unknown',
            str(project.get('iterations', 0)),
            project['path']
        )

    console.print(table)
    console.print()


@app.command()
def continue_project(
    project: str = typer.Option(..., "--project", "-p", help="Project name to continue"),
    feedback: str = typer.Option(..., "--feedback", "-f", help="What needs improvement")
):
    """
    Continue working on an existing project with new requirements or feedback.

    Use this when the initial implementation doesn't meet your requirements.
    """
    pm = ProjectManager()
    project_path = pm.get_project(project)

    if not project_path:
        console.print(f"\n[red]Project '{project}' not found.[/red]")
        console.print("[cyan]List projects with:[/cyan] python main.py list-projects\n")
        return

    console.print(f"\n[bold cyan]Continuing work on:[/bold cyan] {project}")
    console.print(f"[bold cyan]Feedback:[/bold cyan] {feedback}\n")

    # Load project context
    context_data = pm.get_project_context(project)

    # Build continuation prompt
    continuation_prompt = f"""
CONTINUATION TASK - Project: {project}

FEEDBACK FROM USER:
{feedback}

EXISTING PROJECT CONTEXT:
- Specifications created: {len(context_data.get('specifications', []))}
- Source files: {len(context_data.get('source_files', []))}
- Test files: {len(context_data.get('test_files', []))}
- Previous iterations: {len(context_data.get('iterations', []))}

YOUR TASK:
1. Review the feedback above
2. Address the user's concerns
3. Improve/fix the implementation
4. Create or update files as needed

CRITICAL: Use write_file() to update existing files or create new ones.
Work in the existing project directory: {project_path}
"""

    # Create orchestrator with project path
    orchestrator = AgentOrchestrator(project_path=str(project_path))
    orchestrator.initialize_agents()

    # Run workflow with continuation context
    asyncio.run(orchestrator.run_workflow('feature_implementation', continuation_prompt))

    # Record this iteration
    pm.add_iteration(project, feedback, "Iteration completed")

    console.print(f"\n[green]Iteration complete! Check results in:[/green] {project_path}\n")


@app.command()
def clanker():
    """
    Start the interactive project wizard.

    This launches the Clanker Inc interactive interface that guides you through
    setting up a project with customized agent prompts based on your preferences.
    """
    try:
        # Run the wizard
        wizard = ProjectWizard()
        result = wizard.run()

        if not result:
            console.print("[yellow]Wizard cancelled.[/yellow]")
            return

        # Extract configuration
        project_config = result['project_config']
        agent_customizations = result['agent_customizations']

        # Create project directory structure
        pm = ProjectManager()
        project_path = pm.create_project(project_config['name'], config=project_config)

        console.print(f"\n[green]Created project directory:[/green] {project_path}")
        console.print(f"[cyan]All files will be generated in this directory.[/cyan]\n")

        # Create orchestrator with project path and customizations
        orchestrator = AgentOrchestrator(project_path=str(project_path))
        orchestrator.initialize_agents(customizations=agent_customizations)

        # Build project description from wizard input
        project_description = f"""
Project: {project_config['name']}
Type: {project_config['type']}
Description: {project_config['description']}

Technology Stack:
- Language: {project_config['language']}
- Framework: {project_config['framework']}
- Database: {project_config['database']}

Requirements:
- Code Style: {project_config['code_style']}
- Documentation: {project_config['documentation']}
- Testing: {project_config['testing_approach']} (Target: {project_config['coverage_target']})
- Security Level: {project_config['security_level']}
- Performance: {project_config['performance_priority']}
- Error Handling: {project_config['error_handling']}

Please create a complete implementation following these specifications.

IMPORTANT: All files must be created in the project directory structure:
- Specifications go in: specifications/
- Source code goes in: src/
- Tests go in: tests/
- Documentation goes in: docs/
"""

        # Run the workflow
        asyncio.run(orchestrator.run_workflow('feature_implementation', project_description))

        console.print(f"\n[bold green]Project Complete![/bold green]")
        console.print(f"[cyan]Location:[/cyan] {project_path}")
        console.print(f"[cyan]View results:[/cyan] python main.py results --project \"{project_config['name']}\"\n")

    except Exception as e:
        console.print(f"[red]Error running wizard: {e}[/red]")
        logger.error(f"Wizard error: {e}", exc_info=True)


if __name__ == "__main__":
    app()
