"""
Coder Agent
Responsible for implementing features based on specifications.
"""

from typing import Any, Dict, List, Optional
import asyncio
from pathlib import Path

from ..base_agent import BaseAgent, AgentConfig
from crewai import Task


class CoderAgent(BaseAgent):
    """
    Coder agent specializes in:
    - Implementing features based on specifications
    - Writing clean, maintainable code
    - Following best practices and design patterns
    - Creating or modifying files as needed
    """

    def __init__(self, config: AgentConfig):
        """Initialize Coder agent."""
        # Set default configuration for Coder if not provided
        if not config.role:
            config.role = "Senior Software Engineer and Code Implementation Specialist"

        if not config.goal:
            config.goal = (
                "Implement high-quality, maintainable code based on specifications. "
                "Write code that is clean, well-documented, and follows best practices."
            )

        if not config.backstory:
            config.backstory = (
                "You are a senior software engineer with extensive experience in multiple programming languages "
                "and frameworks. You have a deep understanding of software design patterns, best practices, and "
                "clean code principles. You write code that is not only functional but also maintainable, testable, "
                "and scalable. You always consider edge cases and error handling in your implementations."
            )

        super().__init__(config)

        # Initialize Aider integration if enabled
        self.aider_tool = None
        self.use_aider = False

    def setup_aider(self, project_path: str, use_aider: bool = False, aider_settings: Optional[Dict] = None):
        """
        Set up Aider for this project.

        Args:
            project_path: Path to the project directory
            use_aider: Whether to use Aider for implementation
            aider_settings: Optional Aider configuration
        """
        if not use_aider:
            return

        try:
            from tools.aider_tool import AiderTool

            settings = aider_settings or {}
            self.aider_tool = AiderTool(
                project_path=project_path,
                model=self.config.model,
                auto_commit=settings.get('auto_commit', False)
            )

            # Check if Aider is available
            if self.aider_tool.check_aider_available():
                self.use_aider = True
                print(f"[OK] Aider integration enabled for {project_path}")
            else:
                print("[WARNING] Aider not available. Install with: py -3.11 -m pip install aider-chat")
                print("[WARNING] Falling back to text-based code generation")
                self.aider_tool = None
                self.use_aider = False

        except Exception as e:
            print(f"[WARNING] Failed to initialize Aider: {e}")
            print("[WARNING] Falling back to text-based code generation")
            self.aider_tool = None
            self.use_aider = False

    async def execute(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute a code implementation task.

        Args:
            task_description: Description of the code to implement
            context: Optional context (e.g., specification, existing code)

        Returns:
            Result containing the implemented code and changes made
        """
        context = context or {}

        # Create the task for this agent
        task = self.create_task(
            description=task_description,
            expected_output=(
                "Implementation result with:\n"
                "1. List of files created/modified\n"
                "2. Summary of changes made\n"
                "3. Key implementation decisions\n"
                "4. Any assumptions made\n"
                "5. Suggestions for testing"
            ),
            context=context.get("previous_tasks", [])
        )

        # Execute the task using CrewAI
        result = self.execute_task_sync(task)

        return result

    async def implement_feature(
        self,
        specification: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Implement a feature based on a specification.

        Args:
            specification: The specification to implement
            context: Optional context (existing codebase info, etc.)

        Returns:
            Dictionary containing:
            - files_modified: List of files that were modified
            - files_created: List of files that were created
            - summary: Summary of implementation
            - testing_notes: Suggestions for testing
        """
        context = context or {}

        # Use Aider if available
        if self.use_aider and self.aider_tool:
            print("[AIDER] Using Aider for code generation...")
            try:
                result = self.aider_tool.implement_feature(
                    specification=specification,
                    files=[],  # Let Aider decide which files to create
                    create_new=True
                )

                if result['success']:
                    print(f"[AIDER] Created {len(result['files_modified'])} file(s)")
                    return {
                        "files_modified": result['files_modified'],
                        "files_created": result['files_modified'],  # Aider doesn't distinguish
                        "summary": result['output'],
                        "testing_notes": "Run tests to verify implementation"
                    }
                else:
                    print(f"[ERROR] Aider failed: {result.get('error', 'Unknown error')}")
                    print("[WARNING] Falling back to text-based generation")
                    # Fall through to text-based approach
            except Exception as e:
                print(f"[ERROR] Aider error: {e}")
                print("[WARNING] Falling back to text-based generation")
                # Fall through to text-based approach

        # Fallback to text-based generation
        print("[FALLBACK] Using text-based code generation...")
        task_description = f"""
        === IMPLEMENTATION TASK ===

        Specification to implement:
        {specification}

        === CRITICAL OUTPUT FORMAT REQUIREMENT ===
        You MUST output code in this EXACT format for EACH file:

        #### File: `path/to/filename.py`
        ```python
        # Complete, production-ready code here
        # NO placeholders, NO TODO comments
        # 100% working code
        ```

        === EXAMPLE OUTPUT FORMAT ===

        #### File: `src/app.py`
        ```python
        from flask import Flask, jsonify

        app = Flask(__name__)

        @app.route('/')
        def home():
            return jsonify({{"message": "Hello World"}})

        if __name__ == '__main__':
            app.run(debug=True, port=5000)
        ```

        #### File: `src/config.py`
        ```python
        import os

        class Config:
            DEBUG = os.getenv('DEBUG', 'False') == 'True'
            PORT = int(os.getenv('PORT', 5000))
            DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
        ```

        === MANDATORY REQUIREMENTS ===
        1. Create AT LEAST 5-10 files
        2. Use the EXACT format above for EACH file
        3. Include complete, working code (NO placeholders)
        4. Add all imports, error handling, and logic
        5. Make it production-ready

        === FILE STRUCTURE TO CREATE ===
        - Main application file (src/app.py or src/main.js)
        - Configuration file (src/config.py or src/config.js)
        - Models/data structures (src/models/)
        - Routes/endpoints (src/routes/ or src/api/)
        - Utilities (src/utils/)
        - README.md
        - requirements.txt or package.json
        - .env.example

        === CRITICAL ===
        Output ONLY in the format above. Do NOT describe, do NOT explain.
        Just output: #### File: `path` followed by ```language code block

        START NOW!
        """

        result = await self.execute(task_description, context)

        return {
            "files_modified": self._extract_files_modified(result),
            "files_created": self._extract_files_created(result),
            "summary": result,
            "testing_notes": self._extract_testing_notes(result)
        }

    async def refactor_code(
        self,
        file_path: str,
        refactoring_goal: str
    ) -> str:
        """
        Refactor existing code.

        Args:
            file_path: Path to the file to refactor
            refactoring_goal: Description of the refactoring goal

        Returns:
            Summary of refactoring changes
        """
        task_description = f"""
        Refactor the code in {file_path} with the following goal:

        {refactoring_goal}

        Your refactoring should:
        1. Maintain the same functionality
        2. Improve code quality, readability, or performance
        3. Follow best practices and design patterns
        4. Update documentation as needed
        5. Ensure backward compatibility (if applicable)

        Provide a clear summary of changes made and why.
        """

        result = await self.execute(task_description)
        return result

    async def fix_bug(
        self,
        bug_description: str,
        affected_files: List[str],
        reproduction_steps: Optional[str] = None
    ) -> str:
        """
        Fix a bug in the codebase.

        Args:
            bug_description: Description of the bug
            affected_files: List of files potentially affected
            reproduction_steps: Optional steps to reproduce the bug

        Returns:
            Summary of the fix
        """
        task_description = f"""
        Fix the following bug:

        Bug Description: {bug_description}

        Potentially affected files: {', '.join(affected_files)}

        {f"Reproduction Steps:\n{reproduction_steps}" if reproduction_steps else ""}

        Your fix should:
        1. Identify the root cause
        2. Implement a proper fix (not just a workaround)
        3. Ensure the fix doesn't break other functionality
        4. Add error handling if needed
        5. Consider edge cases

        Provide a summary of:
        - Root cause analysis
        - Changes made
        - Why this fix resolves the issue
        - Suggestions for preventing similar bugs
        """

        result = await self.execute(task_description)
        return result

    def _extract_files_modified(self, result: str) -> List[str]:
        """Extract list of modified files from result."""
        files = []
        in_modified_section = False

        for line in result.split('\n'):
            if "modified" in line.lower() or "changed" in line.lower():
                in_modified_section = True
                continue

            if in_modified_section:
                if line.startswith('##'):
                    break
                # Look for file paths
                if '.py' in line or '.js' in line or '.ts' in line or '/' in line:
                    files.append(line.strip().lstrip('-* '))

        return files

    def _extract_files_created(self, result: str) -> List[str]:
        """Extract list of created files from result."""
        files = []
        in_created_section = False

        for line in result.split('\n'):
            if "created" in line.lower() or "new file" in line.lower():
                in_created_section = True
                continue

            if in_created_section:
                if line.startswith('##'):
                    break
                # Look for file paths
                if '.py' in line or '.js' in line or '.ts' in line or '/' in line:
                    files.append(line.strip().lstrip('-* '))

        return files

    def _extract_testing_notes(self, result: str) -> str:
        """Extract testing notes from result."""
        testing_section = ""
        in_testing_section = False

        for line in result.split('\n'):
            if "testing" in line.lower() or "test" in line.lower():
                in_testing_section = True

            if in_testing_section:
                testing_section += line + "\n"
                if line.startswith('##') and testing_section:
                    break

        return testing_section.strip()
