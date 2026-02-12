"""Markdown processor: extract, normalize, execute, diagnose, and auto-fix code blocks.

Reads a Markdown document, extracts fenced code blocks, normalizes
them, and runs each block through the execution → diagnosis → repair
loop until it succeeds or the maximum number of iterations is reached.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional

from .execution import ExecutionResult, execute_code
from .diagnosis import Diagnosis, diagnose
from .repair import repair_code

logger = logging.getLogger(__name__)

DEFAULT_MAX_ITERATIONS = 5


@dataclass
class CodeBlock:
    """A single code block extracted from a Markdown document."""

    language: str
    source: str
    start_line: int


@dataclass
class BlockResult:
    """Result of processing a single code block."""

    block_index: int
    original_code: str
    final_code: str
    success: bool
    iterations: int
    execution_result: Optional[ExecutionResult] = None
    last_diagnosis: Optional[Diagnosis] = None


@dataclass
class MarkdownResult:
    """Aggregated result of processing all code blocks in a document."""

    filepath: str
    total_blocks: int
    block_results: List[BlockResult] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.block_results if r.success)

    @property
    def failure_count(self) -> int:
        return sum(1 for r in self.block_results if not r.success)


# ---------------------------------------------------------------------------
# Stage 1: Extract
# ---------------------------------------------------------------------------

_FENCE_RE = re.compile(
    r"^(?P<fence>`{3,}|~{3,})(?P<lang>\w*)\s*\n(?P<code>.*?)^(?P=fence)\s*$",
    re.MULTILINE | re.DOTALL,
)


def extract_code_blocks(markdown_text: str) -> List[CodeBlock]:
    """Extract fenced code blocks from *markdown_text*.

    Supports both backtick (```) and tilde (~~~) fences.  The optional
    language identifier (e.g. ``python``) is captured when present.

    Args:
        markdown_text: The raw Markdown content.

    Returns:
        A list of ``CodeBlock`` objects in document order.
    """
    blocks: List[CodeBlock] = []
    for m in _FENCE_RE.finditer(markdown_text):
        start_line = markdown_text[: m.start()].count("\n") + 1
        blocks.append(
            CodeBlock(
                language=m.group("lang").lower(),
                source=m.group("code"),
                start_line=start_line,
            )
        )
    return blocks


# ---------------------------------------------------------------------------
# Stage 2: Normalize
# ---------------------------------------------------------------------------

def normalize_code(source: str) -> str:
    """Clean and normalise extracted source code.

    * Strips leading/trailing blank lines.
    * Removes a common leading indent (dedent).
    * Replaces tab characters with four spaces.
    * Ensures the code ends with a single newline.

    Args:
        source: Raw code extracted from a Markdown code block.

    Returns:
        The normalized source code.
    """
    # Replace tabs with spaces
    code = source.expandtabs(4)

    # Strip leading/trailing blank lines while preserving internal structure
    lines = code.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        return ""

    # Dedent: remove the smallest common indent
    non_empty = [line for line in lines if line.strip()]
    if non_empty:
        min_indent = min(len(line) - len(line.lstrip()) for line in non_empty)
        if min_indent > 0:
            lines = [line[min_indent:] if len(line) >= min_indent else line for line in lines]

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Stages 3-6: Execute → Diagnose → Repair loop
# ---------------------------------------------------------------------------

def _run_block_loop(
    source: str,
    block_index: int,
    max_iterations: int,
) -> BlockResult:
    """Run the execute → diagnose → repair loop for a single code block."""
    original = source

    for iteration in range(1, max_iterations + 1):
        logger.info(
            "  Block %d — iteration %d/%d", block_index, iteration, max_iterations
        )

        # Execute
        result = execute_code(source)

        if result.success:
            logger.info("  Block %d — success", block_index)
            return BlockResult(
                block_index=block_index,
                original_code=original,
                final_code=source,
                success=True,
                iterations=iteration,
                execution_result=result,
            )

        # Diagnose
        diag = diagnose(result)
        if diag:
            logger.info("  Block %d — %s: %s", block_index, diag.error_category, diag.root_cause)

            # Repair
            repaired = repair_code(source, diag)
            if repaired != source:
                source = repaired
                logger.info("  Block %d — repaired, retrying", block_index)
            else:
                logger.info("  Block %d — no automatic repair available", block_index)
                return BlockResult(
                    block_index=block_index,
                    original_code=original,
                    final_code=source,
                    success=False,
                    iterations=iteration,
                    execution_result=result,
                    last_diagnosis=diag,
                )
        else:
            logger.info("  Block %d — no diagnosis available", block_index)
            return BlockResult(
                block_index=block_index,
                original_code=original,
                final_code=source,
                success=False,
                iterations=iteration,
                execution_result=result,
            )

    # Max iterations reached
    last_result = execute_code(source)
    last_diag = diagnose(last_result) if not last_result.success else None
    return BlockResult(
        block_index=block_index,
        original_code=original,
        final_code=source,
        success=last_result.success,
        iterations=max_iterations,
        execution_result=last_result,
        last_diagnosis=last_diag,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def process_markdown(
    filepath: str,
    *,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
) -> MarkdownResult:
    """Process all code blocks in a Markdown file.

    For each fenced code block the pipeline performs:
      1. **Extract** — pull code blocks from the Markdown source
      2. **Normalize** — clean up indentation, whitespace, tabs
      3. **Execute** — run the code in a sandboxed namespace
      4. **Diagnose** — analyze any execution failure
      5. **Repair** — auto-fix the code and loop back to step 3

    Only blocks whose language identifier is ``python`` (or empty) are
    executed; all others are skipped.

    Args:
        filepath: Path to the Markdown file.
        max_iterations: Maximum repair iterations per block.

    Returns:
        A ``MarkdownResult`` summarising outcomes for every block.
    """
    logger.info("=== Markdown Processing Start ===")
    logger.info("File: %s", filepath)

    with open(filepath, encoding="utf-8") as fh:
        markdown_text = fh.read()

    return process_markdown_text(
        markdown_text,
        filepath=filepath,
        max_iterations=max_iterations,
    )


def process_markdown_text(
    markdown_text: str,
    *,
    filepath: str = "<string>",
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
) -> MarkdownResult:
    """Process code blocks from raw Markdown text.

    This is the same as :func:`process_markdown` but accepts the Markdown
    content directly instead of reading from a file.

    Args:
        markdown_text: Raw Markdown content.
        filepath: Label used in the result (default ``"<string>"``).
        max_iterations: Maximum repair iterations per block.

    Returns:
        A ``MarkdownResult`` summarising outcomes for every block.
    """
    # Stage 1: Extract
    blocks = extract_code_blocks(markdown_text)
    logger.info("Extracted %d code block(s)", len(blocks))

    executable_blocks = [
        b for b in blocks if b.language in ("python", "")
    ]
    logger.info("Executable blocks: %d", len(executable_blocks))

    md_result = MarkdownResult(filepath=filepath, total_blocks=len(blocks))

    for idx, block in enumerate(executable_blocks):
        logger.info("Processing block %d (line %d)", idx, block.start_line)

        # Stage 2: Normalize
        normalized = normalize_code(block.source)
        if not normalized.strip():
            logger.info("  Block %d - empty after normalization, skipping", idx)
            continue

        # Stages 3-6: Execute → Diagnose → Repair loop
        block_result = _run_block_loop(normalized, idx, max_iterations)
        md_result.block_results.append(block_result)

    logger.info(
        "=== Markdown Processing Complete — %d/%d succeeded ===",
        md_result.success_count,
        len(md_result.block_results),
    )
    return md_result
