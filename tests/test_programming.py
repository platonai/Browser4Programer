"""Tests for the programming stage."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from auto_coder.design import SolutionDesign
from auto_coder.programming import generate_code, apply_patch


class TestGenerateCode:
    """Tests for generate_code()."""

    def test_generates_valid_python(self):
        design = SolutionDesign(
            function_name="add",
            parameters=["a: int", "b: int"],
            return_type="int",
            description="Add two numbers",
        )
        code = generate_code(design)
        assert "def add(" in code
        # Verify it compiles
        compile(code, "<test>", "exec")

    def test_contains_function_name(self):
        design = SolutionDesign(
            function_name="my_func",
            parameters=["x"],
            description="A function",
        )
        code = generate_code(design)
        assert "def my_func(" in code

    def test_contains_parameters(self):
        design = SolutionDesign(
            function_name="f",
            parameters=["a: int", "b: int"],
            description="test",
        )
        code = generate_code(design)
        assert "a: int" in code
        assert "b: int" in code


class TestApplyPatch:
    """Tests for apply_patch()."""

    def test_replaces_with_patch(self):
        result = apply_patch("old code", "new code")
        assert result == "new code\n"

    def test_keeps_original_on_empty_patch(self):
        result = apply_patch("original", "")
        assert result == "original"

    def test_keeps_original_on_whitespace_patch(self):
        result = apply_patch("original", "   ")
        assert result == "original"
