"""Diagnosis stage: analyzes execution failures and identifies root causes.

Given an ``ExecutionResult`` that indicates a failure, this module
determines the likely cause and suggests a repair strategy.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .execution import ExecutionResult


@dataclass
class Diagnosis:
    """Diagnosis of a failed execution."""

    error_category: str
    root_cause: str
    suggestion: str
    line_number: Optional[int] = None


def diagnose(result: ExecutionResult) -> Optional[Diagnosis]:
    """Analyze a failed execution result and produce a diagnosis.

    Args:
        result: The execution result to analyze.

    Returns:
        A ``Diagnosis`` if the execution failed, or ``None`` if it succeeded.
    """
    if result.success:
        return None

    error_type = result.error_type or "Unknown"
    error_msg = result.error or ""
    tb = result.traceback_str or ""

    line_number = _extract_line_number(tb)
    error_category = _categorize_error(error_type)
    root_cause = _identify_root_cause(error_type, error_msg)
    suggestion = _suggest_fix(error_type, error_msg)

    return Diagnosis(
        error_category=error_category,
        root_cause=root_cause,
        suggestion=suggestion,
        line_number=line_number,
    )


def _extract_line_number(traceback_str: str) -> Optional[int]:
    """Extract the line number from a traceback string."""
    match = re.search(r'line (\d+)', traceback_str)
    if match:
        return int(match.group(1))
    return None


def _categorize_error(error_type: str) -> str:
    """Categorize the error into a high-level category."""
    categories = {
        "SyntaxError": "syntax",
        "IndentationError": "syntax",
        "TabError": "syntax",
        "NameError": "reference",
        "AttributeError": "reference",
        "TypeError": "type",
        "ValueError": "value",
        "IndexError": "index",
        "KeyError": "key",
        "ZeroDivisionError": "arithmetic",
        "RecursionError": "recursion",
        "ImportError": "import",
        "ModuleNotFoundError": "import",
        "FileNotFoundError": "io",
        "IOError": "io",
        "PermissionError": "io",
    }
    return categories.get(error_type, "runtime")


def _identify_root_cause(error_type: str, error_msg: str) -> str:
    """Identify the root cause of the error."""
    if error_type == "NameError":
        match = re.search(r"name '(\w+)' is not defined", error_msg)
        if match:
            return f"Variable or function '{match.group(1)}' is used but not defined"
    elif error_type == "TypeError":
        if "argument" in error_msg:
            return "Function called with wrong number or type of arguments"
        if "unsupported operand" in error_msg:
            return "Operation applied to incompatible types"
    elif error_type == "IndexError":
        return "List index is out of the valid range"
    elif error_type == "KeyError":
        return "Dictionary key does not exist"
    elif error_type == "ZeroDivisionError":
        return "Division by zero encountered"
    elif error_type == "SyntaxError":
        return f"Syntax error in the code: {error_msg}"
    elif error_type == "RecursionError":
        return "Infinite recursion detected — missing or incorrect base case"
    elif error_type == "ValueError":
        return f"Invalid value: {error_msg}"

    return f"{error_type}: {error_msg}"


def _suggest_fix(error_type: str, error_msg: str) -> str:
    """Suggest a fix for the error."""
    if error_type == "NameError":
        match = re.search(r"name '(\w+)' is not defined", error_msg)
        if match:
            return f"Define '{match.group(1)}' before using it, or check for typos"
    elif error_type == "TypeError":
        if "argument" in error_msg:
            return "Check function signature and ensure correct number of arguments"
        return "Ensure operand types are compatible"
    elif error_type == "IndexError":
        return "Add bounds checking before accessing list elements"
    elif error_type == "KeyError":
        return "Use dict.get() or check key existence before access"
    elif error_type == "ZeroDivisionError":
        return "Add a check for zero before performing division"
    elif error_type == "SyntaxError":
        return "Review the code syntax near the reported line"
    elif error_type == "RecursionError":
        return "Add or fix the base case for recursion"

    return "Review the error message and fix the code accordingly"
