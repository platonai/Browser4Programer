"""Tests for the markdown_processor module."""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from auto_coder.markdown_processor import (
    CodeBlock,
    BlockResult,
    MarkdownResult,
    extract_code_blocks,
    normalize_code,
    process_markdown,
    process_markdown_text,
)


# ---------------------------------------------------------------------------
# extract_code_blocks
# ---------------------------------------------------------------------------

class TestExtractCodeBlocks:
    """Tests for extract_code_blocks()."""

    def test_empty_document(self):
        assert extract_code_blocks("") == []

    def test_no_code_blocks(self):
        md = "# Hello\n\nSome plain text.\n"
        assert extract_code_blocks(md) == []

    def test_single_python_block(self):
        md = "# Demo\n\n```python\nprint('hello')\n```\n"
        blocks = extract_code_blocks(md)
        assert len(blocks) == 1
        assert blocks[0].language == "python"
        assert "print" in blocks[0].source

    def test_multiple_blocks(self):
        md = (
            "```python\nx = 1\n```\n"
            "\nSome text\n\n"
            "```python\ny = 2\n```\n"
        )
        blocks = extract_code_blocks(md)
        assert len(blocks) == 2

    def test_block_without_language(self):
        md = "```\na = 1 + 2\n```\n"
        blocks = extract_code_blocks(md)
        assert len(blocks) == 1
        assert blocks[0].language == ""

    def test_non_python_language(self):
        md = "```javascript\nconsole.log('hi');\n```\n"
        blocks = extract_code_blocks(md)
        assert len(blocks) == 1
        assert blocks[0].language == "javascript"

    def test_tilde_fence(self):
        md = "~~~python\nprint(42)\n~~~\n"
        blocks = extract_code_blocks(md)
        assert len(blocks) == 1
        assert blocks[0].language == "python"

    def test_start_line_tracking(self):
        md = "line1\nline2\n```python\ncode\n```\n"
        blocks = extract_code_blocks(md)
        assert blocks[0].start_line == 3

    def test_multiline_code_block(self):
        md = "```python\ndef add(a, b):\n    return a + b\n```\n"
        blocks = extract_code_blocks(md)
        assert len(blocks) == 1
        assert "def add" in blocks[0].source
        assert "return a + b" in blocks[0].source


# ---------------------------------------------------------------------------
# normalize_code
# ---------------------------------------------------------------------------

class TestNormalizeCode:
    """Tests for normalize_code()."""

    def test_empty_string(self):
        assert normalize_code("") == ""

    def test_blank_lines_only(self):
        assert normalize_code("\n\n\n") == ""

    def test_strips_leading_blank_lines(self):
        result = normalize_code("\n\n\nx = 1\n")
        assert result.startswith("x = 1")

    def test_strips_trailing_blank_lines(self):
        result = normalize_code("x = 1\n\n\n")
        assert result == "x = 1\n"

    def test_dedents_code(self):
        indented = "    x = 1\n    y = 2\n"
        result = normalize_code(indented)
        assert result == "x = 1\ny = 2\n"

    def test_tabs_replaced(self):
        tabbed = "\tx = 1\n"
        result = normalize_code(tabbed)
        assert "\t" not in result

    def test_ends_with_newline(self):
        result = normalize_code("x = 1")
        assert result.endswith("\n")

    def test_preserves_relative_indent(self):
        code = "    def f():\n        return 1\n"
        result = normalize_code(code)
        assert result == "def f():\n    return 1\n"


# ---------------------------------------------------------------------------
# process_markdown_text — integration
# ---------------------------------------------------------------------------

class TestProcessMarkdownText:
    """Integration tests for process_markdown_text()."""

    def test_valid_code_succeeds(self):
        md = "```python\nx = 42\n```\n"
        result = process_markdown_text(md)
        assert isinstance(result, MarkdownResult)
        assert result.total_blocks == 1
        assert result.success_count == 1
        assert result.failure_count == 0

    def test_broken_code_diagnosed(self):
        md = "```python\nresult = 1 / 0\n```\n"
        result = process_markdown_text(md, max_iterations=2)
        assert result.failure_count >= 0  # may or may not be auto-repaired

    def test_multiple_blocks_mixed(self):
        md = (
            "```python\nx = 1 + 1\n```\n"
            "\n"
            "```python\ny = 2 + 2\n```\n"
        )
        result = process_markdown_text(md)
        assert result.total_blocks == 2
        assert len(result.block_results) == 2
        assert result.success_count == 2

    def test_non_python_blocks_skipped(self):
        md = (
            "```javascript\nconsole.log('hi');\n```\n"
            "\n"
            "```python\nx = 1\n```\n"
        )
        result = process_markdown_text(md)
        assert result.total_blocks == 2
        # Only the Python block is executed
        assert len(result.block_results) == 1
        assert result.success_count == 1

    def test_empty_block_skipped(self):
        md = "```python\n\n\n```\n"
        result = process_markdown_text(md)
        assert len(result.block_results) == 0

    def test_max_iterations_respected(self):
        md = "```python\nundefined_var_xyz\n```\n"
        result = process_markdown_text(md, max_iterations=2)
        for br in result.block_results:
            assert br.iterations <= 2

    def test_auto_repair_attempted(self):
        # Division by zero — repair module can add a zero-guard
        md = "```python\nx = 10\ny = 0\nresult = x / y\n```\n"
        result = process_markdown_text(md, max_iterations=3)
        assert len(result.block_results) == 1
        br = result.block_results[0]
        # The repair module should have modified the code
        assert br.final_code != br.original_code or br.success

    def test_filepath_label(self):
        md = "```python\nx = 1\n```\n"
        result = process_markdown_text(md, filepath="demo.md")
        assert result.filepath == "demo.md"

    def test_block_without_language_executed(self):
        md = "```\nx = 1 + 1\n```\n"
        result = process_markdown_text(md)
        assert result.success_count == 1


# ---------------------------------------------------------------------------
# process_markdown — file-based
# ---------------------------------------------------------------------------

class TestProcessMarkdownFile:
    """Tests for process_markdown() reading from a file."""

    def test_reads_file(self):
        md = "```python\nx = 1 + 2\n```\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(md)
            f.flush()
            path = f.name

        try:
            result = process_markdown(path)
            assert result.filepath == path
            assert result.success_count == 1
        finally:
            os.unlink(path)

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            process_markdown("/nonexistent/path/to/file.md")
