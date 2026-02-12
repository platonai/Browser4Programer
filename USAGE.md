# Usage Guide

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/platonai/Browser4Programer.git
cd Browser4Programer

# Run setup script (Unix/Linux/Mac)
./setup.sh

# Or install manually
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configuration

Edit the `.env` file and add your API key:

```bash
# For OpenAI (recommended)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4

# Or for Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# System configuration
MAX_ITERATIONS=5
TIMEOUT_SECONDS=300
```

### 3. Usage Examples

#### Example 1: Run a predefined example

```bash
python main.py --example
```

This runs a factorial calculation example.

#### Example 2: Specify your own task

```bash
python main.py "Write a function to check if a string is a palindrome"
```

#### Example 3: Interactive mode

```bash
python main.py --interactive
```

Then enter your task when prompted.

#### Example 4: Custom settings

```bash
python main.py "Your task" --max-iterations 10 --provider openai
```

## Understanding the Output

The system will show you each phase:

1. **📖 UNDERSTANDING**: Analyzing your task
2. **🎨 DESIGN**: Creating the solution architecture
3. **💻 PROGRAMMING**: Generating the code
4. **⚙️  EXECUTION**: Running the code
5. **🔍 DIAGNOSIS**: Checking for issues
6. **🔧 REPAIR**: Fixing any problems (if needed)

The EXECUTION → DIAGNOSIS → REPAIR cycle repeats until success.

## Example Output

```
============================================================
SELF-EVOLVING PROGRAMMING SYSTEM
============================================================

📖 Phase 1: UNDERSTANDING the task...
✓ Task understood

🎨 Phase 2: DESIGNING the solution...
✓ Solution designed

💻 Phase 3: PROGRAMMING the solution...
✓ Code generated

🔄 Iteration 1/5
  ⚙️  Phase 4: EXECUTING the code...
  ✓ Execution successful!
  
  OUTPUT:
  factorial(5) = 120
  
  🔍 Phase 5: DIAGNOSING results...
  ✓ No issues found - SUCCESS!

============================================================
PROCESS COMPLETE
============================================================

✅ Task completed successfully!
Iterations needed: 1
Final code saved to: workspace/generated_code_iter_0.py
```

## Output Files

- **workspace/**: Contains generated code files
- **output/**: Contains execution history in JSON format

## Advanced Usage

### Using Different LLM Providers

```bash
# Use OpenAI (default)
python main.py "Your task" --provider openai

# Use Anthropic Claude
python main.py "Your task" --provider anthropic
```

### Adjusting Iteration Limits

```bash
# Allow more repair attempts
python main.py "Your task" --max-iterations 10
```

### Running Without API Keys (Demo Mode)

```bash
# See system architecture and workflow
python examples/demo.py

# List available example tasks
python examples/tasks.py
```

## Task Examples

### Simple Tasks
- "Write a function to check if a number is prime"
- "Create a function to reverse a string"
- "Find the largest element in a list"

### Intermediate Tasks
- "Write a recursive factorial function with error handling"
- "Implement a stack data structure with push, pop, and peek"
- "Create a bubble sort implementation"

### Complex Tasks
- "Build a calculator with error handling"
- "Validate email addresses with regex"
- "Count word frequencies in a text file"

## Troubleshooting

### API Key Issues

If you see "OPENAI_API_KEY not set":
1. Make sure you created the `.env` file
2. Check that your API key is correct
3. Try running `source .env` (on Unix/Linux/Mac)

### Import Errors

If you see module import errors:
```bash
pip install -r requirements.txt
```

### Execution Timeouts

If code execution times out:
- Increase `TIMEOUT_SECONDS` in `.env`
- Or use: `--max-iterations` to allow more attempts

## Running Tests

```bash
# Test system structure
python tests/test_structure.py
```

## System Architecture

The system consists of 6 main modules in a closed loop:

```
┌─────────────┐
│Understanding├──┐
└─────────────┘  │
                 ▼
┌─────────────┐
│   Design    │
└─────────────┘
       │
       ▼
┌─────────────┐
│Programming  │
└─────────────┘
       │
       ▼
┌─────────────┐      ┌─────────────┐
│ Execution   │◄─────┤   Repair    │
└─────────────┘      └─────────────┘
       │                     ▲
       ▼                     │
┌─────────────┐              │
│ Diagnosis   ├──────────────┘
└─────────────┘
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on GitHub.

## Support

For issues or questions:
- Open an issue on GitHub
- Check the README.md for more information
