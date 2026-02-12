"""Tests for the diagnosis stage."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from auto_coder.execution import ExecutionResult
from auto_coder.diagnosis import diagnose, Diagnosis


class TestDiagnose:
    """Tests for diagnose()."""

    def test_returns_none_for_success(self):
        result = ExecutionResult(success=True)
        assert diagnose(result) is None

    def test_diagnoses_name_error(self):
        result = ExecutionResult(
            success=False,
            error="name 'foo' is not defined",
            error_type="NameError",
            traceback_str="File '<string>', line 1",
        )
        diag = diagnose(result)
        assert diag is not None
        assert diag.error_category == "reference"
        assert "foo" in diag.root_cause

    def test_diagnoses_type_error(self):
        result = ExecutionResult(
            success=False,
            error="unsupported operand type(s)",
            error_type="TypeError",
            traceback_str="File '<string>', line 2",
        )
        diag = diagnose(result)
        assert diag is not None
        assert diag.error_category == "type"

    def test_diagnoses_zero_division(self):
        result = ExecutionResult(
            success=False,
            error="division by zero",
            error_type="ZeroDivisionError",
            traceback_str="File '<string>', line 3",
        )
        diag = diagnose(result)
        assert diag is not None
        assert diag.error_category == "arithmetic"

    def test_extracts_line_number(self):
        result = ExecutionResult(
            success=False,
            error="error",
            error_type="RuntimeError",
            traceback_str="File '<string>', line 42, in <module>",
        )
        diag = diagnose(result)
        assert diag is not None
        assert diag.line_number == 42

    def test_suggestion_not_empty(self):
        result = ExecutionResult(
            success=False,
            error="name 'x' is not defined",
            error_type="NameError",
            traceback_str="",
        )
        diag = diagnose(result)
        assert diag is not None
        assert diag.suggestion != ""
