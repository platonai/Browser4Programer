"""Understanding stage: parses and analyzes a programming task description.

Extracts structured requirements from a free-form task description,
including inputs, outputs, constraints, and expected behavior.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class TaskRequirements:
    """Structured representation of a programming task."""

    description: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    function_name: str = ""
    language: str = "python"


def understand_task(task_description: str) -> TaskRequirements:
    """Parse a task description and extract structured requirements.

    Args:
        task_description: Free-form text describing the programming task.

    Returns:
        A ``TaskRequirements`` object with extracted information.
    """
    if not task_description or not task_description.strip():
        raise ValueError("Task description must not be empty")

    description = task_description.strip()
    inputs = _extract_inputs(description)
    outputs = _extract_outputs(description)
    constraints = _extract_constraints(description)
    function_name = _extract_function_name(description)

    return TaskRequirements(
        description=description,
        inputs=inputs,
        outputs=outputs,
        constraints=constraints,
        function_name=function_name,
    )


def _extract_function_name(description: str) -> str:
    """Derive a function name from the task description."""
    # Match backtick/quote-wrapped names anywhere
    backtick_match = re.search(r"[`'\"](\w+)[`'\"]", description)
    if backtick_match:
        return backtick_match.group(1)
    match = re.search(
        r"(?:function|def|method)\s+(\w+)",
        description,
        re.IGNORECASE,
    )
    if match:
        return match.group(1)
    # Fallback: build a name from the first meaningful words
    words = re.findall(r"[a-zA-Z]+", description)
    name_words = [w.lower() for w in words[:3] if len(w) > 2]
    return "_".join(name_words) if name_words else "solution"


def _extract_inputs(description: str) -> List[str]:
    """Identify input parameters mentioned in the description."""
    patterns = [
        r"(?:takes?|accepts?|receives?|given|input[s]?)\s*[:\-]?\s*(.+?)(?:\.|,\s*(?:and\s+)?return|$)",
        r"parameter[s]?\s*[:\-]?\s*(.+?)(?:\.|$)",
    ]
    results: List[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, description, re.IGNORECASE):
            results.append(match.group(1).strip())
    return results


def _extract_outputs(description: str) -> List[str]:
    """Identify expected outputs mentioned in the description."""
    patterns = [
        r"(?:returns?|outputs?|produces?|yields?)\s*[:\-]?\s*(.+?)(?:\.|$)",
        r"(?:result|output)\s+(?:is|should be)\s*[:\-]?\s*(.+?)(?:\.|$)",
    ]
    results: List[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, description, re.IGNORECASE):
            results.append(match.group(1).strip())
    return results


def _extract_constraints(description: str) -> List[str]:
    """Identify constraints mentioned in the description."""
    patterns = [
        r"(?:must|should|cannot|without|limit|constraint|ensure)\s+(.+?)(?:\.|$)",
    ]
    results: List[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, description, re.IGNORECASE):
            results.append(match.group(1).strip())
    return results
