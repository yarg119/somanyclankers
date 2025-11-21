"""
Aider Integration Tool
Wraps Aider CLI for programmatic code generation.
"""

import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AiderTool:
    """
    Wrapper for Aider CLI to generate real code.

    Aider is a command-line tool that uses AI to edit code files.
    This wrapper makes it easy to use Aider programmatically.
    """

    def __init__(
        self,
        project_path: str,
        model: str = "deepseek-coder-v2:16b",
        auto_commit: bool = False
    ):
        """
        Initialize Aider tool.

        Args:
            project_path: Path to the project directory
            model: Model to use (Ollama format: model_name)
            auto_commit: Whether to auto-commit changes
        """
        self.project_path = Path(project_path)
        # Use ollama_chat/ prefix as recommended by Aider documentation
        self.model = f"ollama_chat/{model}"
        self.auto_commit = auto_commit

        # Ensure project path exists
        self.project_path.mkdir(parents=True, exist_ok=True)

    def implement_feature(
        self,
        specification: str,
        files: Optional[List[str]] = None,
        create_new: bool = True
    ) -> Dict[str, any]:
        """
        Use Aider to implement a feature based on specification.

        Args:
            specification: Detailed specification of what to implement
            files: Optional list of files to include in context
            create_new: Whether Aider should create new files

        Returns:
            Dictionary with:
            - success: Whether operation succeeded
            - output: Aider's output
            - files_modified: List of modified files
            - error: Error message if failed
        """
        try:
            # Extract filenames from specification
            extracted_files = self._extract_filenames_from_spec(specification)

            if extracted_files:
                print(f"[AIDER] Extracted files from spec: {extracted_files}")
            else:
                print("[AIDER] No specific files found - generating default file structure")
                # Generate sensible default files based on spec content
                extracted_files = self._generate_default_files(specification)
                if extracted_files:
                    print(f"[AIDER] Suggested files: {extracted_files}")

            # Combine with any explicitly provided files
            all_files = list(set((files or []) + extracted_files))

            # Build the message for Aider (without filenames, they go as args)
            message = self._build_implementation_message(specification, create_new)

            # Run Aider with files as positional arguments
            result = self._run_aider(
                message=message,
                files=all_files,
                auto_yes=True
            )

            return {
                "success": result["returncode"] == 0,
                "output": result["stdout"],
                "files_modified": self._extract_modified_files(result["stdout"]),
                "error": result["stderr"] if result["returncode"] != 0 else None
            }

        except Exception as e:
            logger.error(f"Aider implementation failed: {e}")
            return {
                "success": False,
                "output": "",
                "files_modified": [],
                "error": str(e)
            }

    def _generate_default_files(self, specification: str) -> List[str]:
        """Generate sensible default file structure based on specification content."""
        import re

        files = []
        spec_lower = specification.lower()

        # Always include these base files
        files.append("src/main.py")
        files.append("src/config.py")
        files.append("README.md")

        # Add files based on keywords in specification
        if any(word in spec_lower for word in ['database', 'model', 'schema', 'table', 'db']):
            files.append("src/models/database.py")
            files.append("src/models/__init__.py")

        if any(word in spec_lower for word in ['api', 'endpoint', 'route', 'rest', 'http']):
            files.append("src/api/routes.py")
            files.append("src/api/__init__.py")

        if any(word in spec_lower for word in ['algorithm', 'pricing', 'calculation', 'compute']):
            files.append("src/services/algorithm.py")
            files.append("src/services/__init__.py")

        if any(word in spec_lower for word in ['auth', 'login', 'token', 'jwt', 'session']):
            files.append("src/auth/authentication.py")
            files.append("src/auth/__init__.py")

        if any(word in spec_lower for word in ['sync', 'integration', 'external', 'fetch']):
            files.append("src/services/sync.py")

        # Always add utility files
        files.append("src/utils/helpers.py")
        files.append("src/utils/__init__.py")
        files.append("src/constants.py")

        # Add requirements file
        files.append("requirements.txt")

        return files

    def _extract_filenames_from_spec(self, specification: str) -> List[str]:
        """Extract filenames from specification text."""
        import re

        filenames = []

        # Look for common patterns:
        # 1. Files in backticks: `filename.py` or `src/filename.py`
        # 2. Explicit mentions: "Create filename.py" or "in filename.py"
        # 3. Parenthetical filenames: (filename.py)

        # Pattern 1: Backtick-enclosed filenames
        backtick_pattern = r'`([a-zA-Z0-9_/\-\.]+\.(?:py|js|ts|tsx|jsx|java|cpp|c|h|go|rs|rb))`'
        matches = re.findall(backtick_pattern, specification)
        filenames.extend(matches)

        # Pattern 2: Parenthetical filenames
        paren_pattern = r'\(([a-zA-Z0-9_/\-\.]+\.(?:py|js|ts|tsx|jsx|java|cpp|c|h|go|rs|rb))\)'
        matches = re.findall(paren_pattern, specification)
        filenames.extend(matches)

        # Pattern 3: "Create X" or "in X" where X is a filename
        create_pattern = r'(?:Create|create|in|file:?)\s+([a-zA-Z0-9_/\-\.]+\.(?:py|js|ts|tsx|jsx|java|cpp|c|h|go|rs|rb))'
        matches = re.findall(create_pattern, specification)
        filenames.extend(matches)

        # Remove duplicates and clean up
        unique_files = list(set(filenames))

        # Clean up paths (remove any leading/trailing whitespace)
        cleaned_files = [f.strip() for f in unique_files]

        return cleaned_files

    def _build_implementation_message(
        self,
        specification: str,
        create_new: bool
    ) -> str:
        """Build the message to send to Aider."""
        # Aider works best with VERY concise, direct instructions
        # Strip out markdown formatting and extract just the core task

        import re

        # Extract functional requirements
        func_reqs = []
        for line in specification.split('\n'):
            # Look for functional requirements sections
            if 'FR' in line and (':' in line or 'Description' in line):
                # Clean up the line - remove markdown, numbering, etc.
                clean_line = re.sub(r'^#+\s*', '', line)  # Remove markdown headers
                clean_line = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_line)  # Remove bold
                clean_line = clean_line.strip()
                if clean_line:
                    func_reqs.append(clean_line)
            elif line.strip().startswith('- ') and 'ID:' not in line and 'Description:' not in line:
                # Include detail lines but clean them
                clean_line = line.strip().lstrip('- *')
                if clean_line and len(clean_line) > 10:
                    func_reqs.append(clean_line)

        # Build a simple, actionable message without markdown artifacts
        if func_reqs:
            # Use functional requirements
            core_spec = '\n'.join(func_reqs[:8])
        else:
            # Extract just text, no markdown
            clean_spec = re.sub(r'`[^`]+`', lambda m: m.group(0).strip('`'), specification)
            clean_spec = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_spec)
            clean_spec = re.sub(r'#+\s*', '', clean_spec)
            core_spec = clean_spec[:1000]

        # Build a clear, concise message for Aider
        message = f"""Implement the following:

{core_spec}

Requirements:
- Write complete, production-ready code
- Include error handling and docstrings
- Add type hints where appropriate
- NO placeholders or TODO comments"""

        return message.strip()

    def _run_aider(
        self,
        message: str,
        files: List[str],
        auto_yes: bool = True
    ) -> Dict[str, any]:
        """
        Run Aider command.

        Args:
            message: Message/prompt for Aider
            files: Files to add to context
            auto_yes: Auto-accept all changes

        Returns:
            Dictionary with returncode, stdout, stderr
        """
        # Build Aider command using Python 3.11 specifically
        # (Python 3.13 not compatible with Aider yet)
        cmd = ["python", "-m", "aider"]

        # Add model
        cmd.extend(["--model", self.model])

        # Use "whole" edit format (DeepSeek-Coder-V2 ONLY supports "whole" format)
        # This makes it return full modified files instead of diffs
        cmd.extend(["--edit-format", "whole"])

        # Suppress model warnings (Ollama models are unknown to Aider but work fine)
        cmd.append("--no-show-model-warnings")

        # Add auto-yes flag
        if auto_yes:
            cmd.append("--yes")

        # Add message
        cmd.extend(["--message", message])

        # Add files to context
        if files:
            cmd.extend(files)

        # Add no-git flag if not using git
        if not self.auto_commit:
            cmd.append("--no-git")

        logger.info(f"Running Aider: {' '.join(cmd)}")

        # Set environment variables
        import os
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'  # Force UTF-8 encoding
        env['NO_COLOR'] = '1'  # Disable colored output
        env['TERM'] = 'dumb'  # Use simple terminal mode

        # Run Aider directly (no batch file on Linux)
        try:
            result = subprocess.run(
                cmd,  # Pass command as list, not joined string
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                env=env
            )

            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except subprocess.TimeoutExpired:
            logger.error("Aider command timed out")
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out after 5 minutes"
            }
        except FileNotFoundError:
            logger.error("Aider not found. Install with: pip install aider-chat")
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "Aider not installed. Run: pip install aider-chat"
            }

    def _extract_modified_files(self, aider_output: str) -> List[str]:
        """Extract list of modified files from Aider output."""
        modified_files = []

        # Aider typically shows files like:
        # "Modified: src/app.py"
        # "Created: src/new_file.py"
        for line in aider_output.split('\n'):
            if 'Modified:' in line or 'Created:' in line or 'Added:' in line:
                # Extract filename
                parts = line.split(':', 1)
                if len(parts) == 2:
                    filename = parts[1].strip()
                    modified_files.append(filename)

        return modified_files

    def add_files_to_context(self, files: List[str]) -> bool:
        """
        Add files to Aider's context (for future operations).

        Args:
            files: List of file paths to add

        Returns:
            True if successful
        """
        # This would be used if maintaining a persistent Aider session
        # For now, we pass files to each command
        pass

    def check_aider_available(self) -> bool:
        """Check if Aider is installed and available."""
        try:
            result = subprocess.run(
                ["python", "-m", "aider", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False


def test_aider_tool():
    """Test the Aider tool."""
    import tempfile
    import os

    # Create a test project
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Test project: {tmpdir}")

        aider = AiderTool(project_path=tmpdir)

        # Check if Aider is available
        if not aider.check_aider_available():
            print("❌ Aider not installed!")
            print("Install with: pip install aider-chat")
            return False

        print("✅ Aider is available")

        # Test implementation
        result = aider.implement_feature(
            specification="Create a simple Python calculator with add, subtract, multiply, divide functions in calculator.py"
        )

        if result["success"]:
            print("✅ Aider ran successfully!")
            print(f"Modified files: {result['files_modified']}")

            # Check if file was created
            calc_file = Path(tmpdir) / "calculator.py"
            if calc_file.exists():
                print("✅ File was created!")
                print("\nFile content:")
                print(calc_file.read_text())
                return True
            else:
                print("❌ File was not created")
                return False
        else:
            print(f"❌ Aider failed: {result['error']}")
            return False


if __name__ == "__main__":
    # Run test
    test_aider_tool()
