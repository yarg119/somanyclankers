"""
ProjectManager Agent
Responsible for requirements analysis and specification creation.
"""

from typing import Any, Dict, List, Optional
import asyncio

from ..base_agent import BaseAgent, AgentConfig
from crewai import Task


class ProjectManagerAgent(BaseAgent):
    """
    ProjectManager agent specializes in:
    - Analyzing user requirements
    - Creating detailed specifications
    - Asking clarifying questions
    - Validating specifications for completeness
    """

    def __init__(self, config: AgentConfig):
        """Initialize ProjectManager agent."""
        # Set default configuration for ProjectManager if not provided
        if not config.role:
            config.role = "Requirements Analyst and Specification Specialist"

        if not config.goal:
            config.goal = (
                "Analyze user requirements, create comprehensive specifications, "
                "and ensure all stakeholders have a clear understanding of what needs to be built"
            )

        if not config.backstory:
            config.backstory = (
                "You are an experienced product manager and requirements analyst with a keen eye for detail. "
                "You excel at breaking down complex requirements into clear, actionable specifications. "
                "You always ask the right questions to uncover hidden requirements and edge cases. "
                "Your specifications are known for being thorough yet easy to understand."
            )

        super().__init__(config)

    async def execute(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute a requirements analysis task.

        Args:
            task_description: Description of the requirement to analyze
            context: Optional context (e.g., existing specs, user feedback)

        Returns:
            Result containing the specification and any clarifying questions
        """
        context = context or {}

        # Create the task for this agent
        task = self.create_task(
            description=task_description,
            expected_output=(
                "A detailed specification document with:\n"
                "1. Clear overview of the requirement\n"
                "2. Functional and non-functional requirements\n"
                "3. Architecture overview\n"
                "4. Implementation plan\n"
                "5. Acceptance criteria\n"
                "6. List of clarifying questions (if any)\n"
                "7. Dependencies and risks"
            ),
            context=context.get("previous_tasks", [])
        )

        # Execute the task using CrewAI
        result = self.execute_task_sync(task)

        return result

    async def analyze_requirements(self, user_requirement: str) -> Dict[str, Any]:
        """
        Analyze user requirements and create a specification.

        Args:
            user_requirement: The user's requirement description

        Returns:
            Dictionary containing:
            - specification: The created specification
            - questions: List of clarifying questions
            - confidence: Confidence score (0-1)
        """
        task_description = f"""
        Analyze the following user requirement and create a detailed specification document:

        Requirement: {user_requirement}

        CRITICAL INSTRUCTIONS:
        1. You MUST use the create_specification tool to save your specification
        2. First, analyze the requirement and draft a comprehensive specification
        3. Then use create_specification(title="...", content="...") to save it

        Your specification should include:
        1. Overview and Purpose
        2. Functional Requirements (numbered, with IDs like FR1, FR2, etc.)
        3. Non-Functional Requirements (NFR1, NFR2, etc.)
        4. Architecture Overview (design patterns, recommended approach)
        5. Implementation Plan (phases with time estimates)
        6. Acceptance Criteria (testable conditions)
        7. Clarifying Questions (to ask stakeholders)
        8. Dependencies and Risks (with severity and mitigation)

        TOOL USAGE:
        - Use create_specification(title="Feature Name Specification", content="full markdown content here")
        - The content should be formatted in Markdown
        - Include all sections listed above
        - Be detailed and thorough

        After saving the specification, provide a brief summary of what was created.

        Remember: ACTUALLY USE THE create_specification TOOL to save the document!
        """

        result = await self.execute(task_description)

        return {
            "specification": result,
            "questions": self._extract_questions(result),
            "confidence": self._calculate_confidence(result)
        }

    def _extract_questions(self, specification: str) -> List[str]:
        """Extract questions from the specification."""
        questions = []
        in_questions_section = False

        for line in specification.split('\n'):
            if "Open Questions" in line or "Clarifying Questions" in line:
                in_questions_section = True
                continue

            if in_questions_section:
                if line.startswith('##'):
                    break
                if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '-', '*')):
                    question = line.strip().lstrip('0123456789.-* ')
                    if question:
                        questions.append(question)

        return questions

    def _calculate_confidence(self, specification: str) -> float:
        """Calculate confidence score based on specification completeness."""
        required_sections = [
            "Overview",
            "Requirements",
            "Architecture",
            "Implementation Plan",
            "Acceptance Criteria"
        ]

        present_sections = sum(1 for section in required_sections if section in specification)
        todo_count = specification.count("TODO")
        question_count = specification.count("?")

        # Base confidence on section presence
        confidence = present_sections / len(required_sections)

        # Reduce confidence based on TODOs and questions
        confidence -= min(todo_count * 0.05, 0.3)
        confidence -= min(question_count * 0.02, 0.2)

        return max(0.0, min(1.0, confidence))

    async def refine_with_answers(
        self,
        spec_name: str,
        qa_pairs: Dict[str, str]
    ) -> str:
        """
        Refine a specification with answers to clarifying questions.

        Args:
            spec_name: Name of the specification to refine
            qa_pairs: Dictionary of questions and answers

        Returns:
            Updated specification
        """
        task_description = f"""
        Refine the specification '{spec_name}' by incorporating the following Q&A:

        {chr(10).join(f"Q: {q}\nA: {a}" for q, a in qa_pairs.items())}

        Update the specification to:
        1. Remove answered questions from the Open Questions section
        2. Incorporate the answers into the appropriate sections
        3. Expand on requirements based on the answers
        4. Update the implementation plan if needed
        5. Revise acceptance criteria based on new information
        """

        result = await self.execute(task_description)
        return result
