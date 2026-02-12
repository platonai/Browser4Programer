"""Tests for the understanding stage."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from auto_coder.understanding import understand_task, TaskRequirements


class TestUnderstandTask:
    """Tests for understand_task()."""

    def test_empty_description_raises(self):
        with pytest.raises(ValueError):
            understand_task("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            understand_task("   ")

    def test_basic_task(self):
        req = understand_task("Write a function add that takes two numbers")
        assert isinstance(req, TaskRequirements)
        assert req.function_name == "add"
        assert req.description != ""

    def test_function_name_extraction(self):
        req = understand_task("Implement `factorial` for computing factorials")
        assert req.function_name == "factorial"

    def test_fallback_function_name(self):
        req = understand_task("sort a list of integers")
        assert req.function_name != ""

    def test_extracts_inputs(self):
        req = understand_task("A function that takes a list of numbers")
        assert len(req.inputs) > 0

    def test_extracts_outputs(self):
        req = understand_task("Returns the sum of all elements")
        assert len(req.outputs) > 0

    def test_extracts_constraints(self):
        req = understand_task("Must handle negative numbers")
        assert len(req.constraints) > 0
