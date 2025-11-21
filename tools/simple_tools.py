"""
Simple Direct Tools for CrewAI Agents
Direct file and specification operations without MCP server overhead.
"""

from typing import Any, Optional
from crewai.tools.base_tool import BaseTool
from pydantic import Field
import os
from pathlib import Path
import json


class WriteFileTool(BaseTool):
    """Tool for writing content to files."""

    name: str = "write_file"
    description: str = (
        "Write content to a file. "
        "Parameters: file_path (str), content (str). "
        "Creates parent directories if they don't exist."
    )
    base_directory: Optional[str] = None

    def _run(self, file_path: str, content: str) -> str:
        """Write content to a file."""
        try:
            # If base_directory is set, resolve path relative to it
            if self.base_directory:
                base_path = Path(self.base_directory)
                # If file_path is absolute, use it as-is; otherwise, make it relative to base
                path = Path(file_path)
                if not path.is_absolute():
                    path = base_path / file_path
            else:
                path = Path(file_path)

            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"Successfully wrote {len(content)} characters to {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"


class ReadFileTool(BaseTool):
    """Tool for reading file contents."""

    name: str = "read_file"
    description: str = (
        "Read the contents of a file. "
        "Parameters: file_path (str). "
        "Returns the file content as a string."
    )
    base_directory: Optional[str] = None

    def _run(self, file_path: str) -> str:
        """Read content from a file."""
        try:
            # If base_directory is set, resolve path relative to it
            if self.base_directory:
                base_path = Path(self.base_directory)
                path = Path(file_path)
                if not path.is_absolute():
                    path = base_path / file_path
            else:
                path = Path(file_path)

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except FileNotFoundError:
            return f"Error: File not found: {path if self.base_directory else file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"


class ListDirectoryTool(BaseTool):
    """Tool for listing directory contents."""

    name: str = "list_directory"
    description: str = (
        "List files and directories in a given path. "
        "Parameters: directory_path (str). "
        "Returns a list of files and directories."
    )

    def _run(self, directory_path: str) -> str:
        """List directory contents."""
        try:
            path = Path(directory_path)
            if not path.exists():
                return f"Error: Directory not found: {directory_path}"

            items = []
            for item in path.iterdir():
                item_type = "dir" if item.is_dir() else "file"
                items.append(f"{item_type}: {item.name}")

            return "\n".join(items) if items else "Directory is empty"
        except Exception as e:
            return f"Error listing directory: {str(e)}"


class CreateDirectoryTool(BaseTool):
    """Tool for creating directories."""

    name: str = "create_directory"
    description: str = (
        "Create a new directory (including parent directories). "
        "Parameters: directory_path (str). "
        "Creates all parent directories if they don't exist."
    )

    def _run(self, directory_path: str) -> str:
        """Create a directory."""
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return f"Successfully created directory: {directory_path}"
        except Exception as e:
            return f"Error creating directory: {str(e)}"


class CreateSpecificationTool(BaseTool):
    """Tool for creating specification documents."""

    name: str = "create_specification"
    description: str = (
        "Create a new specification document. "
        "Parameters: title (str) - the specification title, "
        "content (str) - the full markdown content. "
        "Filename will be auto-generated from title. "
        "Saves to specifications/ directory."
    )
    base_directory: Optional[str] = None

    def _run(self, title: str, content: str) -> str:
        """Create a specification document."""
        try:
            # Generate filename from title
            filename = title.lower().replace(" ", "_") + ".md"

            # Ensure filename has .md extension
            if not filename.endswith('.md'):
                filename += '.md'

            # Create specifications directory
            if self.base_directory:
                spec_dir = Path(self.base_directory) / "specifications"
            else:
                spec_dir = Path("specifications")

            spec_dir.mkdir(exist_ok=True, parents=True)

            # Write specification file
            spec_path = spec_dir / filename

            # Format the specification with title
            full_content = f"# {title}\n\n{content}"

            with open(spec_path, 'w', encoding='utf-8') as f:
                f.write(full_content)

            return f"Successfully created specification: {spec_path}"
        except Exception as e:
            return f"Error creating specification: {str(e)}"


class ReadSpecificationTool(BaseTool):
    """Tool for reading specification documents."""

    name: str = "read_specification"
    description: str = (
        "Read an existing specification document. "
        "Parameters: filename (str). "
        "Reads from specifications/ directory."
    )
    base_directory: Optional[str] = None

    def _run(self, filename: str) -> str:
        """Read a specification document."""
        try:
            # Ensure filename has .md extension
            if not filename.endswith('.md'):
                filename += '.md'

            # Determine spec directory path
            if self.base_directory:
                spec_path = Path(self.base_directory) / "specifications" / filename
            else:
                spec_path = Path("specifications") / filename

            if not spec_path.exists():
                return f"Error: Specification not found: {filename}"

            with open(spec_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return content
        except Exception as e:
            return f"Error reading specification: {str(e)}"


def get_simple_tools_for_agent(tool_categories: list[str], base_directory: Optional[str] = None) -> list[BaseTool]:
    """
    Get tools for an agent based on tool categories.

    Args:
        tool_categories: List of tool category names
        base_directory: Optional base directory for all file operations

    Returns:
        List of BaseTool instances
    """
    tools = []

    for category in tool_categories:
        if category == "code_editor":
            tools.extend([
                WriteFileTool(base_directory=base_directory),
                ReadFileTool(base_directory=base_directory),
                ListDirectoryTool(),
            ])
        elif category == "specification":
            tools.extend([
                CreateSpecificationTool(base_directory=base_directory),
                ReadSpecificationTool(base_directory=base_directory),
            ])
        elif category == "filesystem":
            tools.extend([
                WriteFileTool(base_directory=base_directory),
                ReadFileTool(base_directory=base_directory),
                ListDirectoryTool(),
                CreateDirectoryTool(),
            ])

    return tools
