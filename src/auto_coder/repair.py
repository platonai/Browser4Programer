"""Repair stage: automatically fixes code based on a diagnosis.

Given the original source code and a ``Diagnosis``, this module
applies targeted repairs to produce corrected source code.
"""

from __future__ import annotations

import re

from .diagnosis import Diagnosis


def repair_code(source: str, diagnosis: Diagnosis) -> str:
    """Attempt to automatically repair source code based on a diagnosis.

    Args:
        source: The original (broken) source code.
        diagnosis: The diagnosis describing the problem.

    Returns:
        The repaired source code.  If no automatic repair is possible,
        returns the original source unchanged.
    """
    category = diagnosis.error_category

    repair_handlers = {
        "syntax": _repair_syntax,
        "reference": _repair_reference,
        "type": _repair_type,
        "index": _repair_index,
        "key": _repair_key,
        "arithmetic": _repair_arithmetic,
        "recursion": _repair_recursion,
    }

    handler = repair_handlers.get(category)
    if handler:
        return handler(source, diagnosis)

    return source


def _repair_syntax(source: str, diagnosis: Diagnosis) -> str:
    """Attempt to fix syntax errors."""
    lines = source.split("\n")

    # Fix common missing colons
    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if re.match(r'^\s*(def |if |elif |else|for |while |class |try|except|finally)', stripped):
            if stripped and not stripped.endswith(":") and not stripped.endswith("\\"):
                lines[i] = stripped + ":"

    # Fix unmatched parentheses
    open_count = source.count("(")
    close_count = source.count(")")
    if open_count > close_count:
        lines[-1] = lines[-1] + ")" * (open_count - close_count)
    elif close_count > open_count:
        # Remove extra closing parens from the end
        diff = close_count - open_count
        for i in range(len(lines) - 1, -1, -1):
            while diff > 0 and lines[i].rstrip().endswith(")"):
                lines[i] = lines[i].rstrip()[:-1]
                diff -= 1
            if diff == 0:
                break

    return "\n".join(lines)


def _repair_reference(source: str, diagnosis: Diagnosis) -> str:
    """Attempt to fix reference errors (NameError, AttributeError)."""
    match = re.search(r"'(\w+)'", diagnosis.root_cause)
    if not match:
        return source

    missing_name = match.group(1)
    lines = source.split("\n")

    # Check if it looks like a function call
    call_pattern = re.compile(rf'\b{re.escape(missing_name)}\s*\(')
    is_function_call = any(call_pattern.search(line) for line in lines)

    if is_function_call:
        # Add a stub function definition before the first use
        indent = ""
        for line in lines:
            if call_pattern.search(line):
                indent = re.match(r'^(\s*)', line).group(1)
                break
        stub = f"{indent}def {missing_name}(*args, **kwargs):\n{indent}    pass\n"
        return stub + source
    else:
        # Add a variable initialisation before the first use
        for i, line in enumerate(lines):
            if missing_name in line:
                indent = re.match(r'^(\s*)', line).group(1)
                lines.insert(i, f"{indent}{missing_name} = None")
                break
        return "\n".join(lines)


def _repair_type(source: str, diagnosis: Diagnosis) -> str:
    """Attempt to fix type errors."""
    if "unsupported operand" in diagnosis.root_cause:
        # Wrap numeric operations with int() / float()
        lines = source.split("\n")
        for i, line in enumerate(lines):
            if re.search(r'[\+\-\*/]', line) and not line.strip().startswith("#"):
                # Try to add explicit type conversion
                line = re.sub(r'(\b\w+\b)\s*([+\-*/])\s*(\b\w+\b)',
                              r'int(\1) \2 int(\3)', line, count=1)
                lines[i] = line
                break
        return "\n".join(lines)
    return source


def _repair_index(source: str, diagnosis: Diagnosis) -> str:
    """Attempt to fix index errors by adding bounds checking."""
    lines = source.split("\n")
    for i, line in enumerate(lines):
        match = re.search(r'(\w+)\[(\w+)\]', line)
        if match and not line.strip().startswith("#"):
            var_name = match.group(1)
            idx_expr = match.group(2)
            indent = re.match(r'^(\s*)', line).group(1)
            guard = f"{indent}if {idx_expr} < len({var_name}):\n"
            lines[i] = guard + "    " + line
            break
    return "\n".join(lines)


def _repair_key(source: str, diagnosis: Diagnosis) -> str:
    """Attempt to fix key errors by using .get()."""
    lines = source.split("\n")
    for i, line in enumerate(lines):
        match = re.search(r'(\w+)\[([\'"][^\'"]+[\'"])\]', line)
        if match and not line.strip().startswith("#"):
            var_name = match.group(1)
            key = match.group(2)
            old = f"{var_name}[{key}]"
            new = f"{var_name}.get({key})"
            lines[i] = line.replace(old, new)
            break
    return "\n".join(lines)


def _repair_arithmetic(source: str, diagnosis: Diagnosis) -> str:
    """Attempt to fix arithmetic errors like division by zero."""
    lines = source.split("\n")
    for i, line in enumerate(lines):
        if "/" in line and not line.strip().startswith("#"):
            match = re.search(r'/\s*(\w+)', line)
            if match:
                divisor = match.group(1)
                indent = re.match(r'^(\s*)', line).group(1)
                guard = f"{indent}if {divisor} == 0:\n{indent}    {divisor} = 1  # avoid division by zero\n"
                lines.insert(i, guard)
                break
    return "\n".join(lines)


def _repair_recursion(source: str, diagnosis: Diagnosis) -> str:
    """Attempt to fix infinite recursion by adding a base case."""
    lines = source.split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("def "):
            indent_match = re.match(r'^(\s*)', line)
            body_indent = (indent_match.group(1) if indent_match else "") + "    "
            # Find the parameter name
            param_match = re.search(r'def \w+\((\w+)', line)
            if param_match:
                param = param_match.group(1)
                base_case = (
                    f"{body_indent}if {param} <= 0:\n"
                    f"{body_indent}    return 0\n"
                )
                lines.insert(i + 1, base_case)
            break
    return "\n".join(lines)
