"""
Agent System
Multi-agent orchestration for automated software development.
"""

from .base_agent import BaseAgent, AgentConfig
from .roles.project_manager import ProjectManagerAgent
from .roles.architect import ArchitectAgent
from .roles.coder import CoderAgent
from .roles.tester import TesterAgent
from .roles.reviewer import ReviewerAgent

__all__ = [
    "BaseAgent",
    "AgentConfig",
    "ProjectManagerAgent",
    "ArchitectAgent",
    "CoderAgent",
    "TesterAgent",
    "ReviewerAgent"
]
