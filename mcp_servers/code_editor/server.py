"""
MCP Server for Code Editing
Provides tools for reading, writing, and modifying code files.
"""

import asyncio
import os
import re
from typing import Any, Dict, List, Optional
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class CodeEditorServer:
    """MCP Server for code editing operations."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.server = Server("code-editor-server")
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP tool handlers."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available code editing tools."""
            return [
                Tool(
                    name="read_file",
                    description="Read the contents of a file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to read (relative to project root)"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="write_file",
                    description="Write content to a file (creates or overwrites)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to write"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write to the file"
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                ),
                Tool(
                    name="edit_file",
                    description="Edit specific lines in a file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to edit"
                            },
                            "old_text": {
                                "type": "string",
                                "description": "Text to find and replace"
                            },
                            "new_text": {
                                "type": "string",
                                "description": "New text to insert"
                            }
                        },
                        "required": ["file_path", "old_text", "new_text"]
                    }
                ),
                Tool(
                    name="search_code",
                    description="Search for code patterns in the project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "description": "Search pattern (regex supported)"
                            },
                            "file_pattern": {
                                "type": "string",
                                "description": "File pattern to search in (e.g., '*.py')",
                                "default": "*"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 50
                            }
                        },
                        "required": ["pattern"]
                    }
                ),
                Tool(
                    name="list_files",
                    description="List files in a directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directory to list (relative to project root)",
                                "default": "."
                            },
                            "pattern": {
                                "type": "string",
                                "description": "File pattern to match (e.g., '*.py')",
                                "default": "*"
                            }
                        }
                    }
                ),
                Tool(
                    name="create_directory",
                    description="Create a new directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "Path to the directory to create"
                            }
                        },
                        "required": ["directory_path"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""

            if name == "read_file":
                return await self._read_file(arguments["file_path"])

            elif name == "write_file":
                return await self._write_file(
                    arguments["file_path"],
                    arguments["content"]
                )

            elif name == "edit_file":
                return await self._edit_file(
                    arguments["file_path"],
                    arguments["old_text"],
                    arguments["new_text"]
                )

            elif name == "search_code":
                return await self._search_code(
                    arguments["pattern"],
                    arguments.get("file_pattern", "*"),
                    arguments.get("max_results", 50)
                )

            elif name == "list_files":
                return await self._list_files(
                    arguments.get("directory", "."),
                    arguments.get("pattern", "*")
                )

            elif name == "create_directory":
                return await self._create_directory(
                    arguments["directory_path"]
                )

            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]

    def _get_full_path(self, relative_path: str) -> Path:
        """Convert relative path to full path within project root."""
        full_path = (self.project_root / relative_path).resolve()

        # Security check: ensure path is within project root
        if not str(full_path).startswith(str(self.project_root)):
            raise ValueError(f"Path {relative_path} is outside project root")

        return full_path

    async def _read_file(self, file_path: str) -> List[TextContent]:
        """Read a file's contents."""
        try:
            full_path = self._get_full_path(file_path)

            if not full_path.exists():
                return [TextContent(
                    type="text",
                    text=f"File not found: {file_path}"
                )]

            content = full_path.read_text(encoding='utf-8')

            return [TextContent(
                type="text",
                text=f"File: {file_path}\n\n{content}"
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error reading file: {str(e)}"
            )]

    async def _write_file(
        self,
        file_path: str,
        content: str
    ) -> List[TextContent]:
        """Write content to a file."""
        try:
            full_path = self._get_full_path(file_path)

            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            full_path.write_text(content, encoding='utf-8')

            return [TextContent(
                type="text",
                text=f"Successfully wrote to {file_path} ({len(content)} characters)"
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error writing file: {str(e)}"
            )]

    async def _edit_file(
        self,
        file_path: str,
        old_text: str,
        new_text: str
    ) -> List[TextContent]:
        """Edit a file by replacing old text with new text."""
        try:
            full_path = self._get_full_path(file_path)

            if not full_path.exists():
                return [TextContent(
                    type="text",
                    text=f"File not found: {file_path}"
                )]

            # Read current content
            content = full_path.read_text(encoding='utf-8')

            # Check if old text exists
            if old_text not in content:
                return [TextContent(
                    type="text",
                    text=f"Could not find the specified text in {file_path}"
                )]

            # Replace text
            new_content = content.replace(old_text, new_text)

            # Write back
            full_path.write_text(new_content, encoding='utf-8')

            return [TextContent(
                type="text",
                text=f"Successfully edited {file_path}"
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error editing file: {str(e)}"
            )]

    async def _search_code(
        self,
        pattern: str,
        file_pattern: str,
        max_results: int
    ) -> List[TextContent]:
        """Search for code patterns in the project."""
        try:
            results = []
            count = 0

            # Compile regex pattern
            regex = re.compile(pattern, re.IGNORECASE)

            # Search files
            for file_path in self.project_root.rglob(file_pattern):
                if not file_path.is_file():
                    continue

                # Skip hidden directories and common non-source directories
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                if any(part in ['node_modules', '__pycache__', 'venv', 'env'] for part in file_path.parts):
                    continue

                try:
                    content = file_path.read_text(encoding='utf-8')

                    # Find matches
                    for line_num, line in enumerate(content.split('\n'), 1):
                        if regex.search(line):
                            relative_path = file_path.relative_to(self.project_root)
                            results.append(f"{relative_path}:{line_num}: {line.strip()}")
                            count += 1

                            if count >= max_results:
                                break

                except Exception:
                    # Skip files that can't be read
                    continue

                if count >= max_results:
                    break

            if not results:
                return [TextContent(
                    type="text",
                    text=f"No matches found for pattern: {pattern}"
                )]

            result_text = f"Found {count} matches for '{pattern}':\n\n" + "\n".join(results)

            if count >= max_results:
                result_text += f"\n\n(Limited to {max_results} results)"

            return [TextContent(
                type="text",
                text=result_text
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error searching code: {str(e)}"
            )]

    async def _list_files(
        self,
        directory: str,
        pattern: str
    ) -> List[TextContent]:
        """List files in a directory."""
        try:
            full_path = self._get_full_path(directory)

            if not full_path.exists():
                return [TextContent(
                    type="text",
                    text=f"Directory not found: {directory}"
                )]

            if not full_path.is_dir():
                return [TextContent(
                    type="text",
                    text=f"Not a directory: {directory}"
                )]

            # List files matching pattern
            files = []
            for file_path in full_path.glob(pattern):
                relative_path = file_path.relative_to(self.project_root)
                file_type = "dir" if file_path.is_dir() else "file"
                files.append(f"[{file_type}] {relative_path}")

            if not files:
                return [TextContent(
                    type="text",
                    text=f"No files found in {directory} matching pattern {pattern}"
                )]

            result_text = f"Files in {directory}:\n\n" + "\n".join(sorted(files))

            return [TextContent(
                type="text",
                text=result_text
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error listing files: {str(e)}"
            )]

    async def _create_directory(
        self,
        directory_path: str
    ) -> List[TextContent]:
        """Create a new directory."""
        try:
            full_path = self._get_full_path(directory_path)

            full_path.mkdir(parents=True, exist_ok=True)

            return [TextContent(
                type="text",
                text=f"Successfully created directory: {directory_path}"
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error creating directory: {str(e)}"
            )]

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point."""
    server = CodeEditorServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
