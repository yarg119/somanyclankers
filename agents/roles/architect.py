"""
Architect Agent
Responsible for system architecture and technical design decisions.
"""

from typing import Any, Dict, List, Optional
import asyncio

from ..base_agent import BaseAgent, AgentConfig


class ArchitectAgent(BaseAgent):
    """
    Architect agent specializes in:
    - Designing system architecture
    - Making high-level technical decisions
    - Creating technical specifications
    - Defining component interactions
    - Selecting appropriate technologies
    """

    def __init__(self, config: AgentConfig):
        """Initialize Architect agent."""
        # Set default configuration for Architect if not provided
        if not config.role:
            config.role = "System Architecture and Technical Design Expert"

        if not config.goal:
            config.goal = (
                "Design robust, scalable system architectures that meet requirements. "
                "Make informed technical decisions about frameworks, patterns, and "
                "component interactions. Create clear technical specifications."
            )

        if not config.backstory:
            config.backstory = (
                "You are a seasoned software architect with deep expertise in system design, "
                "design patterns, and software engineering principles. You have architected "
                "systems ranging from microservices to monoliths, cloud-native to on-premise. "
                "You understand trade-offs between different architectural approaches and can "
                "make informed decisions based on requirements, constraints, and scale.\n\n"
                "Your expertise includes:\n"
                "- Microservices vs monolithic architectures\n"
                "- Event-driven architectures and message queuing\n"
                "- Database design and data modeling\n"
                "- API design (REST, GraphQL, gRPC)\n"
                "- Caching strategies and performance optimization\n"
                "- Security architecture and authentication patterns\n"
                "- Cloud architecture (AWS, Azure, GCP)\n"
                "- Design patterns (SOLID, DDD, CQRS, etc.)\n\n"
                "You create architectures that are:\n"
                "- Scalable and maintainable\n"
                "- Well-documented with clear diagrams\n"
                "- Based on proven patterns and best practices\n"
                "- Aligned with business and technical requirements\n"
                "- Pragmatic and implementable"
            )

        super().__init__(config)

    async def execute(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute an architecture task.

        Args:
            task_description: Description of the architecture task
            context: Optional context (e.g., requirements, constraints)

        Returns:
            Result containing architectural design
        """
        context = context or {}

        # Create the task for this agent
        task = self.create_task(
            description=task_description,
            expected_output=(
                "Technical architecture design with:\n"
                "1. System architecture overview\n"
                "2. Component breakdown and responsibilities\n"
                "3. Technology stack recommendations\n"
                "4. Data flow and component interactions\n"
                "5. Design patterns to use\n"
                "6. Scalability and performance considerations\n"
                "7. Security considerations\n"
                "8. Deployment architecture"
            ),
            context=context.get("previous_tasks", [])
        )

        # Execute the task using CrewAI
        result = self.execute_task_sync(task)

        return result

    async def design_architecture(
        self,
        specification: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Design system architecture based on specification.

        Args:
            specification: The specification to base architecture on
            context: Optional context (constraints, existing systems, etc.)

        Returns:
            Dictionary containing:
            - architecture: The architectural design
            - components: List of major components
            - technology_stack: Recommended technologies
            - design_decisions: Key architectural decisions
        """
        context = context or {}

        task_description = f"""
        Design a comprehensive system architecture based on this specification:

        SPECIFICATION:
        {specification}

        ARCHITECTURE DESIGN REQUIREMENTS:

        1. SYSTEM OVERVIEW:
           - High-level architecture diagram (describe in text/ASCII)
           - Main architectural pattern (e.g., MVC, microservices, layered)
           - Justification for chosen approach

        2. COMPONENT BREAKDOWN:
           - List all major components/modules
           - Describe responsibility of each component
           - Define interfaces between components
           - Identify shared components/utilities

        3. TECHNOLOGY STACK:
           - Backend framework recommendation
           - Database choice and rationale
           - API technology (REST/GraphQL/gRPC)
           - Authentication/Authorization approach
           - Caching strategy if needed
           - Message queue if needed

        4. DATA ARCHITECTURE:
           - Database schema design
           - Data models and relationships
           - Data flow between components
           - Data validation strategy

        5. API DESIGN:
           - API endpoints structure
           - Request/response formats
           - Versioning strategy
           - Error handling approach

        6. SECURITY ARCHITECTURE:
           - Authentication mechanism
           - Authorization strategy
           - Data encryption (at rest and in transit)
           - Input validation and sanitization
           - Rate limiting and DDoS protection

        7. SCALABILITY:
           - Horizontal vs vertical scaling approach
           - Caching layers
           - Database scaling strategy
           - Load balancing

        8. DEPLOYMENT:
           - Deployment model (containerized, serverless, etc.)
           - Infrastructure requirements
           - CI/CD considerations

        9. DESIGN PATTERNS:
           - Which design patterns to use and where
           - Why these patterns are appropriate

        10. TRADE-OFFS AND DECISIONS:
            - Key architectural decisions made
            - Trade-offs considered
            - Alternatives evaluated

        OPTIONAL TOOL USAGE:
        - If helpful, use create_specification to save the architecture document
        - Use create_specification(title="<Feature> Architecture Design", content="...")

        Provide a comprehensive but pragmatic architecture that can be implemented.
        """

        result = await self.execute(task_description, context)

        return {
            "architecture": result,
            "components": self._extract_components(result),
            "technology_stack": self._extract_tech_stack(result),
            "design_decisions": self._extract_decisions(result)
        }

    async def create_technical_plan(
        self,
        specification: str,
        architecture: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a technical implementation plan.

        Args:
            specification: Feature specification
            architecture: Architectural design
            context: Optional context

        Returns:
            Dictionary with implementation plan
        """
        context = context or {}

        task_description = f"""
        Create a detailed technical implementation plan:

        SPECIFICATION:
        {specification}

        ARCHITECTURE:
        {architecture}

        IMPLEMENTATION PLAN REQUIREMENTS:

        1. DEVELOPMENT PHASES:
           - Break down into logical phases
           - Define deliverables for each phase
           - Identify dependencies between phases

        2. COMPONENT IMPLEMENTATION ORDER:
           - Which components to build first
           - Why this order (dependencies, risk reduction)
           - Parallel development opportunities

        3. TECHNICAL TASKS:
           - Database setup and migrations
           - API endpoint implementation
           - Service layer development
           - Integration points
           - Testing infrastructure

        4. TECHNICAL CHALLENGES:
           - Identify potential technical challenges
           - Propose solutions or mitigation strategies
           - Highlight areas needing R&D

        5. DEPENDENCIES:
           - External libraries/frameworks needed
           - Third-party services/APIs
           - Infrastructure requirements

        6. TESTING STRATEGY:
           - Unit testing approach
           - Integration testing approach
           - E2E testing if needed

        Provide a clear, actionable plan that guides implementation.
        """

        result = await self.execute(task_description, context)

        return {
            "plan": result,
            "phases": self._extract_phases(result),
            "tasks": self._extract_tasks(result)
        }

    def _extract_components(self, result: str) -> List[str]:
        """Extract list of components from result."""
        components = []
        in_components_section = False

        for line in result.split('\n'):
            if "component" in line.lower() or "module" in line.lower():
                in_components_section = True
                continue

            if in_components_section and line.strip():
                if line.startswith('##'):
                    break
                # Look for component names (typically in lists)
                if line.strip().startswith('-') or line.strip().startswith('*'):
                    component = line.strip().lstrip('-*').strip()
                    if component:
                        components.append(component)

        return components[:10]  # Limit to first 10

    def _extract_tech_stack(self, result: str) -> Dict[str, str]:
        """Extract technology stack from result."""
        tech_stack = {}
        in_tech_section = False

        for line in result.split('\n'):
            if "technology" in line.lower() or "tech stack" in line.lower():
                in_tech_section = True
                continue

            if in_tech_section and line.strip():
                if line.startswith('##'):
                    break
                # Look for key-value pairs
                if ':' in line:
                    parts = line.split(':', 1)
                    key = parts[0].strip().lstrip('-*').strip()
                    value = parts[1].strip()
                    tech_stack[key] = value

        return tech_stack

    def _extract_decisions(self, result: str) -> List[str]:
        """Extract key design decisions from result."""
        decisions = []
        in_decisions_section = False

        for line in result.split('\n'):
            if "decision" in line.lower() or "trade-off" in line.lower():
                in_decisions_section = True
                continue

            if in_decisions_section and line.strip():
                if line.startswith('##'):
                    break
                if line.strip().startswith('-') or line.strip().startswith('*'):
                    decision = line.strip().lstrip('-*').strip()
                    if decision:
                        decisions.append(decision)

        return decisions[:5]  # Limit to first 5

    def _extract_phases(self, result: str) -> List[str]:
        """Extract implementation phases from result."""
        phases = []
        in_phases_section = False

        for line in result.split('\n'):
            if "phase" in line.lower():
                in_phases_section = True
                continue

            if in_phases_section and line.strip():
                if line.startswith('##'):
                    break
                if "phase" in line.lower():
                    phases.append(line.strip())

        return phases

    def _extract_tasks(self, result: str) -> List[str]:
        """Extract tasks from result."""
        tasks = []
        in_tasks_section = False

        for line in result.split('\n'):
            if "task" in line.lower():
                in_tasks_section = True
                continue

            if in_tasks_section and line.strip():
                if line.startswith('##'):
                    break
                if line.strip().startswith('-') or line.strip().startswith('*'):
                    task = line.strip().lstrip('-*').strip()
                    if task:
                        tasks.append(task)

        return tasks[:15]  # Limit to first 15
