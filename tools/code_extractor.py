"""
Code Extractor - Post-processor for Coder Agent Output
Extracts write_file() calls from agent output and executes them.
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
import ast


class CodeExtractor:
    """Extracts and executes write_file calls from agent output."""

    # Files that should never be overwritten
    PROTECTED_FILES = {
        'main.py',  # Orchestrator
        'agents/base_agent.py',
        'agents/__init__.py',
        'tools/__init__.py',
        'tools/code_extractor.py',
        'tools/simple_tools.py',
        'tools/mcp_tool_wrapper.py',
        'config/agents.yaml',
        'config/models.yaml',
        'config/settings.yaml',
        '.env',
        'requirements.txt'
    }

    def __init__(self):
        self.files_created = []
        self.files_modified = []
        self.errors = []

    def extract_and_execute(self, agent_output: str) -> Dict[str, any]:
        """
        Extract write_file calls from agent output and execute them.

        Args:
            agent_output: The text output from the Coder agent

        Returns:
            Dictionary with:
            - files_created: List of file paths created
            - files_modified: List of file paths modified
            - errors: List of error messages
            - summary: Summary of operations
        """
        # Try multiple extraction methods

        # Method 1: Direct write_file calls
        self._extract_write_file_calls(agent_output)

        # Method 2: Code blocks with file path comments
        self._extract_code_blocks_with_paths(agent_output)

        # Method 3: Sections with file headers
        self._extract_file_sections(agent_output)

        return {
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "errors": self.errors,
            "summary": self._generate_summary()
        }

    def _extract_write_file_calls(self, output: str):
        """Extract explicit write_file() function calls."""
        patterns = [
            # Pattern 1: write_file(file_path="...", content="""...""")
            r'write_file\s*\(\s*file_path\s*=\s*["\']([^"\']+)["\']\s*,\s*content\s*=\s*"""(.*?)"""\s*\)',
            # Pattern 2: write_file(file_path="...", content="...")
            r'write_file\s*\(\s*file_path\s*=\s*["\']([^"\']+)["\']\s*,\s*content\s*=\s*["\'](.+?)["\']\s*\)',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, output, re.DOTALL)
            for match in matches:
                file_path = match.group(1).strip()
                content = match.group(2).strip()
                content = self._clean_content(content)
                self._write_file(file_path, content)

    def _extract_code_blocks_with_paths(self, output: str):
        """Extract code from markdown blocks with file path comments."""
        # Pattern: ```python\n# path/to/file.py\ncode...```
        pattern = r'```python\s*\n\s*#\s*([^\n]+\.py)\s*\n(.*?)```'

        matches = re.finditer(pattern, output, re.DOTALL)
        for match in matches:
            file_path = match.group(1).strip()
            content = match.group(2).strip()
            self._write_file(file_path, content)

    def _extract_file_sections(self, output: str):
        """Extract files from section headers like '#### Module Name (path.py)'."""
        # Look for patterns like:
        # #### Main Module (`calculator_main.py`)
        # or
        # #### Operations Module (`operations.py`)
        # followed by code block

        lines = output.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check for section header with filename
            if line.strip().startswith('####') or line.strip().startswith('###'):
                # Try to extract filename from backticks or parentheses
                filename_match = re.search(r'[`\(]([^`\)]+\.py)[`\)]', line)

                if filename_match:
                    filename = filename_match.group(1)

                    # Look for code block following this header
                    j = i + 1
                    while j < len(lines) and not lines[j].strip().startswith('```'):
                        j += 1

                    if j < len(lines) and lines[j].strip().startswith('```'):
                        # Found code block start
                        code_start = j + 1
                        code_end = code_start

                        # Find code block end
                        while code_end < len(lines) and not lines[code_end].strip() == '```':
                            code_end += 1

                        if code_end < len(lines):
                            # Extract code
                            content = '\n'.join(lines[code_start:code_end])
                            self._write_file(filename, content)

                        i = code_end
                    else:
                        i += 1
                else:
                    i += 1
            else:
                i += 1

    def _clean_content(self, content: str) -> str:
        """Clean up extracted content."""
        # Remove leading/trailing whitespace
        content = content.strip()

        # Handle escaped quotes
        content = content.replace(r'\"', '"')
        content = content.replace(r"\'", "'")

        # Remove markdown code fence if present
        if content.startswith('```'):
            lines = content.split('\n')
            # Remove first line (```python or similar)
            if lines[0].startswith('```'):
                lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            content = '\n'.join(lines)

        return content

    def _write_file(self, file_path: str, content: str) -> bool:
        """
        Write content to a file.

        Args:
            file_path: Path to the file
            content: Content to write

        Returns:
            True if successful, False otherwise
        """
        try:
            # Normalize path for comparison
            normalized_path = file_path.replace('\\', '/')

            # Check if file is protected
            if normalized_path in self.PROTECTED_FILES or any(normalized_path.endswith(pf) for pf in self.PROTECTED_FILES):
                error_msg = f"Skipping protected file: {file_path}"
                self.errors.append(error_msg)
                return False

            path = Path(file_path)

            # Check if file exists
            file_existed = path.exists()

            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write the file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Track the operation
            if file_existed:
                self.files_modified.append(str(path))
            else:
                self.files_created.append(str(path))

            return True

        except Exception as e:
            error_msg = f"Error writing {file_path}: {str(e)}"
            self.errors.append(error_msg)
            return False

    def _generate_summary(self) -> str:
        """Generate a summary of operations."""
        summary_parts = []

        if self.files_created:
            summary_parts.append(f"Created {len(self.files_created)} file(s):")
            for f in self.files_created:
                summary_parts.append(f"  - {f}")

        if self.files_modified:
            summary_parts.append(f"\nModified {len(self.files_modified)} file(s):")
            for f in self.files_modified:
                summary_parts.append(f"  - {f}")

        if self.errors:
            summary_parts.append(f"\nEncountered {len(self.errors)} error(s):")
            for e in self.errors:
                summary_parts.append(f"  - {e}")

        if not self.files_created and not self.files_modified:
            summary_parts.append("No files were created or modified.")

        return "\n".join(summary_parts)

    def extract_code_blocks(self, agent_output: str) -> List[Tuple[str, str]]:
        """
        Extract code blocks from markdown in agent output.

        Args:
            agent_output: The text output from agent

        Returns:
            List of tuples (filename, code_content)
        """
        code_blocks = []

        # Pattern for markdown code blocks with file path comments
        pattern = r'```(?:python)?\s*(?:#\s*)?([^\n]+\.py)?\s*\n(.*?)```'

        matches = re.finditer(pattern, agent_output, re.DOTALL)

        for match in matches:
            filename = match.group(1)
            code = match.group(2).strip()

            if filename:
                filename = filename.strip().lstrip('#').strip()
                code_blocks.append((filename, code))

        return code_blocks

    def extract_from_inline_comments(self, agent_output: str) -> List[Tuple[str, str]]:
        """
        Extract file paths and content from inline comments.

        Looks for patterns like:
        # src/file.py
        code here...

        Args:
            agent_output: The text output

        Returns:
            List of tuples (filename, code_content)
        """
        results = []
        lines = agent_output.split('\n')

        current_file = None
        current_content = []

        for line in lines:
            # Check if line is a file path comment
            if line.strip().startswith('#') and '.py' in line:
                # Save previous file if any
                if current_file and current_content:
                    results.append((current_file, '\n'.join(current_content)))

                # Start new file
                current_file = line.strip().lstrip('#').strip()
                current_content = []
            elif current_file and line.strip():
                current_content.append(line)

        # Save last file
        if current_file and current_content:
            results.append((current_file, '\n'.join(current_content)))

        return results


def process_coder_output(output: str) -> Dict[str, any]:
    """
    Main function to process coder agent output.

    Args:
        output: The raw output from the Coder agent

    Returns:
        Dictionary with extraction results
    """
    extractor = CodeExtractor()
    return extractor.extract_and_execute(output)
