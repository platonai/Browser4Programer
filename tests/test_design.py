"""Tests for the design stage."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from auto_coder.understanding import TaskRequirements
from auto_coder.design import design_solution, SolutionDesign


class TestDesignSolution:
    """Tests for design_solution()."""

    def test_returns_solution_design(self):
        req = TaskRequirements(description="Sort a list of numbers")
        design = design_solution(req)
        assert isinstance(design, SolutionDesign)

    def test_uses_function_name(self):
        req = TaskRequirements(description="Sort a list", function_name="my_sort")
        design = design_solution(req)
        assert design.function_name == "my_sort"

    def test_default_function_name(self):
        req = TaskRequirements(description="Do something")
        design = design_solution(req)
        assert design.function_name == "solution"

    def test_has_algorithm_steps(self):
        req = TaskRequirements(description="Sort and filter a list")
        design = design_solution(req)
        assert len(design.algorithm_steps) >= 2  # at least validate + return

    def test_derives_list_parameter(self):
        req = TaskRequirements(description="Sort a list of numbers")
        design = design_solution(req)
        assert any("list" in p for p in design.parameters)

    def test_derives_return_type_bool(self):
        req = TaskRequirements(description="Return true or false")
        design = design_solution(req)
        assert design.return_type == "bool"
