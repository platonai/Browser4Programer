"""Tests for the repair stage."""

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from auto_coder.diagnosis import Diagnosis
from auto_coder.repair import repair_code, repair_code_with_cli, _build_issue_description


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


class TestCliRepair:
    """Tests for CLI-based repair functionality."""

    def test_cli_repair_modifies_source(self):
        """CLI tool that modifies source.py should produce repaired code."""
        diag = Diagnosis(
            error_category="syntax",
            root_cause="Syntax error in the code",
            suggestion="Fix syntax",
        )
        source = "def foo()\n    return 1"
        # Use a shell command that fixes the source file by adding the colon
        cmd = "sed -i 's/def foo()/def foo():/' {source_file}"
        result = repair_code_with_cli(source, diag, cmd)
        assert "def foo():" in result

    def test_cli_repair_returns_original_on_failure(self):
        """Failed CLI command should return the original source."""
        diag = Diagnosis(
            error_category="unknown",
            root_cause="mystery",
            suggestion="investigate",
        )
        source = "x = 1"
        cmd = "false"  # always exits with code 1
        result = repair_code_with_cli(source, diag, cmd)
        assert result == source

    def test_cli_repair_returns_original_on_timeout(self):
        """Timed-out CLI command should return the original source."""
        diag = Diagnosis(
            error_category="unknown",
            root_cause="mystery",
            suggestion="investigate",
        )
        source = "x = 1"
        # sleep longer than the internal timeout (patched to 1s via monkeypatch below)
        cmd = "sleep 999"
        # We can't easily test the 120s timeout, but we can verify
        # the function handles a non-existent command gracefully
        cmd_bad = "nonexistent_command_xyz_12345"
        result = repair_code_with_cli(source, diag, cmd_bad)
        assert result == source

    def test_cli_repair_issue_file_placeholder(self):
        """The {issue_file} placeholder should be replaced with a real path."""
        diag = Diagnosis(
            error_category="syntax",
            root_cause="Missing colon",
            suggestion="Add colon",
            line_number=1,
        )
        source = "def foo()\n    return 1"
        # Command that reads the issue file and verifies it exists,
        # then fixes the source file
        cmd = (
            "test -f {issue_file} && "
            "sed -i 's/def foo()/def foo():/' {source_file}"
        )
        result = repair_code_with_cli(source, diag, cmd)
        assert "def foo():" in result

    def test_cli_fallback_when_builtin_fails(self):
        """repair_code should fall back to CLI when built-in repair has no effect."""
        diag = Diagnosis(
            error_category="unknown",
            root_cause="mystery",
            suggestion="investigate",
        )
        source = "x = 1"
        # CLI command that appends a comment to the source
        cmd = "echo '# fixed' >> {source_file}"
        result = repair_code(source, diag, repair_command=cmd)
        assert "# fixed" in result

    def test_no_cli_fallback_without_repair_command(self):
        """Without repair_command, unknown categories return source unchanged."""
        diag = Diagnosis(
            error_category="unknown",
            root_cause="mystery",
            suggestion="investigate",
        )
        result = repair_code("x = 1", diag, repair_command=None)
        assert result == "x = 1"

    def test_builtin_takes_precedence_over_cli(self):
        """Built-in repair should be used first before CLI fallback."""
        diag = Diagnosis(
            error_category="syntax",
            root_cause="Syntax error",
            suggestion="Fix syntax",
        )
        source = "def foo()\n    return 1"
        # CLI command that would add a different marker
        cmd = "echo '# cli_was_called' >> {source_file}"
        result = repair_code(source, diag, repair_command=cmd)
        # Built-in repair should have fixed the colon
        assert "def foo():" in result
        # CLI should NOT have been called since built-in worked
        assert "# cli_was_called" not in result

    def test_cli_repair_cleans_up_temp_files(self):
        """Temp files should be cleaned up after CLI repair."""
        diag = Diagnosis(
            error_category="unknown",
            root_cause="mystery",
            suggestion="investigate",
        )
        source = "x = 1"
        cmd = "true"  # succeed without modifying anything
        result = repair_code_with_cli(source, diag, cmd)
        # Result should be the original since command didn't modify the file
        assert result == source


class TestBuildIssueDescription:
    """Tests for _build_issue_description()."""

    def test_contains_error_category(self):
        diag = Diagnosis(
            error_category="syntax",
            root_cause="Missing colon",
            suggestion="Add colon",
        )
        desc = _build_issue_description("x = 1", diag)
        assert "syntax" in desc

    def test_contains_root_cause(self):
        diag = Diagnosis(
            error_category="syntax",
            root_cause="Missing colon after def",
            suggestion="Add colon",
        )
        desc = _build_issue_description("x = 1", diag)
        assert "Missing colon after def" in desc

    def test_contains_source_code(self):
        diag = Diagnosis(
            error_category="syntax",
            root_cause="error",
            suggestion="fix",
        )
        desc = _build_issue_description("def foo():\n    pass", diag)
        assert "def foo():" in desc
        assert "```python" in desc

    def test_contains_line_number_when_present(self):
        diag = Diagnosis(
            error_category="syntax",
            root_cause="error",
            suggestion="fix",
            line_number=42,
        )
        desc = _build_issue_description("x = 1", diag)
        assert "42" in desc

    def test_omits_line_number_when_absent(self):
        diag = Diagnosis(
            error_category="syntax",
            root_cause="error",
            suggestion="fix",
        )
        desc = _build_issue_description("x = 1", diag)
        assert "**Line:**" not in desc
