"""Tests for the repair stage."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from auto_coder.diagnosis import Diagnosis
from auto_coder.repair import repair_code


class TestRepairCode:
    """Tests for repair_code()."""

    def test_returns_original_on_unknown_category(self):
        diag = Diagnosis(
            error_category="unknown",
            root_cause="mystery",
            suggestion="investigate",
        )
        result = repair_code("x = 1", diag)
        assert result == "x = 1"

    def test_fixes_missing_colon(self):
        diag = Diagnosis(
            error_category="syntax",
            root_cause="Syntax error",
            suggestion="Fix syntax",
        )
        source = "def foo()\n    return 1"
        result = repair_code(source, diag)
        assert "def foo():" in result

    def test_fixes_name_error_variable(self):
        diag = Diagnosis(
            error_category="reference",
            root_cause="Variable or function 'x' is used but not defined",
            suggestion="Define 'x'",
        )
        source = "y = x + 1"
        result = repair_code(source, diag)
        assert "x = None" in result

    def test_fixes_division_by_zero(self):
        diag = Diagnosis(
            error_category="arithmetic",
            root_cause="Division by zero encountered",
            suggestion="Add a check for zero",
        )
        source = "result = a / b"
        result = repair_code(source, diag)
        assert "== 0" in result

    def test_fixes_key_error(self):
        diag = Diagnosis(
            error_category="key",
            root_cause="Dictionary key does not exist",
            suggestion="Use dict.get()",
        )
        source = "v = data['key']"
        result = repair_code(source, diag)
        assert ".get(" in result
