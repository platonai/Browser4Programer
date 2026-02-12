"""Intelligent agent for task flow management.

Provides a higher-level orchestrator that manages multiple programming
tasks through the existing pipeline.  The agent handles:

* **Task queuing** — accept and prioritise multiple tasks.
* **Dependency resolution** — ensure prerequisite tasks complete first.
* **State tracking** — maintain per-task status throughout the lifecycle.
* **Pipeline coordination** — delegate each task to :func:`run_pipeline`.
"""

from __future__ import annotations

import enum
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from .pipeline import PipelineResult, run_pipeline

logger = logging.getLogger(__name__)


class TaskStatus(enum.Enum):
    """Lifecycle status of a managed task."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskPriority(enum.Enum):
    """Priority levels for task ordering."""

    LOW = 1
    NORMAL = 2
    HIGH = 3


@dataclass
class TaskInfo:
    """Descriptor for a single task managed by the agent."""

    task_id: str
    description: str
    test_call: Optional[str] = None
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[PipelineResult] = None
    error_message: Optional[str] = None


@dataclass
class AgentResult:
    """Aggregated outcome of an agent run."""

    tasks: List[TaskInfo] = field(default_factory=list)

    @property
    def completed_count(self) -> int:
        """Number of tasks that finished successfully."""
        return sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)

    @property
    def failed_count(self) -> int:
        """Number of tasks that failed."""
        return sum(1 for t in self.tasks if t.status == TaskStatus.FAILED)

    @property
    def skipped_count(self) -> int:
        """Number of tasks that were skipped."""
        return sum(1 for t in self.tasks if t.status == TaskStatus.SKIPPED)

    @property
    def all_succeeded(self) -> bool:
        """``True`` when every task completed successfully."""
        return all(t.status == TaskStatus.COMPLETED for t in self.tasks)


class Agent:
    """Intelligent agent that manages a task workflow.

    Example usage::

        agent = Agent(max_iterations=5)
        agent.add_task("t1", "Write a function add that adds two numbers",
                       test_call="add(2, 3)")
        agent.add_task("t2", "Write a sort function", test_call="sort_list([3,1,2])",
                       dependencies=["t1"])
        result = agent.run()

    Args:
        max_iterations: Maximum repair iterations per task (forwarded to
            the pipeline).
        repair_command: Optional CLI command template for external repair
            tools.
    """

    def __init__(
        self,
        max_iterations: int = 5,
        repair_command: Optional[str] = None,
    ) -> None:
        self._tasks: Dict[str, TaskInfo] = {}
        self._max_iterations = max_iterations
        self._repair_command = repair_command

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @property
    def tasks(self) -> List[TaskInfo]:
        """Return all registered tasks in insertion order."""
        return list(self._tasks.values())

    def add_task(
        self,
        task_id: str,
        description: str,
        *,
        test_call: Optional[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: Optional[List[str]] = None,
    ) -> TaskInfo:
        """Register a new task with the agent.

        Args:
            task_id: Unique identifier for the task.
            description: Natural-language task description.
            test_call: Optional test expression forwarded to the pipeline.
            priority: Scheduling priority.
            dependencies: List of *task_id* values that must complete
                before this task may run.

        Returns:
            The newly created ``TaskInfo``.

        Raises:
            ValueError: If *task_id* is already registered or empty.
        """
        if not task_id or not task_id.strip():
            raise ValueError("task_id must not be empty")
        if task_id in self._tasks:
            raise ValueError(f"Duplicate task_id: {task_id!r}")

        task = TaskInfo(
            task_id=task_id,
            description=description,
            test_call=test_call,
            priority=priority,
            dependencies=list(dependencies) if dependencies else [],
        )
        self._tasks[task_id] = task
        logger.info("Task registered: %s", task_id)
        return task

    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """Look up a task by its ID.

        Returns:
            The ``TaskInfo`` or ``None`` if not found.
        """
        return self._tasks.get(task_id)

    # ------------------------------------------------------------------
    # Scheduling
    # ------------------------------------------------------------------

    def _resolve_order(self) -> List[str]:
        """Return task IDs in execution order (topological + priority).

        Tasks with unsatisfied dependencies that reference unknown IDs
        are marked *SKIPPED*.

        Raises:
            ValueError: If a dependency cycle is detected.
        """
        # Validate dependency references
        for task in self._tasks.values():
            for dep_id in task.dependencies:
                if dep_id not in self._tasks:
                    task.status = TaskStatus.SKIPPED
                    task.error_message = (
                        f"Dependency '{dep_id}' not found"
                    )
                    logger.warning(
                        "Task %s skipped — dependency '%s' not found",
                        task.task_id,
                        dep_id,
                    )

        # Kahn's algorithm for topological sort
        in_degree: Dict[str, int] = {tid: 0 for tid in self._tasks}
        for task in self._tasks.values():
            if task.status == TaskStatus.SKIPPED:
                continue
            for dep_id in task.dependencies:
                if dep_id in in_degree:
                    in_degree[task.task_id] += 1

        # Seed the queue with zero-in-degree tasks, sorted by priority
        queue: List[str] = sorted(
            [tid for tid, deg in in_degree.items()
             if deg == 0 and self._tasks[tid].status != TaskStatus.SKIPPED],
            key=lambda tid: self._tasks[tid].priority.value,
            reverse=True,
        )
        order: List[str] = []
        visited: Set[str] = set()

        while queue:
            tid = queue.pop(0)
            if tid in visited:
                continue
            visited.add(tid)
            order.append(tid)

            # Decrease in-degree for dependents
            for other in self._tasks.values():
                if other.status == TaskStatus.SKIPPED:
                    continue
                if tid in other.dependencies:
                    in_degree[other.task_id] -= 1
                    if in_degree[other.task_id] == 0:
                        queue.append(other.task_id)
            # Keep queue sorted by priority
            queue.sort(
                key=lambda t: self._tasks[t].priority.value,
                reverse=True,
            )

        # Detect cycles (tasks still with in_degree > 0 that aren't skipped)
        remaining = [
            tid for tid, deg in in_degree.items()
            if deg > 0 and self._tasks[tid].status != TaskStatus.SKIPPED
        ]
        if remaining:
            raise ValueError(
                f"Dependency cycle detected among tasks: {remaining}"
            )

        return order

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run(self) -> AgentResult:
        """Execute all registered tasks in dependency/priority order.

        Returns:
            An ``AgentResult`` summarising outcomes for every task.
        """
        logger.info("=== Agent Run Start ===")

        order = self._resolve_order()
        logger.info("Execution order: %s", order)

        completed: Set[str] = set()

        for task_id in order:
            task = self._tasks[task_id]

            # Skip if a dependency failed
            deps_ok = all(
                self._tasks[dep].status == TaskStatus.COMPLETED
                for dep in task.dependencies
                if dep in self._tasks
            )
            if not deps_ok:
                task.status = TaskStatus.SKIPPED
                task.error_message = "Skipped because a dependency failed"
                logger.warning("Task %s skipped — dependency failed", task_id)
                continue

            logger.info("--- Running task: %s ---", task_id)
            task.status = TaskStatus.RUNNING

            try:
                pipeline_result = run_pipeline(
                    task_description=task.description,
                    test_call=task.test_call,
                    max_iterations=self._max_iterations,
                    repair_command=self._repair_command,
                )
                task.result = pipeline_result

                if pipeline_result.success:
                    task.status = TaskStatus.COMPLETED
                    completed.add(task_id)
                    logger.info("Task %s completed successfully", task_id)
                else:
                    task.status = TaskStatus.FAILED
                    task.error_message = "Pipeline did not succeed"
                    logger.warning("Task %s failed", task_id)

            except Exception as exc:
                task.status = TaskStatus.FAILED
                task.error_message = str(exc)
                logger.exception("Task %s raised an exception", task_id)

        agent_result = AgentResult(tasks=list(self._tasks.values()))
        logger.info(
            "=== Agent Run Complete — %d/%d succeeded ===",
            agent_result.completed_count,
            len(agent_result.tasks),
        )
        return agent_result
