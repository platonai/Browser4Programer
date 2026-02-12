"""Tests for the agent module."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from auto_coder.agent import (
    Agent,
    AgentResult,
    TaskInfo,
    TaskPriority,
    TaskStatus,
)


class TestAgentAddTask:
    """Tests for Agent.add_task."""

    def test_add_single_task(self):
        agent = Agent()
        task = agent.add_task("t1", "Write a function add")
        assert isinstance(task, TaskInfo)
        assert task.task_id == "t1"
        assert task.description == "Write a function add"
        assert task.status == TaskStatus.PENDING

    def test_add_task_with_options(self):
        agent = Agent()
        task = agent.add_task(
            "t1",
            "Write a function add",
            test_call="add(2, 3)",
            priority=TaskPriority.HIGH,
            dependencies=["t0"],
        )
        assert task.test_call == "add(2, 3)"
        assert task.priority == TaskPriority.HIGH
        assert task.dependencies == ["t0"]

    def test_duplicate_task_id_raises(self):
        agent = Agent()
        agent.add_task("t1", "Task one")
        with pytest.raises(ValueError, match="Duplicate task_id"):
            agent.add_task("t1", "Task two")

    def test_empty_task_id_raises(self):
        agent = Agent()
        with pytest.raises(ValueError, match="task_id must not be empty"):
            agent.add_task("", "Some task")

    def test_whitespace_task_id_raises(self):
        agent = Agent()
        with pytest.raises(ValueError, match="task_id must not be empty"):
            agent.add_task("   ", "Some task")

    def test_tasks_property(self):
        agent = Agent()
        agent.add_task("t1", "Task one")
        agent.add_task("t2", "Task two")
        tasks = agent.tasks
        assert len(tasks) == 2
        assert tasks[0].task_id == "t1"
        assert tasks[1].task_id == "t2"


class TestAgentGetTask:
    """Tests for Agent.get_task."""

    def test_get_existing_task(self):
        agent = Agent()
        agent.add_task("t1", "Task one")
        task = agent.get_task("t1")
        assert task is not None
        assert task.task_id == "t1"

    def test_get_nonexistent_task(self):
        agent = Agent()
        assert agent.get_task("missing") is None


class TestAgentResolveOrder:
    """Tests for dependency resolution and priority ordering."""

    def test_single_task_order(self):
        agent = Agent()
        agent.add_task("t1", "Task one")
        order = agent._resolve_order()
        assert order == ["t1"]

    def test_priority_ordering(self):
        agent = Agent()
        agent.add_task("low", "Low task", priority=TaskPriority.LOW)
        agent.add_task("high", "High task", priority=TaskPriority.HIGH)
        agent.add_task("normal", "Normal task", priority=TaskPriority.NORMAL)
        order = agent._resolve_order()
        assert order[0] == "high"

    def test_dependency_ordering(self):
        agent = Agent()
        agent.add_task("t2", "Second task", dependencies=["t1"])
        agent.add_task("t1", "First task")
        order = agent._resolve_order()
        assert order.index("t1") < order.index("t2")

    def test_unknown_dependency_skips_task(self):
        agent = Agent()
        agent.add_task("t1", "Task with missing dep", dependencies=["missing"])
        agent._resolve_order()
        task = agent.get_task("t1")
        assert task.status == TaskStatus.SKIPPED
        assert "not found" in task.error_message

    def test_cycle_detection(self):
        agent = Agent()
        agent.add_task("t1", "Task one", dependencies=["t2"])
        agent.add_task("t2", "Task two", dependencies=["t1"])
        with pytest.raises(ValueError, match="Dependency cycle"):
            agent._resolve_order()

    def test_chain_dependency(self):
        agent = Agent()
        agent.add_task("t3", "Third", dependencies=["t2"])
        agent.add_task("t1", "First")
        agent.add_task("t2", "Second", dependencies=["t1"])
        order = agent._resolve_order()
        assert order.index("t1") < order.index("t2")
        assert order.index("t2") < order.index("t3")


class TestAgentRun:
    """Integration tests for Agent.run."""

    def test_run_single_task(self):
        agent = Agent()
        agent.add_task(
            "add",
            "Write a function add that adds two numbers",
            test_call="add(2, 3)",
        )
        result = agent.run()
        assert isinstance(result, AgentResult)
        assert result.completed_count == 1
        assert result.all_succeeded is True

    def test_run_multiple_independent_tasks(self):
        agent = Agent()
        agent.add_task(
            "add",
            "Write a function add that adds two numbers",
            test_call="add(1, 1)",
        )
        agent.add_task(
            "sort",
            "Write a function sort_list that sorts a list",
            test_call="sort_list([3, 1, 2])",
        )
        result = agent.run()
        assert result.completed_count == 2
        assert result.all_succeeded is True

    def test_run_with_dependencies(self):
        agent = Agent()
        agent.add_task(
            "t1",
            "Write a function add that adds two numbers",
            test_call="add(2, 3)",
        )
        agent.add_task(
            "t2",
            "Write a function factorial that computes the factorial of n",
            test_call="factorial(5)",
            dependencies=["t1"],
        )
        result = agent.run()
        assert result.completed_count == 2
        assert result.all_succeeded is True

    def test_dependency_failure_skips_dependent(self):
        agent = Agent(max_iterations=1)
        agent.add_task(
            "bad",
            "Do something impossible with no clear pattern",
            test_call="impossible_function()",
        )
        agent.add_task(
            "good",
            "Write a function add that adds two numbers",
            test_call="add(2, 3)",
            dependencies=["bad"],
        )
        result = agent.run()
        bad_task = [t for t in result.tasks if t.task_id == "bad"][0]
        good_task = [t for t in result.tasks if t.task_id == "good"][0]
        assert bad_task.status == TaskStatus.FAILED
        assert good_task.status == TaskStatus.SKIPPED

    def test_run_empty_agent(self):
        agent = Agent()
        result = agent.run()
        assert result.completed_count == 0
        assert result.all_succeeded is True
        assert len(result.tasks) == 0


class TestAgentResult:
    """Tests for AgentResult properties."""

    def test_completed_count(self):
        result = AgentResult(tasks=[
            TaskInfo(task_id="t1", description="d1", status=TaskStatus.COMPLETED),
            TaskInfo(task_id="t2", description="d2", status=TaskStatus.FAILED),
        ])
        assert result.completed_count == 1

    def test_failed_count(self):
        result = AgentResult(tasks=[
            TaskInfo(task_id="t1", description="d1", status=TaskStatus.FAILED),
            TaskInfo(task_id="t2", description="d2", status=TaskStatus.FAILED),
        ])
        assert result.failed_count == 2

    def test_skipped_count(self):
        result = AgentResult(tasks=[
            TaskInfo(task_id="t1", description="d1", status=TaskStatus.SKIPPED),
        ])
        assert result.skipped_count == 1

    def test_all_succeeded_true(self):
        result = AgentResult(tasks=[
            TaskInfo(task_id="t1", description="d1", status=TaskStatus.COMPLETED),
        ])
        assert result.all_succeeded is True

    def test_all_succeeded_false(self):
        result = AgentResult(tasks=[
            TaskInfo(task_id="t1", description="d1", status=TaskStatus.COMPLETED),
            TaskInfo(task_id="t2", description="d2", status=TaskStatus.FAILED),
        ])
        assert result.all_succeeded is False

    def test_all_succeeded_empty(self):
        result = AgentResult(tasks=[])
        assert result.all_succeeded is True


class TestTaskPriority:
    """Tests for TaskPriority enum."""

    def test_ordering(self):
        assert TaskPriority.LOW.value < TaskPriority.NORMAL.value
        assert TaskPriority.NORMAL.value < TaskPriority.HIGH.value


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_values(self):
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.SKIPPED.value == "skipped"
