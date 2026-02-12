"""Command-line interface for auto_coder.

Usage:
    python -m auto_coder "Write a function that computes the factorial of n"
    python -m auto_coder --task "Sort a list" --test "solution([3,1,2])"
"""

from __future__ import annotations

import argparse
import logging
import sys

from .pipeline import run_pipeline


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

    task_description = args.task or args.task_flag
    if not task_description:
        parser.error("A task description is required")

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

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


if __name__ == "__main__":
    sys.exit(main())
