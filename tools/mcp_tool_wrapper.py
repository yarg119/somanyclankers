"""
MCP Tool Wrapper for CrewAI
Bridges Model Context Protocol tools with CrewAI's tool system.
"""

from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field
from crewai_tools import BaseTool
import subprocess
import json
import os


class MCPToolWrapper(BaseTool):
    """
    Wrapper that makes MCP tools compatible with CrewAI.

    This wrapper communicates with MCP servers via stdio and
    exposes their tools to CrewAI agents.
    """

    name: str = Field(...)
    description: str = Field(...)
    mcp_server_command: List[str] = Field(...)
    mcp_tool_name: str = Field(...)

    def _run(self, **kwargs: Any) -> str:
        """
        Execute the MCP tool.

        Args:
            **kwargs: Tool parameters

        Returns:
            Tool execution result as string
        """
        try:
            # Prepare the MCP request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": self.mcp_tool_name,
                    "arguments": kwargs
                }
            }

            # Start the MCP server process
            process = subprocess.Popen(
                self.mcp_server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Send the request
            stdout, stderr = process.communicate(
                input=json.dumps(request) + "\n",
                timeout=30
            )

            # Parse the response
            if stderr:
                return f"Error: {stderr}"

            response = json.loads(stdout)

            if "error" in response:
                return f"Tool error: {response['error']}"

            if "result" in response:
                return str(response["result"])

            return str(response)

        except subprocess.TimeoutExpired:
            return "Error: MCP tool execution timed out"
        except json.JSONDecodeError as e:
            return f"Error: Failed to parse MCP response: {e}"
        except Exception as e:
            return f"Error: {str(e)}"


class FileSystemTools:
    """Collection of filesystem MCP tools wrapped for CrewAI."""

    @staticmethod
    def get_read_file_tool() -> MCPToolWrapper:
        """Get tool for reading files."""
        return MCPToolWrapper(
            name="read_file",
            description="Read the contents of a file from the filesystem",
            mcp_server_command=["python", "-m", "mcp_servers.filesystem.server"],
            mcp_tool_name="read_file"
        )

    @staticmethod
    def get_write_file_tool() -> MCPToolWrapper:
        """Get tool for writing files."""
        return MCPToolWrapper(
            name="write_file",
            description="Write content to a file in the filesystem",
            mcp_server_command=["python", "-m", "mcp_servers.filesystem.server"],
            mcp_tool_name="write_file"
        )

    @staticmethod
    def get_list_directory_tool() -> MCPToolWrapper:
        """Get tool for listing directory contents."""
        return MCPToolWrapper(
            name="list_directory",
            description="List the contents of a directory",
            mcp_server_command=["python", "-m", "mcp_servers.filesystem.server"],
            mcp_tool_name="list_directory"
        )

    @staticmethod
    def get_create_directory_tool() -> MCPToolWrapper:
        """Get tool for creating directories."""
        return MCPToolWrapper(
            name="create_directory",
            description="Create a new directory",
            mcp_server_command=["python", "-m", "mcp_servers.filesystem.server"],
            mcp_tool_name="create_directory"
        )


class SpecificationTools:
    """Collection of specification management MCP tools wrapped for CrewAI."""

    @staticmethod
    def get_create_spec_tool() -> MCPToolWrapper:
        """Get tool for creating specifications."""
        return MCPToolWrapper(
            name="create_specification",
            description="Create a new specification document",
            mcp_server_command=["python", "-m", "mcp_servers.specification.server"],
            mcp_tool_name="create_specification"
        )

    @staticmethod
    def get_read_spec_tool() -> MCPToolWrapper:
        """Get tool for reading specifications."""
        return MCPToolWrapper(
            name="read_specification",
            description="Read an existing specification document",
            mcp_server_command=["python", "-m", "mcp_servers.specification.server"],
            mcp_tool_name="read_specification"
        )

    @staticmethod
    def get_update_spec_tool() -> MCPToolWrapper:
        """Get tool for updating specifications."""
        return MCPToolWrapper(
            name="update_specification",
            description="Update an existing specification document",
            mcp_server_command=["python", "-m", "mcp_servers.specification.server"],
            mcp_tool_name="update_specification"
        )


class CodeEditorTools:
    """Collection of code editing MCP tools wrapped for CrewAI."""

    @staticmethod
    def get_edit_code_tool() -> MCPToolWrapper:
        """Get tool for editing code files."""
        return MCPToolWrapper(
            name="edit_code",
            description="Make targeted edits to code files",
            mcp_server_command=["python", "-m", "mcp_servers.code_editor.server"],
            mcp_tool_name="edit_code"
        )

    @staticmethod
    def get_search_code_tool() -> MCPToolWrapper:
        """Get tool for searching code."""
        return MCPToolWrapper(
            name="search_code",
            description="Search for code patterns in the codebase",
            mcp_server_command=["python", "-m", "mcp_servers.code_editor.server"],
            mcp_tool_name="search_code"
        )


def get_tools_for_agent(tool_names: List[str]) -> List[BaseTool]:
    """
    Get MCP tools for an agent based on tool names.

    Args:
        tool_names: List of tool category names (e.g., ['code_editor', 'specification'])

    Returns:
        List of CrewAI-compatible tools
    """
    tools = []

    for tool_name in tool_names:
        if tool_name == "code_editor":
            tools.extend([
                FileSystemTools.get_read_file_tool(),
                FileSystemTools.get_write_file_tool(),
                FileSystemTools.get_list_directory_tool(),
                CodeEditorTools.get_edit_code_tool(),
                CodeEditorTools.get_search_code_tool()
            ])
        elif tool_name == "specification":
            tools.extend([
                SpecificationTools.get_create_spec_tool(),
                SpecificationTools.get_read_spec_tool(),
                SpecificationTools.get_update_spec_tool()
            ])
        elif tool_name == "filesystem":
            tools.extend([
                FileSystemTools.get_read_file_tool(),
                FileSystemTools.get_write_file_tool(),
                FileSystemTools.get_list_directory_tool(),
                FileSystemTools.get_create_directory_tool()
            ])

    return tools
