"""Pipeline controller: orchestrates the self-evolving closed loop.

Ties together all stages — understanding, design, programming,
execution, diagnosis, and repair — into an iterative cycle that
automatically evolves the solution until it passes or the maximum
number of iterations is reached.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional

from .understanding import TaskRequirements, understand_task
from .design import SolutionDesign, design_solution
from .programming import generate_code, apply_patch
from .execution import ExecutionResult, execute_code
from .diagnosis import Diagnosis, diagnose
from .repair import repair_code

logger = logging.getLogger(__name__)

DEFAULT_MAX_ITERATIONS = 5


@dataclass
class IterationRecord:
    """Record of a single iteration through the loop."""

    iteration: int
    source_code: str
    execution_result: ExecutionResult
    diagnosis: Optional[Diagnosis] = None
    repaired: bool = False


@dataclass
class PipelineResult:
    """Final result of the pipeline execution."""

    success: bool
    task_description: str
    requirements: TaskRequirements
    design: SolutionDesign
    final_code: str
    iterations: List[IterationRecord] = field(default_factory=list)
    total_iterations: int = 0
    final_result: Optional[ExecutionResult] = None


def run_pipeline(
    task_description: str,
    test_call: Optional[str] = None,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    repair_command: Optional[str] = None,
) -> PipelineResult:
    """Run the full self-evolving pipeline for a programming task.

    The pipeline performs:
      1. **Understanding** — parse the task description
      2. **Design** — create a solution blueprint
      3. **Programming** — generate code
      4. **Execution** — run the code
      5. **Diagnosis** — analyse failures
      6. **Repair** — patch the code and loop back to step 4

    Args:
        task_description: Natural-language description of the task.
        test_call: Optional expression used to verify correctness
                   (e.g. ``"add(2, 3)"``).
        max_iterations: Maximum repair iterations before giving up.
        repair_command: Optional CLI command template for external repair
                        tools.  Supports ``{issue_file}`` and
                        ``{source_file}`` placeholders.

    Returns:
        A ``PipelineResult`` summarising the outcome.
    """
    logger.info("=== Pipeline Start ===")
    logger.info("Task: %s", task_description)

    # Stage 1: Understanding
    logger.info("Stage 1: Understanding")
    requirements = understand_task(task_description)
    logger.info("  Function name: %s", requirements.function_name)

    # Stage 2: Design
    logger.info("Stage 2: Design")
    design = design_solution(requirements)
    logger.info("  Parameters: %s", design.parameters)
    logger.info("  Steps: %s", design.algorithm_steps)

    # Stage 3: Programming
    logger.info("Stage 3: Programming")
    source = generate_code(design)
    logger.info("  Generated %d bytes of code", len(source))

    iterations: List[IterationRecord] = []

    for iteration in range(1, max_iterations + 1):
        logger.info("--- Iteration %d/%d ---", iteration, max_iterations)

        # Stage 4: Execution
        logger.info("Stage 4: Execution")
        result = execute_code(source, test_call)
        logger.info("  Success: %s", result.success)

        record = IterationRecord(
            iteration=iteration,
            source_code=source,
            execution_result=result,
        )

        if result.success:
            logger.info("  Return value: %s", result.return_value)
            iterations.append(record)
            logger.info("=== Pipeline Complete (success) ===")
            return PipelineResult(
                success=True,
                task_description=task_description,
                requirements=requirements,
                design=design,
                final_code=source,
                iterations=iterations,
                total_iterations=iteration,
                final_result=result,
            )

        # Stage 5: Diagnosis
        logger.info("Stage 5: Diagnosis")
        diag = diagnose(result)
        record.diagnosis = diag
        if diag:
            logger.info("  Category: %s", diag.error_category)
            logger.info("  Root cause: %s", diag.root_cause)
            logger.info("  Suggestion: %s", diag.suggestion)

            # Stage 6: Repair
            logger.info("Stage 6: Repair")
            repaired_source = repair_code(source, diag, repair_command=repair_command)
            if repaired_source != source:
                record.repaired = True
                source = repaired_source
                logger.info("  Code repaired — retrying")
            else:
                logger.info("  No automatic repair available")
        else:
            logger.info("  No diagnosis available")

        iterations.append(record)

    logger.info("=== Pipeline Complete (max iterations reached) ===")
    return PipelineResult(
        success=False,
        task_description=task_description,
        requirements=requirements,
        design=design,
        final_code=source,
        iterations=iterations,
        total_iterations=max_iterations,
        final_result=iterations[-1].execution_result if iterations else None,
    )
