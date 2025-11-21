"""
Base Agent Class
Provides common functionality for all specialized agents.
"""

from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
import os
import sys
from pathlib import Path

from crewai import Agent, Task
from pydantic import BaseModel

# Add tools directory to path
tools_dir = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(tools_dir))

from simple_tools import get_simple_tools_for_agent


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    name: str
    role: str
    goal: str
    backstory: str
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    tools: List[str] = []
    fallback_model: Optional[str] = None
    base_directory: Optional[str] = None


class BaseAgent(ABC):
    """
    Base class for all specialized agents in the system.

    Each agent has:
    - A specific role and expertise area
    - Access to MCP tools via CrewAI
    - Configuration for LLM model selection
    - Methods for executing tasks
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize the base agent.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.agent = None
        self._initialize_agent()

    def _initialize_agent(self):
        """Initialize the CrewAI agent with configuration."""
        # Get LLM configuration from model config
        llm_config = self._get_llm_config()

        # Get simple tools based on configuration and base directory
        tools = get_simple_tools_for_agent(
            self.config.tools,
            base_directory=self.config.base_directory
        )

        # Create CrewAI agent
        self.agent = Agent(
            role=self.config.role,
            goal=self.config.goal,
            backstory=self.config.backstory,
            verbose=True,
            allow_delegation=False,
            llm=llm_config,
            tools=tools
        )

    def _get_llm_config(self) -> str:
        """
        Get LLM configuration based on model name.

        Returns:
            LLM model string for CrewAI (uses LiteLLM format)
        """
        model_name = self.config.model

        # Check if it's a local model (Ollama)
        if "deepseek" in model_name.lower() or ":" in model_name:
            # Format for Ollama models in LiteLLM: ollama/<model_name>
            return f"ollama/{model_name}"

        # Cloud models (Anthropic Claude)
        elif "claude" in model_name.lower():
            # For Claude, we need to use the actual API model name
            # Map our config names to actual API model names
            model_mapping = {
                "claude-sonnet-4": "claude-3-5-sonnet-20241022",  # Claude 3.5 Sonnet (latest)
                "claude-opus-4": "claude-3-opus-20240229",  # Claude 3 Opus
                "claude-haiku-4": "claude-3-5-haiku-20241022"  # Claude 3.5 Haiku
            }
            actual_model = model_mapping.get(model_name, model_name)
            return actual_model

        # Google Gemini models
        elif "gemini" in model_name.lower():
            # For Gemini, just use the model name as-is
            # CrewAI/google-genai will handle the formatting
            return model_name

        # OpenAI models
        elif "gpt" in model_name.lower():
            # Format for OpenAI: <model_name> (LiteLLM uses OPENAI_API_KEY env var)
            return model_name

        else:
            # Default to the model name as-is
            return model_name

    @abstractmethod
    async def execute(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute a task with this agent.

        Args:
            task_description: Description of the task to execute
            context: Optional context information

        Returns:
            Result of the task execution
        """
        pass

    def create_task(
        self,
        description: str,
        expected_output: str,
        context: Optional[List[Task]] = None
    ) -> Task:
        """
        Create a CrewAI task for this agent.

        Args:
            description: Task description
            expected_output: Expected output format
            context: Optional list of previous tasks for context

        Returns:
            CrewAI Task instance
        """
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent,
            context=context or []
        )

    def execute_task_sync(self, task: Task) -> str:
        """
        Execute a task synchronously using CrewAI.

        Args:
            task: The task to execute

        Returns:
            Task output as string
        """
        from crewai import Crew

        # Create a crew with just this agent and task
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )

        # Execute and get result
        result = crew.kickoff()
        return str(result)

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(role={self.config.role}, model={self.config.model})"
