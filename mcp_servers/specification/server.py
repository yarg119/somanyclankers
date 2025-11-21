"""
MCP Server for Specification Management
Provides tools for creating, refining, and validating software specifications
using GitHub's spec-kit framework.
"""

import asyncio
import json
import os
import subprocess
from typing import Any, Dict, List, Optional
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class SpecificationServer:
    """MCP Server for specification management using spec-kit."""

    def __init__(self, specs_dir: str = "specifications"):
        self.specs_dir = Path(specs_dir)
        self.specs_dir.mkdir(exist_ok=True)
        self.server = Server("specification-server")
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP tool handlers."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available specification tools."""
            return [
                Tool(
                    name="create_specification",
                    description="Create a new software specification from a user requirement",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the specification"
                            },
                            "description": {
                                "type": "string",
                                "description": "Initial description of the feature or requirement"
                            },
                            "spec_name": {
                                "type": "string",
                                "description": "Name for the spec file (without extension)"
                            }
                        },
                        "required": ["title", "description", "spec_name"]
                    }
                ),
                Tool(
                    name="refine_specification",
                    description="Refine an existing specification by asking clarifying questions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "spec_name": {
                                "type": "string",
                                "description": "Name of the spec file to refine"
                            },
                            "questions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of clarifying questions to ask"
                            }
                        },
                        "required": ["spec_name", "questions"]
                    }
                ),
                Tool(
                    name="validate_specification",
                    description="Validate a specification for completeness and clarity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "spec_name": {
                                "type": "string",
                                "description": "Name of the spec file to validate"
                            }
                        },
                        "required": ["spec_name"]
                    }
                ),
                Tool(
                    name="list_specifications",
                    description="List all available specifications",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_specification",
                    description="Get the content of a specific specification",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "spec_name": {
                                "type": "string",
                                "description": "Name of the spec file to retrieve"
                            }
                        },
                        "required": ["spec_name"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""

            if name == "create_specification":
                return await self._create_specification(
                    arguments["title"],
                    arguments["description"],
                    arguments["spec_name"]
                )

            elif name == "refine_specification":
                return await self._refine_specification(
                    arguments["spec_name"],
                    arguments["questions"]
                )

            elif name == "validate_specification":
                return await self._validate_specification(
                    arguments["spec_name"]
                )

            elif name == "list_specifications":
                return await self._list_specifications()

            elif name == "get_specification":
                return await self._get_specification(
                    arguments["spec_name"]
                )

            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]

    async def _create_specification(
        self,
        title: str,
        description: str,
        spec_name: str
    ) -> List[TextContent]:
        """Create a new specification."""
        try:
            spec_path = self.specs_dir / f"{spec_name}.md"

            # Create specification using template
            spec_content = f"""# {title}

## Overview
{description}

## Requirements

### Functional Requirements
- [ ] TODO: Define functional requirements

### Non-Functional Requirements
- [ ] TODO: Define non-functional requirements (performance, scalability, security)

## Architecture

### Components
TODO: Define system components

### Data Flow
TODO: Describe data flow

## Implementation Plan

### Phase 1: Foundation
- [ ] TODO: Define foundation tasks

### Phase 2: Core Features
- [ ] TODO: Define core feature tasks

### Phase 3: Testing & Deployment
- [ ] TODO: Define testing and deployment tasks

## Acceptance Criteria
- [ ] TODO: Define acceptance criteria

## Open Questions
TODO: List any open questions or clarifications needed

## Dependencies
TODO: List dependencies

## Risks & Mitigations
TODO: Identify risks and mitigation strategies

## Timeline
TODO: Estimated timeline

---
*Created with Automated Coding Agent Network*
"""

            # Write specification file
            spec_path.write_text(spec_content, encoding='utf-8')

            return [TextContent(
                type="text",
                text=f"Successfully created specification: {spec_path}\n\nNext steps:\n1. Review and fill in the TODO sections\n2. Use refine_specification to add clarifying questions\n3. Use validate_specification to check completeness"
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error creating specification: {str(e)}"
            )]

    async def _refine_specification(
        self,
        spec_name: str,
        questions: List[str]
    ) -> List[TextContent]:
        """Refine a specification with clarifying questions."""
        try:
            spec_path = self.specs_dir / f"{spec_name}.md"

            if not spec_path.exists():
                return [TextContent(
                    type="text",
                    text=f"Specification not found: {spec_name}"
                )]

            # Read existing content
            content = spec_path.read_text(encoding='utf-8')

            # Add questions to Open Questions section
            questions_section = "\n## Open Questions\n"
            for i, question in enumerate(questions, 1):
                questions_section += f"{i}. {question}\n"

            # Replace or append Open Questions section
            if "## Open Questions" in content:
                parts = content.split("## Open Questions")
                # Find the next section
                next_section = None
                for line in parts[1].split('\n'):
                    if line.startswith('##'):
                        next_section = line
                        break

                if next_section:
                    content = parts[0] + questions_section + "\n" + next_section + "\n" + parts[1].split(next_section, 1)[1]
                else:
                    content = parts[0] + questions_section
            else:
                content += "\n" + questions_section

            spec_path.write_text(content, encoding='utf-8')

            return [TextContent(
                type="text",
                text=f"Successfully refined specification: {spec_path}\nAdded {len(questions)} clarifying questions"
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error refining specification: {str(e)}"
            )]

    async def _validate_specification(
        self,
        spec_name: str
    ) -> List[TextContent]:
        """Validate a specification for completeness."""
        try:
            spec_path = self.specs_dir / f"{spec_name}.md"

            if not spec_path.exists():
                return [TextContent(
                    type="text",
                    text=f"Specification not found: {spec_name}"
                )]

            content = spec_path.read_text(encoding='utf-8')

            # Check for required sections
            required_sections = [
                "Overview",
                "Requirements",
                "Architecture",
                "Implementation Plan",
                "Acceptance Criteria"
            ]

            missing_sections = []
            todo_count = content.count("TODO:")

            for section in required_sections:
                if f"## {section}" not in content:
                    missing_sections.append(section)

            # Generate validation report
            report = f"Validation Report for {spec_name}:\n\n"

            if missing_sections:
                report += f"❌ Missing sections: {', '.join(missing_sections)}\n"
            else:
                report += "✓ All required sections present\n"

            if todo_count > 0:
                report += f"⚠️  {todo_count} TODO items remaining\n"
            else:
                report += "✓ No TODO items\n"

            # Check for open questions
            if "## Open Questions" in content:
                questions_section = content.split("## Open Questions")[1].split("##")[0]
                question_lines = [line for line in questions_section.split('\n') if line.strip().startswith(tuple('123456789'))]
                if question_lines:
                    report += f"⚠️  {len(question_lines)} open questions need answers\n"

            if not missing_sections and todo_count == 0:
                report += "\n✓ Specification is complete and ready for implementation"
            else:
                report += "\n⚠️  Specification needs more work before implementation"

            return [TextContent(
                type="text",
                text=report
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error validating specification: {str(e)}"
            )]

    async def _list_specifications(self) -> List[TextContent]:
        """List all specifications."""
        try:
            spec_files = list(self.specs_dir.glob("*.md"))

            if not spec_files:
                return [TextContent(
                    type="text",
                    text="No specifications found"
                )]

            spec_list = "Available Specifications:\n\n"
            for spec_file in spec_files:
                # Read first line (title)
                first_line = spec_file.read_text(encoding='utf-8').split('\n')[0]
                title = first_line.replace('#', '').strip()
                spec_list += f"- {spec_file.stem}: {title}\n"

            return [TextContent(
                type="text",
                text=spec_list
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error listing specifications: {str(e)}"
            )]

    async def _get_specification(
        self,
        spec_name: str
    ) -> List[TextContent]:
        """Get the content of a specification."""
        try:
            spec_path = self.specs_dir / f"{spec_name}.md"

            if not spec_path.exists():
                return [TextContent(
                    type="text",
                    text=f"Specification not found: {spec_name}"
                )]

            content = spec_path.read_text(encoding='utf-8')

            return [TextContent(
                type="text",
                text=f"Specification: {spec_name}\n\n{content}"
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting specification: {str(e)}"
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
    server = SpecificationServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
