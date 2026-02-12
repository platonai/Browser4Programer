"""Tests for the execution stage."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from auto_coder.execution import execute_code, ExecutionResult


class TestExecuteCode:
    """Tests for execute_code()."""

    def test_successful_execution(self):
        result = execute_code("x = 42")
        assert result.success is True
        assert result.error is None

    def test_syntax_error(self):
        result = execute_code("def bad(")
        assert result.success is False
        assert result.error_type == "SyntaxError"

    def test_runtime_error(self):
        result = execute_code("x = 1 / 0")
        assert result.success is False
        assert result.error_type == "ZeroDivisionError"

    def test_test_call_success(self):
        code = "def add(a, b): return a + b"
        result = execute_code(code, test_call="add(2, 3)")
        assert result.success is True
        assert result.return_value == 5

    def test_test_call_failure(self):
        code = "def add(a, b): return a + b"
        result = execute_code(code, test_call="add(2)")
        assert result.success is False
        assert result.error_type == "TypeError"

    def test_namespace_populated(self):
        result = execute_code("x = 42")
        assert result.namespace.get("x") == 42
