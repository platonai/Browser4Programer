"""Execution stage: safely runs generated code and captures results.

Executes Python source code in an isolated namespace and returns
the outcome, including any errors that occurred.
"""

from __future__ import annotations

import traceback
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ExecutionResult:
    """Result of executing generated code."""

    success: bool
    return_value: Any = None
    output: str = ""
    error: Optional[str] = None
    error_type: Optional[str] = None
    traceback_str: Optional[str] = None
    namespace: Dict[str, Any] = field(default_factory=dict)


def execute_code(source: str, test_call: Optional[str] = None) -> ExecutionResult:
    """Execute Python source code and optionally invoke a test call.

    The code is executed in a restricted namespace.  If *test_call* is
    provided, it is evaluated after the source has been executed, and
    its return value is captured.

    Args:
        source: Python source code to execute.
        test_call: Optional expression to evaluate after execution
                   (e.g. ``"add(2, 3)"``).

    Returns:
        An ``ExecutionResult`` with the outcome.
    """
    namespace: Dict[str, Any] = {"__builtins__": __builtins__}

    try:
        exec(source, namespace)  # noqa: S102
    except Exception as exc:
        return ExecutionResult(
            success=False,
            error=str(exc),
            error_type=type(exc).__name__,
            traceback_str=traceback.format_exc(),
            namespace=namespace,
        )

    if test_call is not None:
        try:
            result = eval(test_call, namespace)  # noqa: S307
            return ExecutionResult(
                success=True,
                return_value=result,
                namespace=namespace,
            )
        except Exception as exc:
            return ExecutionResult(
                success=False,
                return_value=None,
                error=str(exc),
                error_type=type(exc).__name__,
                traceback_str=traceback.format_exc(),
                namespace=namespace,
            )

    return ExecutionResult(success=True, namespace=namespace)
