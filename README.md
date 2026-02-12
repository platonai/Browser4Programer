# Browser4Programer

A Self-Evolving Programming Automation System that performs:
**understanding → design → programming → execution → diagnosis → automatic repair**

This system creates a sustainable and iterative self-evolving closed loop for automated programming tasks.

## 🌟 Features

- **Intelligent Understanding**: Analyzes and structures programming tasks using AI
- **Smart Design**: Creates architectural designs for solutions
- **Code Generation**: Generates production-quality Python code
- **Safe Execution**: Runs generated code in isolated workspace
- **Automatic Diagnosis**: Identifies issues and errors
- **Self-Repair**: Automatically fixes code issues and retries
- **Iterative Loop**: Continues until success or max iterations reached

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key (or Anthropic API key)

### Installation

```bash
# Clone the repository
git clone https://github.com/platonai/Browser4Programer.git
cd Browser4Programer

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your API key
```

### Usage

```bash
# Run with a task description
python main.py "Write a function to calculate fibonacci numbers"

# Run example task
python main.py --example

# Interactive mode
python main.py --interactive

# Customize settings
python main.py "Your task" --max-iterations 10 --provider openai
```

## 📖 How It Works

The system implements a complete self-evolving closed loop:

```
┌─────────────────────────────────────────────────────────┐
│                   CLOSED LOOP CYCLE                      │
└─────────────────────────────────────────────────────────┘

1. 📖 UNDERSTANDING
   ↓ Parse and analyze the programming task
   
2. 🎨 DESIGN
   ↓ Create solution architecture and design
   
3. 💻 PROGRAMMING
   ↓ Generate Python code from design
   
4. ⚙️  EXECUTION
   ↓ Run the generated code safely
   
5. 🔍 DIAGNOSIS
   ↓ Analyze results and identify issues
   
6. 🔧 REPAIR (if needed)
   ↓ Automatically fix issues
   └─→ Loop back to EXECUTION (steps 4-6 repeat until success)
```

## 🏗️ Architecture

```
Browser4Programer/
├── src/
│   ├── config.py              # Configuration management
│   ├── llm_client.py          # LLM provider interface
│   ├── orchestrator.py        # Main closed loop orchestrator
│   └── modules/
│       ├── understanding.py   # Task understanding
│       ├── design.py          # Solution design
│       ├── programming.py     # Code generation
│       ├── execution.py       # Safe code execution
│       ├── diagnosis.py       # Result analysis
│       └── repair.py          # Automatic repair
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
└── .env.example              # Configuration template
```

## 🔧 Configuration

Edit `.env` file to configure:

```bash
# OpenAI Configuration (default)
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4

# Or use Anthropic
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# System Settings
MAX_ITERATIONS=5        # Maximum repair attempts
TIMEOUT_SECONDS=300     # Execution timeout
WORKSPACE_DIR=workspace # Code execution directory
```

## 📊 Example Output

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
  Fibonacci(10) = 55
  
  🔍 Phase 5: DIAGNOSING results...
  ✓ No issues found - SUCCESS!

============================================================
PROCESS COMPLETE
============================================================
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

An AI programmer initially works for Browser4.
