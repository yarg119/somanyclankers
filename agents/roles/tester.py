"""
Tester Agent
Responsible for creating and running tests to validate implementations.
"""

from typing import Any, Dict, List, Optional
import asyncio

from ..base_agent import BaseAgent, AgentConfig


class TesterAgent(BaseAgent):
    """
    Tester agent specializes in:
    - Writing comprehensive unit tests
    - Creating integration tests
    - Validating code against specifications
    - Ensuring edge case coverage
    """

    def __init__(self, config: AgentConfig):
        """Initialize Tester agent."""
        # Set default configuration for Tester if not provided
        if not config.role:
            config.role = "Quality Assurance and Testing Specialist"

        if not config.goal:
            config.goal = (
                "Create comprehensive test suites that ensure code quality and reliability. "
                "Validate implementations against specifications and catch edge cases."
            )

        if not config.backstory:
            config.backstory = (
                "You are a meticulous QA engineer with expertise in test-driven development. "
                "You have a keen eye for edge cases and potential bugs. You write tests that are "
                "thorough, maintainable, and provide confidence in the codebase. You understand "
                "the importance of test coverage and always validate against specifications. "
                "Your tests catch bugs before they reach production."
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
                "1. Complete unit tests for all functions\n"
                "2. Edge case tests\n"
                "3. Error condition tests\n"
                "4. Integration tests if applicable\n"
                "5. Test execution summary"
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
            Dictionary containing:
            - test_files: List of test files created
            - summary: Summary of tests created
            - coverage_notes: Notes on test coverage
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
        2. Create test files in the tests/ directory (e.g., tests/test_feature.py)
        3. Write complete, executable test code - not pseudocode or examples
        4. Include all necessary imports (unittest, pytest, etc.)

        YOUR TESTS MUST INCLUDE:
        1. Unit tests for each function/method
        2. Tests for normal cases (happy path)
        3. Tests for edge cases (empty inputs, boundaries, etc.)
        4. Tests for error conditions (invalid inputs, exceptions)
        5. Integration tests if the code has multiple components
        6. Proper test setup and teardown if needed

        REQUIRED TOOLS USAGE:
        - Use write_file(file_path="tests/test_<module>.py", content="full test code here")
        - Create multiple test files if testing multiple modules
        - Each test file should be complete and runnable

        TEST CODE REQUIREMENTS:
        - Use pytest or unittest framework
        - Add descriptive docstrings for each test
        - Use clear assertion messages
        - Group related tests in test classes
        - Follow naming convention: test_<function_name>_<scenario>

        EXAMPLE TEST STRUCTURE:
        ```python
        import unittest
        from module import function_to_test

        class TestFeatureName(unittest.TestCase):
            def test_function_normal_case(self):
                '''Test function with valid input'''
                result = function_to_test(valid_input)
                self.assertEqual(result, expected_output)

            def test_function_edge_case(self):
                '''Test function with edge case'''
                result = function_to_test(edge_case_input)
                self.assertEqual(result, expected_output)

            def test_function_error_handling(self):
                '''Test function error handling'''
                with self.assertRaises(ExpectedException):
                    function_to_test(invalid_input)
        ```

        Remember: ACTUALLY USE THE write_file TOOL to create the test files!
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
        in_files_section = False

        for line in result.split('\n'):
            if "test" in line.lower() and ("created" in line.lower() or "file" in line.lower()):
                in_files_section = True
                continue

            if in_files_section:
                if line.startswith('##'):
                    break
                # Look for file paths
                if 'test_' in line and '.py' in line:
                    files.append(line.strip().lstrip('-* '))

        return files

    def _extract_coverage_notes(self, result: str) -> str:
        """Extract coverage notes from result."""
        coverage_section = ""
        in_coverage_section = False

        for line in result.split('\n'):
            if "coverage" in line.lower() or "test summary" in line.lower():
                in_coverage_section = True

            if in_coverage_section:
                coverage_section += line + "\n"
                # Stop at next major section
                if line.startswith('##') and coverage_section:
                    break

        return coverage_section.strip() if coverage_section else "No coverage notes provided"
