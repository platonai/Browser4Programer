"""
Demo script to showcase the Self-Evolving Programming System

This script demonstrates the system without requiring API keys
by showing the workflow and architecture.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def demo_workflow():
    """Demonstrate the system workflow"""
    print("="*70)
    print("SELF-EVOLVING PROGRAMMING SYSTEM - DEMO")
    print("="*70)
    print()
    
    print("This system implements a complete self-evolving closed loop:")
    print()
    
    stages = [
        ("📖 UNDERSTANDING", "Analyzes and structures the programming task using AI"),
        ("🎨 DESIGN", "Creates architectural design and solution approach"),
        ("💻 PROGRAMMING", "Generates production-quality Python code"),
        ("⚙️  EXECUTION", "Runs the code in an isolated workspace"),
        ("🔍 DIAGNOSIS", "Analyzes results and identifies any issues"),
        ("🔧 REPAIR", "Automatically fixes issues and loops back to execution"),
    ]
    
    for stage, description in stages:
        print(f"{stage}")
        print(f"   {description}")
        print()
    
    print("The system continues the EXECUTION → DIAGNOSIS → REPAIR loop")
    print("until the code works successfully or max iterations is reached.")
    print()
    
    print("="*70)
    print("KEY FEATURES")
    print("="*70)
    print()
    
    features = [
        "✓ Fully automated code generation",
        "✓ Self-diagnosing capabilities",
        "✓ Automatic error repair",
        "✓ Iterative improvement",
        "✓ Safe isolated execution",
        "✓ Complete execution history",
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print()
    print("="*70)
    print("EXAMPLE USAGE")
    print("="*70)
    print()
    print('  python main.py "Write a function to calculate fibonacci numbers"')
    print('  python main.py --example')
    print('  python main.py --interactive')
    print()
    print("For full functionality, configure your API key in .env file")
    print("See README.md for detailed instructions")
    print()


def demo_architecture():
    """Show system architecture"""
    print("\n" + "="*70)
    print("SYSTEM ARCHITECTURE")
    print("="*70)
    print("""
Browser4Programer/
├── src/
│   ├── config.py              # Configuration management
│   ├── llm_client.py          # LLM provider interface (OpenAI/Anthropic)
│   ├── orchestrator.py        # Main closed loop orchestrator
│   └── modules/
│       ├── understanding.py   # Phase 1: Task understanding
│       ├── design.py          # Phase 2: Solution design
│       ├── programming.py     # Phase 3: Code generation
│       ├── execution.py       # Phase 4: Safe code execution
│       ├── diagnosis.py       # Phase 5: Result analysis
│       └── repair.py          # Phase 6: Automatic repair
├── main.py                    # CLI entry point
├── examples/                  # Example tasks
├── workspace/                 # Code execution workspace
└── output/                    # Execution history logs
    """)


if __name__ == "__main__":
    demo_workflow()
    demo_architecture()
