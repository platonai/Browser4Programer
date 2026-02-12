"""Design stage: produces a solution blueprint from task requirements.

Given structured requirements, this module generates a design that
describes the approach, algorithm, data structures, and function
signature to be used when generating code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .understanding import TaskRequirements


@dataclass
class SolutionDesign:
    """Blueprint for a code solution."""

    function_name: str
    parameters: List[str] = field(default_factory=list)
    return_type: str = "Any"
    algorithm_steps: List[str] = field(default_factory=list)
    description: str = ""


def design_solution(requirements: TaskRequirements) -> SolutionDesign:
    """Create a solution design from task requirements.

    Args:
        requirements: Structured task requirements.

    Returns:
        A ``SolutionDesign`` describing the planned implementation.
    """
    function_name = requirements.function_name or "solution"
    parameters = _derive_parameters(requirements)
    return_type = _derive_return_type(requirements)
    algorithm_steps = _derive_algorithm_steps(requirements)

    return SolutionDesign(
        function_name=function_name,
        parameters=parameters,
        return_type=return_type,
        algorithm_steps=algorithm_steps,
        description=requirements.description,
    )


def _derive_parameters(requirements: TaskRequirements) -> List[str]:
    """Derive function parameters from the requirements."""
    desc_lower = requirements.description.lower()

    # Ordered from most specific to least specific to avoid overlap
    param_hints = [
        ("two integers", ["a: int", "b: int"]),
        ("two numbers", ["a: int", "b: int"]),
        ("two strings", ["s1: str", "s2: str"]),
        ("factorial", ["n: int"]),
        ("fibonacci", ["n: int"]),
        ("list", ["items: list"]),
        ("array", ["arr: list"]),
        ("string", ["s: str"]),
        ("text", ["text: str"]),
        ("number", ["n: int"]),
        ("integer", ["n: int"]),
        ("of n", ["n: int"]),
        ("dictionary", ["data: dict"]),
        ("dict", ["data: dict"]),
    ]

    for hint, params in param_hints:
        if hint in desc_lower:
            return params

    return ["data"]


def _derive_return_type(requirements: TaskRequirements) -> str:
    """Derive the return type from the requirements."""
    desc_lower = requirements.description.lower()

    type_hints = {
        "true or false": "bool",
        "boolean": "bool",
        "count": "int",
        "number": "int",
        "sum": "int",
        "average": "float",
        "mean": "float",
        "list": "list",
        "string": "str",
        "sorted": "list",
        "dictionary": "dict",
    }

    for hint, rtype in type_hints.items():
        if hint in desc_lower:
            return rtype

    return "Any"


def _derive_algorithm_steps(requirements: TaskRequirements) -> List[str]:
    """Derive high-level algorithm steps from the requirements."""
    steps = ["Validate inputs"]

    desc_lower = requirements.description.lower()
    if "sort" in desc_lower:
        steps.append("Sort the data")
    if "filter" in desc_lower:
        steps.append("Filter elements based on condition")
    if "sum" in desc_lower or "add" in desc_lower:
        steps.append("Compute the sum")
    if "search" in desc_lower or "find" in desc_lower:
        steps.append("Search for the target element")
    if "reverse" in desc_lower:
        steps.append("Reverse the data")
    if "count" in desc_lower:
        steps.append("Count matching elements")
    if "convert" in desc_lower or "transform" in desc_lower:
        steps.append("Transform the data")

    steps.append("Return the result")
    return steps
