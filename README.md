# Browser4Programer

An AI programmer initially works for Browser4.

## Auto-Coder: Self-Evolving Programming Automation

**auto_coder** is a Python automation pipeline that performs a closed-loop cycle of:

1. **Understanding** – Parse and analyze a programming task description
2. **Design** – Create a solution blueprint (parameters, algorithm steps)
3. **Programming** – Generate executable Python code
4. **Execution** – Run the generated code in a sandboxed namespace
5. **Diagnosis** – Identify root causes when execution fails
6. **Automatic Repair** – Patch the code and iterate until the task succeeds

### Quick Start

```bash
# Run a task with a test assertion
python -m auto_coder "Write a function factorial that computes the factorial of n" \
    --test "factorial(5)"

# Verbose output
python -m auto_coder -v "Write a function add that adds two numbers" \
    --test "add(2, 3)"
```

### Markdown Processing

Process code blocks inside a Markdown document through an automated
**Extract → Normalize → Execute → Diagnose → Auto-fix** loop:

```bash
python -m auto_coder --markdown examples/demo.md
python -m auto_coder --md examples/demo.md -v --max-iterations 3
```

Each fenced Python code block is extracted, cleaned up, executed in a
sandbox, and — if execution fails — automatically diagnosed and repaired.
The loop repeats until the block succeeds or the iteration limit is
reached.

### Agent Mode

Manage multiple tasks with dependencies and priorities through an
intelligent agent:

```bash
python -m auto_coder --agent tasks.json
```

The JSON file should contain an array of task objects:

```json
[
    {
        "task_id": "add",
        "description": "Write a function add that adds two numbers",
        "test_call": "add(2, 3)",
        "priority": "high"
    },
    {
        "task_id": "sort",
        "description": "Write a function sort_list that sorts a list",
        "test_call": "sort_list([3, 1, 2])",
        "dependencies": ["add"]
    }
]
```

The agent resolves dependencies, orders tasks by priority, and skips
downstream tasks when a dependency fails.

### Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

### Project Structure

```
src/auto_coder/
├── __init__.py            # Package metadata
├── __main__.py            # CLI entry point
├── understanding.py       # Stage 1: task parsing
├── design.py              # Stage 2: solution design
├── programming.py         # Stage 3: code generation
├── execution.py           # Stage 4: code execution
├── diagnosis.py           # Stage 5: error analysis
├── repair.py              # Stage 6: automatic repair
├── pipeline.py            # Orchestrator (closed loop)
├── markdown_processor.py  # Markdown code-block processing loop
└── agent.py               # Intelligent agent for task flow management
```
