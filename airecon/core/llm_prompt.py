"""
airecon/core/llm_prompt.py

Prompt templates and parsers for structured LLM responses (e.g., JSON action schema).
Designed for use in AIRecon: autonomous cybersecurity agent with self-hosted LLM.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data models for structured actions
# ---------------------------------------------------------------------------

@dataclass
class ReconAction:
    """Represents a single reconnaissance action suggested by the LLM."""
    action_name: str
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action_name,
            "target": self.target,
            "parameters": self.parameters,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReconAction":
        return cls(
            action_name=data.get("action", ""),
            target=data.get("target", ""),
            parameters=data.get("parameters", {}),
            description=data.get("description"),
        )


@dataclass
class StructuredResponse:
    """Complete structured response from the LLM."""
    reasoning: Optional[str] = None
    actions: List[ReconAction] = field(default_factory=list)
    error: Optional[str] = None

    def is_valid(self) -> bool:
        return self.error is None and len(self.actions) > 0

    def to_json(self) -> str:
        return json.dumps(self.asdict(), indent=2)

    def asdict(self) -> Dict[str, Any]:
        return {
            "reasoning": self.reasoning,
            "actions": [a.to_dict() for a in self.actions],
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

class PromptBuilder:
    """
    Builds system and user prompts for the LLM to produce structured action JSON.

    The system prompt instructs the model to output a JSON object with fields:
    - reasoning: free‑text explanation
    - actions: list of action objects (action, target, parameters, description)

    Example output format:
    {
      "reasoning": "Discovered subdomain mail.example.com – starting port scan.",
      "actions": [
        {
          "action": "port_scan",
          "target": "mail.example.com",
          "parameters": {"ports": "22,80,443,8080"},
          "description": "Quick scan of common ports"
        }
      ]
    }
    """

    SYSTEM_PROMPT: str = """You are an autonomous cybersecurity reconnaissance agent.
Your task is to analyse the current state and output structured JSON only.

REQUIRED OUTPUT FORMAT: