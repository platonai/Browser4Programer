"""Programming stage: generates executable code from a solution design.

Translates a ``SolutionDesign`` into Python source code ready for
execution.
"""

from __future__ import annotations

from typing import List

from .design import SolutionDesign


def generate_code(design: SolutionDesign) -> str:
    """Generate Python source code from a solution design.

    Args:
        design: The solution blueprint.

    Returns:
        A string containing valid Python source code.
    """
    params_str = ", ".join(design.parameters)
    steps_comments = _format_steps_as_comments(design.algorithm_steps)
    body = _generate_body(design)

    lines = [
        f"def {design.function_name}({params_str}):",
        '    """',
        f"    {design.description}",
        '    """',
    ]
    code = "\n".join(lines) + "\n" + steps_comments + body
    return code


def apply_patch(source: str, patch: str) -> str:
    """Apply a code patch to existing source code.

    The *patch* is a string containing replacement source code.  If the
    patch is non-empty, it replaces the original source entirely.

    Args:
        source: The original source code.
        patch: The replacement code.

    Returns:
        The patched source code.
    """
    if patch and patch.strip():
        return patch.strip() + "\n"
    return source


def _format_steps_as_comments(steps: List[str]) -> str:
    """Format algorithm steps as inline comments."""
    lines: List[str] = []
    for i, step in enumerate(steps, 1):
        lines.append(f"    # Step {i}: {step}")
    return "\n".join(lines) + "\n" if lines else ""


def _generate_body(design: SolutionDesign) -> str:
    """Generate the function body based on the design."""
    desc_lower = design.description.lower()
    lines: List[str] = []

    if "sum" in desc_lower and "list" in desc_lower:
        lines.append("    total = 0")
        lines.append("    for item in items:")
        lines.append("        total += item")
        lines.append("    return total")
    elif "sort" in desc_lower:
        param = design.parameters[0].split(":")[0].strip() if design.parameters else "data"
        lines.append(f"    return sorted({param})")
    elif "reverse" in desc_lower:
        param = design.parameters[0].split(":")[0].strip() if design.parameters else "data"
        lines.append(f"    if isinstance({param}, str):")
        lines.append(f"        return {param}[::-1]")
        lines.append(f"    return list(reversed({param}))")
    elif "factorial" in desc_lower:
        lines.append("    if n < 0:")
        lines.append("        raise ValueError('n must be non-negative')")
        lines.append("    if n <= 1:")
        lines.append("        return 1")
        lines.append("    return n * %s(n - 1)" % design.function_name)
    elif "fibonacci" in desc_lower:
        lines.append("    if n <= 0:")
        lines.append("        return 0")
        lines.append("    if n == 1:")
        lines.append("        return 1")
        lines.append("    a, b = 0, 1")
        lines.append("    for _ in range(2, n + 1):")
        lines.append("        a, b = b, a + b")
        lines.append("    return b")
    elif "palindrome" in desc_lower:
        param = design.parameters[0].split(":")[0].strip() if design.parameters else "s"
        lines.append(f"    cleaned = str({param}).lower().replace(' ', '')")
        lines.append("    return cleaned == cleaned[::-1]")
    elif "count" in desc_lower:
        param = design.parameters[0].split(":")[0].strip() if design.parameters else "data"
        lines.append(f"    return len({param})")
    elif "max" in desc_lower or "largest" in desc_lower:
        param = design.parameters[0].split(":")[0].strip() if design.parameters else "data"
        lines.append(f"    return max({param})")
    elif "min" in desc_lower or "smallest" in desc_lower:
        param = design.parameters[0].split(":")[0].strip() if design.parameters else "data"
        lines.append(f"    return min({param})")
    elif "average" in desc_lower or "mean" in desc_lower:
        param = design.parameters[0].split(":")[0].strip() if design.parameters else "data"
        lines.append(f"    if not {param}:")
        lines.append("        return 0.0")
        lines.append(f"    return sum({param}) / len({param})")
    elif ("add" in desc_lower or "sum" in desc_lower) and "two" in desc_lower:
        lines.append("    return a + b")
    else:
        # Generic pass-through implementation
        param = design.parameters[0].split(":")[0].strip() if design.parameters else "data"
        lines.append(f"    return {param}")

    return "\n".join(lines) + "\n"
