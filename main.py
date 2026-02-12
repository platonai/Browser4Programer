#!/usr/bin/env python3
"""
Main CLI entry point for the Self-Evolving Programming System

Usage:
    python main.py "Your programming task description"
    python main.py --interactive
    python main.py --example
"""
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.orchestrator import SelfEvolvingOrchestrator


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Self-Evolving Programming System - Automated code generation with self-repair",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Write a function to calculate fibonacci numbers"
  python main.py --interactive
  python main.py --example
        """
    )
    
    parser.add_argument(
        'task',
        nargs='?',
        help='Programming task description'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--example',
        action='store_true',
        help='Run an example task'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=5,
        help='Maximum number of repair iterations (default: 5)'
    )
    parser.add_argument(
        '--provider',
        choices=['openai', 'anthropic'],
        default='openai',
        help='LLM provider to use (default: openai)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config.load_from_env()
    config.max_iterations = args.max_iterations
    config.llm_provider = args.provider
    
    # Check for API key
    if config.llm_provider == 'openai' and not config.openai_api_key:
        print("❌ Error: OPENAI_API_KEY not set")
        print("Please set your OpenAI API key in .env file or environment variable")
        print("Copy .env.example to .env and add your API key")
        sys.exit(1)
    elif config.llm_provider == 'anthropic' and not config.anthropic_api_key:
        print("❌ Error: ANTHROPIC_API_KEY not set")
        print("Please set your Anthropic API key in .env file or environment variable")
        sys.exit(1)
    
    # Initialize orchestrator
    orchestrator = SelfEvolvingOrchestrator(config)
    
    # Determine task
    if args.example:
        task = "Write a Python function that calculates the factorial of a number using recursion. Include proper error handling for negative numbers and non-integers."
        print(f"Running example task:\n{task}\n")
    elif args.interactive:
        print("Interactive mode - Enter your programming task:")
        task = input("> ").strip()
        if not task:
            print("No task provided. Exiting.")
            sys.exit(1)
    elif args.task:
        task = args.task
    else:
        parser.print_help()
        sys.exit(1)
    
    # Run the self-evolving system
    try:
        result = orchestrator.run(task)
        
        # Print final result
        print("\n" + "="*60)
        print("FINAL RESULT")
        print("="*60)
        
        if result['success']:
            print("✅ Task completed successfully!")
            print(f"\nIterations needed: {result['iterations']}")
            print(f"\nFinal code saved to: workspace/generated_code_iter_{result['iterations']-1}.py")
            print("\nFinal Output:")
            print("-" * 60)
            print(result['output'])
        else:
            print("❌ Task failed to complete")
            print(f"Error: {result.get('error', 'Unknown error')}")
            print(f"Iterations attempted: {result['iterations']}")
        
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
