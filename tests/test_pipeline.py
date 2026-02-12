"""Tests for the pipeline (end-to-end)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from auto_coder.pipeline import run_pipeline, PipelineResult


class TestPipeline:
    """End-to-end tests for the pipeline."""

    def test_add_two_numbers(self):
        result = run_pipeline(
            task_description="Write a function add that adds two numbers",
            test_call="add(2, 3)",
        )
        assert isinstance(result, PipelineResult)
        assert result.success is True
        assert result.final_result.return_value == 5

    def test_sort_list(self):
        result = run_pipeline(
            task_description="Write a function sort_list that sorts a list",
            test_call="sort_list([3, 1, 2])",
        )
        assert result.success is True
        assert result.final_result.return_value == [1, 2, 3]

    def test_factorial(self):
        result = run_pipeline(
            task_description="Write a function factorial that computes the factorial of n",
            test_call="factorial(5)",
        )
        assert result.success is True
        assert result.final_result.return_value == 120

    def test_palindrome(self):
        result = run_pipeline(
            task_description="Write a function is_palindrome that checks if a string is a palindrome",
            test_call="is_palindrome('racecar')",
        )
        assert result.success is True
        assert result.final_result.return_value is True

    def test_pipeline_tracks_iterations(self):
        result = run_pipeline(
            task_description="Write a function add that adds two numbers",
            test_call="add(1, 1)",
        )
        assert result.total_iterations >= 1
        assert len(result.iterations) >= 1

    def test_max_iterations_respected(self):
        # This task will likely fail but should respect the limit
        result = run_pipeline(
            task_description="Do something impossible with no clear pattern",
            test_call="impossible_function()",
            max_iterations=2,
        )
        assert result.total_iterations <= 2
