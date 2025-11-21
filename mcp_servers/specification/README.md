# Specification MCP Server

An MCP server for managing software specifications using GitHub's spec-kit framework.

## Overview

This server provides tools for creating, refining, validating, and managing software specifications as part of the automated coding agent network.

## Available Tools

### 1. create_specification

Create a new software specification from a user requirement.

**Parameters:**
- `title` (string): Title of the specification
- `description` (string): Initial description of the feature or requirement
- `spec_name` (string): Name for the spec file (without extension)

**Example:**
```json
{
  "title": "User Authentication System",
  "description": "Implement JWT-based authentication with refresh tokens",
  "spec_name": "auth_system"
}
```

### 2. refine_specification

Refine an existing specification by adding clarifying questions.

**Parameters:**
- `spec_name` (string): Name of the spec file to refine
- `questions` (array): List of clarifying questions

**Example:**
```json
{
  "spec_name": "auth_system",
  "questions": [
    "What is the desired token expiration time?",
    "Should we support OAuth providers?",
    "What password complexity requirements are needed?"
  ]
}
```

### 3. validate_specification

Validate a specification for completeness and clarity.

**Parameters:**
- `spec_name` (string): Name of the spec file to validate

**Example:**
```json
{
  "spec_name": "auth_system"
}
```

### 4. list_specifications

List all available specifications.

**Parameters:** None

### 5. get_specification

Get the full content of a specific specification.

**Parameters:**
- `spec_name` (string): Name of the spec file to retrieve

**Example:**
```json
{
  "spec_name": "auth_system"
}
```

## Running the Server

### Standalone Mode

```bash
python mcp_servers/specification/server.py
```

### Via MCP Client

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "specification": {
      "command": "python",
      "args": ["mcp_servers/specification/server.py"]
    }
  }
}
```

## Specification Template

Each specification includes:

- **Overview**: High-level description
- **Requirements**: Functional and non-functional requirements
- **Architecture**: System components and data flow
- **Implementation Plan**: Phased approach to implementation
- **Acceptance Criteria**: Success metrics
- **Open Questions**: Clarifications needed
- **Dependencies**: External dependencies
- **Risks & Mitigations**: Risk assessment
- **Timeline**: Estimated timeline

## Integration with Agents

The ProjectManager agent uses this server to:
1. Create initial specifications from user requirements
2. Refine specifications by asking clarifying questions
3. Validate specifications before implementation
4. Provide specifications to other agents (Architect, Coder)

## File Storage

Specifications are stored in the `specifications/` directory as Markdown files.

## Development

### Adding New Tools

1. Add tool definition in `_register_handlers()`
2. Implement tool handler method
3. Update this README

### Testing

```bash
# Test specification creation
python -c "
import asyncio
from mcp_servers.specification.server import SpecificationServer

async def test():
    server = SpecificationServer()
    result = await server._create_specification(
        'Test Feature',
        'A test feature for validation',
        'test_feature'
    )
    print(result[0].text)

asyncio.run(test())
"
```
