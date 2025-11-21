"""
Reviewer Agent
Responsible for code quality review, specification adherence, and improvement suggestions.
"""

from typing import Any, Dict, List, Optional
import asyncio

from ..base_agent import BaseAgent, AgentConfig


class ReviewerAgent(BaseAgent):
    """
    Reviewer agent specializes in:
    - Reviewing code quality and style
    - Checking adherence to specifications
    - Identifying bugs and security issues
    - Providing constructive improvement suggestions
    - Ensuring best practices are followed
    """

    def __init__(self, config: AgentConfig):
        """Initialize Reviewer agent."""
        # Set default configuration for Reviewer if not provided
        if not config.role:
            config.role = "Code Quality and Review Specialist"

        if not config.goal:
            config.goal = (
                "Review code for quality, correctness, and adherence to specifications. "
                "Identify bugs, security issues, and improvement opportunities. "
                "Provide constructive feedback that helps improve code quality."
            )

        if not config.backstory:
            config.backstory = (
                "You are a senior code reviewer with extensive experience in multiple programming "
                "languages and frameworks. You have a keen eye for detail and can spot bugs, "
                "security vulnerabilities, and code smells that others miss. You understand "
                "software engineering best practices, design patterns, and clean code principles.\n\n"
                "Your expertise includes:\n"
                "- Code quality and maintainability assessment\n"
                "- Security vulnerability identification (OWASP Top 10)\n"
                "- Performance optimization opportunities\n"
                "- Design pattern and architecture review\n"
                "- Testing coverage and quality\n"
                "- Documentation completeness\n"
                "- Specification adherence validation\n"
                "- Best practices enforcement\n\n"
                "Your reviews are known for being:\n"
                "- Thorough and comprehensive\n"
                "- Constructive and educational\n"
                "- Focused on both correctness and maintainability\n"
                "- Balanced between perfectionism and pragmatism\n"
                "- Clear with specific examples and suggestions\n\n"
                "You provide feedback that helps developers improve while maintaining "
                "a collaborative and respectful tone. You explain the 'why' behind your "
                "suggestions, not just the 'what'."
            )

        super().__init__(config)

    async def execute(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute a code review task.

        Args:
            task_description: Description of the review task
            context: Optional context (e.g., code to review, specification)

        Returns:
            Result containing review findings and suggestions
        """
        context = context or {}

        # Create the task for this agent
        task = self.create_task(
            description=task_description,
            expected_output=(
                "Comprehensive code review with:\n"
                "1. Overall quality assessment\n"
                "2. Specification adherence check\n"
                "3. Bug and security issue identification\n"
                "4. Code quality issues (style, maintainability)\n"
                "5. Performance concerns\n"
                "6. Improvement suggestions\n"
                "7. Positive aspects worth noting\n"
                "8. Priority-ranked action items"
            ),
            context=context.get("previous_tasks", [])
        )

        # Execute the task using CrewAI
        result = self.execute_task_sync(task)

        return result

    async def review_code(
        self,
        code: str,
        specification: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Review code against specification.

        Args:
            code: The code to review
            specification: The specification to validate against
            context: Optional context

        Returns:
            Dictionary containing:
            - review_summary: Overall review summary
            - issues: List of identified issues
            - suggestions: List of improvement suggestions
            - score: Quality score (0-10)
        """
        context = context or {}

        task_description = f"""
        Conduct a comprehensive code review for the following code:

        SPECIFICATION:
        {specification}

        CODE TO REVIEW:
        {code}

        REVIEW REQUIREMENTS:

        1. SPECIFICATION ADHERENCE:
           - Does the code implement all specified requirements?
           - Are there any missing features or functionality?
           - Does it meet acceptance criteria?
           - Are there any deviations from the specification?

        2. CODE QUALITY:
           - Is the code readable and maintainable?
           - Are variable and function names descriptive?
           - Is the code properly structured and organized?
           - Are there any code smells or anti-patterns?
           - Is there appropriate use of comments/docstrings?
           - Does it follow language-specific conventions (PEP 8 for Python, etc.)?

        3. SECURITY:
           - Are there any security vulnerabilities?
           - Is input validation implemented properly?
           - Are there SQL injection risks?
           - Are there XSS vulnerabilities?
           - Is sensitive data handled securely?
           - Are authentication/authorization checks present?

        4. BUG IDENTIFICATION:
           - Are there any logical errors?
           - Are edge cases handled?
           - Are error conditions handled properly?
           - Are there potential runtime errors?
           - Are there any race conditions or concurrency issues?

        5. PERFORMANCE:
           - Are there performance bottlenecks?
           - Is the algorithm complexity reasonable?
           - Are there unnecessary loops or operations?
           - Is memory usage efficient?
           - Are database queries optimized (if applicable)?

        6. TESTING:
           - Is the code testable?
           - Are there tests included?
           - Is test coverage adequate?
           - Do tests cover edge cases?

        7. MAINTAINABILITY:
           - Is the code DRY (Don't Repeat Yourself)?
           - Are functions/methods focused and single-purpose?
           - Is coupling minimized?
           - Is cohesion maximized?
           - Would this be easy to extend or modify?

        8. DOCUMENTATION:
           - Are docstrings/comments present and helpful?
           - Is the API documented?
           - Are complex algorithms explained?
           - Are assumptions documented?

        OUTPUT FORMAT:

        ## Overall Assessment
        [Brief summary of code quality - 2-3 sentences]
        **Quality Score: X/10**

        ## Specification Adherence
        ✅ **Met Requirements:**
        - [List requirements that are properly implemented]

        ❌ **Missing or Incomplete:**
        - [List any missing functionality]

        ## Critical Issues
        🔴 **High Priority:**
        1. [Security vulnerabilities, bugs, major issues]

        🟡 **Medium Priority:**
        1. [Code quality issues, performance concerns]

        🟢 **Low Priority:**
        1. [Style improvements, minor suggestions]

        ## Positive Aspects
        ✨ [Things done well - be specific and encouraging]

        ## Detailed Findings

        ### Security
        [Security analysis]

        ### Code Quality
        [Quality analysis]

        ### Performance
        [Performance analysis]

        ### Testing
        [Testing analysis]

        ## Specific Improvement Suggestions

        1. **[Issue Title]**
           - **Problem:** [What's wrong]
           - **Impact:** [Why it matters]
           - **Suggestion:** [How to fix it]
           - **Example:** [Code example if applicable]

        2. [Continue for each major suggestion...]

        ## Action Items (Priority Ordered)

        1. [ ] **Critical:** [Must fix before deployment]
        2. [ ] **Important:** [Should fix soon]
        3. [ ] **Enhancement:** [Nice to have]

        ## Summary

        [Final thoughts and overall recommendation: Approve / Approve with changes / Needs work]

        Provide a thorough but constructive review. Balance critical feedback with recognition
        of good practices. Explain why issues matter and how to address them.
        """

        result = await self.execute(task_description, context)

        return {
            "review_summary": result,
            "issues": self._extract_issues(result),
            "suggestions": self._extract_suggestions(result),
            "score": self._extract_score(result)
        }

    async def review_architecture(
        self,
        architecture: str,
        specification: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Review architectural design.

        Args:
            architecture: The architecture design to review
            specification: The specification to validate against
            context: Optional context

        Returns:
            Dictionary with architecture review
        """
        context = context or {}

        task_description = f"""
        Review the following architectural design:

        SPECIFICATION:
        {specification}

        ARCHITECTURE DESIGN:
        {architecture}

        ARCHITECTURE REVIEW REQUIREMENTS:

        1. ALIGNMENT WITH REQUIREMENTS:
           - Does the architecture support all functional requirements?
           - Are non-functional requirements addressed (scalability, performance, security)?
           - Are there any gaps?

        2. ARCHITECTURAL PATTERNS:
           - Are appropriate patterns used?
           - Is the pattern correctly applied?
           - Are there better alternatives?

        3. SCALABILITY:
           - Can the system scale horizontally/vertically?
           - Are there bottlenecks in the design?
           - Is caching strategy appropriate?
           - Is the database design scalable?

        4. SECURITY ARCHITECTURE:
           - Is authentication/authorization properly designed?
           - Are security boundaries clear?
           - Is data protection adequate?
           - Are there security vulnerabilities in the design?

        5. MAINTAINABILITY:
           - Is the architecture modular?
           - Are components loosely coupled?
           - Is it easy to understand?
           - Can components be independently deployed/updated?

        6. TECHNOLOGY CHOICES:
           - Are technology choices appropriate?
           - Are they justified?
           - Are there better alternatives?
           - Are dependencies minimized?

        7. PERFORMANCE:
           - Will the architecture meet performance requirements?
           - Are there performance bottlenecks?
           - Is data flow efficient?

        8. DEPLOYMENT:
           - Is the deployment strategy sound?
           - Is it production-ready?
           - Are infrastructure requirements reasonable?

        Provide a comprehensive architecture review with specific feedback and suggestions.
        """

        result = await self.execute(task_description, context)

        return {
            "review": result,
            "concerns": self._extract_concerns(result),
            "recommendations": self._extract_recommendations(result)
        }

    async def create_review_summary(
        self,
        reviews: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a summary of multiple reviews.

        Args:
            reviews: List of review texts
            context: Optional context

        Returns:
            Consolidated review summary
        """
        context = context or {}

        task_description = f"""
        Create a consolidated summary of the following reviews:

        REVIEWS:
        {chr(10).join([f"Review {i+1}:{chr(10)}{review}{chr(10)}" for i, review in enumerate(reviews)])}

        SUMMARY REQUIREMENTS:

        1. Identify common themes across reviews
        2. Consolidate duplicate or similar issues
        3. Prioritize issues by frequency and severity
        4. Create a unified action plan
        5. Highlight areas of consensus and disagreement

        Provide a clear, actionable summary that synthesizes all reviews.
        """

        result = await self.execute(task_description, context)

        return result

    def _extract_issues(self, result: str) -> List[Dict[str, str]]:
        """Extract identified issues from review result."""
        issues = []
        current_priority = None

        for line in result.split('\n'):
            line_lower = line.lower()

            # Detect priority sections
            if 'high priority' in line_lower or '🔴' in line:
                current_priority = 'high'
                continue
            elif 'medium priority' in line_lower or '🟡' in line:
                current_priority = 'medium'
                continue
            elif 'low priority' in line_lower or '🟢' in line:
                current_priority = 'low'
                continue

            # Extract issues from list items
            if current_priority and line.strip():
                if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '-', '*')):
                    issue_text = line.strip().lstrip('0123456789.-* ').strip()
                    if issue_text and len(issue_text) > 10:  # Filter out headers
                        issues.append({
                            'priority': current_priority,
                            'description': issue_text
                        })

        return issues[:20]  # Limit to top 20 issues

    def _extract_suggestions(self, result: str) -> List[str]:
        """Extract improvement suggestions from review result."""
        suggestions = []
        in_suggestions_section = False

        for line in result.split('\n'):
            if 'suggestion' in line.lower() or 'improvement' in line.lower():
                in_suggestions_section = True
                continue

            if in_suggestions_section and line.strip():
                if line.startswith('##'):
                    break
                if line.strip().startswith(('-', '*', '1.', '2.', '3.', '4.', '5.')):
                    suggestion = line.strip().lstrip('-*0123456789. ').strip()
                    if suggestion and len(suggestion) > 10:
                        suggestions.append(suggestion)

        return suggestions[:15]  # Limit to top 15 suggestions

    def _extract_score(self, result: str) -> Optional[int]:
        """Extract quality score from review result."""
        for line in result.split('\n'):
            if 'score' in line.lower() and '/' in line:
                # Extract number before /10
                import re
                match = re.search(r'(\d+)\s*/\s*10', line)
                if match:
                    try:
                        return int(match.group(1))
                    except ValueError:
                        pass
        return None

    def _extract_concerns(self, result: str) -> List[str]:
        """Extract architectural concerns from review result."""
        concerns = []
        in_concerns_section = False

        for line in result.split('\n'):
            if 'concern' in line.lower() or 'issue' in line.lower() or 'risk' in line.lower():
                in_concerns_section = True
                continue

            if in_concerns_section and line.strip():
                if line.startswith('##'):
                    break
                if line.strip().startswith(('-', '*')):
                    concern = line.strip().lstrip('-* ').strip()
                    if concern:
                        concerns.append(concern)

        return concerns[:10]  # Limit to top 10 concerns

    def _extract_recommendations(self, result: str) -> List[str]:
        """Extract recommendations from review result."""
        recommendations = []
        in_recommendations_section = False

        for line in result.split('\n'):
            if 'recommendation' in line.lower() or 'suggest' in line.lower():
                in_recommendations_section = True
                continue

            if in_recommendations_section and line.strip():
                if line.startswith('##'):
                    break
                if line.strip().startswith(('-', '*', '1.', '2.', '3.')):
                    rec = line.strip().lstrip('-*0123456789. ').strip()
                    if rec:
                        recommendations.append(rec)

        return recommendations[:10]  # Limit to top 10 recommendations
