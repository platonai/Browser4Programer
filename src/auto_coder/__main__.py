"""Command-line interface for auto_coder.

Usage:
    python -m auto_coder "Write a function that computes the factorial of n"
    python -m auto_coder --task "Sort a list" --test "solution([3,1,2])"
    python -m auto_coder --markdown examples/demo.md
"""

from __future__ import annotations

import argparse
import logging
import sys

from .pipeline import run_pipeline
from .markdown_processor import process_markdown


def main(argv: list[str] | None = None) -> int:
    """Entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="auto_coder",
        description="Self-evolving programming automation pipeline.",
    )
    parser.add_argument(
        "task",
        nargs="?",
        help="Programming task description",
    )
    parser.add_argument(
        "--task", "-t",
        dest="task_flag",
        help="Programming task description (alternative flag)",
    )
    parser.add_argument(
        "--test",
        dest="test_call",
        default=None,
        help="Test expression to verify correctness (e.g. 'add(2, 3)')",
    )
    parser.add_argument(
        "--markdown", "--md",
        dest="markdown_file",
        default=None,
        help="Path to a Markdown file whose code blocks will be extracted, "
             "executed, diagnosed, and auto-fixed",
    )
    parser.add_argument(
        "--max-iterations", "-m",
        type=int,
        default=5,
        help="Maximum repair iterations (default: 5)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args(argv)

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    # Markdown mode
    if args.markdown_file:
        md_result = process_markdown(
            args.markdown_file,
            max_iterations=args.max_iterations,
        )
        _print_markdown_result(md_result)
        return 0 if md_result.failure_count == 0 else 1

    # Task mode
    task_description = args.task or args.task_flag
    if not task_description:
        parser.error("A task description or --markdown file is required")

    result = run_pipeline(
        task_description=task_description,
        test_call=args.test_call,
        max_iterations=args.max_iterations,
    )

    _print_result(result)
    return 0 if result.success else 1


def _print_result(result):
    """Print a human-readable summary of the pipeline result."""
    print("\n" + "=" * 60)
    print("PIPELINE RESULT")
    print("=" * 60)
    print(f"Task: {result.task_description}")
    print(f"Status: {'SUCCESS' if result.success else 'FAILED'}")
    print(f"Iterations: {result.total_iterations}")
    print()
    print("--- Generated Code ---")
    print(result.final_code)
    if result.final_result and result.final_result.return_value is not None:
        print(f"Return value: {result.final_result.return_value}")
    if not result.success and result.iterations:
        last = result.iterations[-1]
        if last.diagnosis:
            print(f"\nLast error: {last.diagnosis.root_cause}")
            print(f"Suggestion: {last.diagnosis.suggestion}")
    print("=" * 60)


def _print_markdown_result(md_result):
    """Print a human-readable summary of the Markdown processing result."""
    print("\n" + "=" * 60)
    print("MARKDOWN PROCESSING RESULT")
    print("=" * 60)
    print(f"File: {md_result.filepath}")
    print(f"Total blocks: {md_result.total_blocks}")
    print(f"Executed: {len(md_result.block_results)}")
    print(f"Succeeded: {md_result.success_count}")
    print(f"Failed: {md_result.failure_count}")

    for br in md_result.block_results:
        status = "SUCCESS" if br.success else "FAILED"
        print(f"\n--- Block {br.block_index} [{status}] "
              f"({br.iterations} iteration(s)) ---")
        print(br.final_code)
        if not br.success and br.last_diagnosis:
            print(f"  Error: {br.last_diagnosis.root_cause}")
            print(f"  Suggestion: {br.last_diagnosis.suggestion}")

    print("=" * 60)


if __name__ == "__main__":
    sys.exit(main())
