"""
Test script to validate the Self-Evolving System structure

This script tests that all components are properly set up
without requiring API keys.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.config import Config
        print("  ✓ Config module")
        
        from src.llm_client import LLMClient
        print("  ✓ LLM Client module")
        
        from src.orchestrator import SelfEvolvingOrchestrator
        print("  ✓ Orchestrator module")
        
        from src.modules.understanding import UnderstandingModule
        print("  ✓ Understanding module")
        
        from src.modules.design import DesignModule
        print("  ✓ Design module")
        
        from src.modules.programming import ProgrammingModule
        print("  ✓ Programming module")
        
        from src.modules.execution import ExecutionModule
        print("  ✓ Execution module")
        
        from src.modules.diagnosis import DiagnosisModule
        print("  ✓ Diagnosis module")
        
        from src.modules.repair import RepairModule
        print("  ✓ Repair module")
        
        print("\n✅ All imports successful!\n")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}\n")
        return False


def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    
    try:
        from src.config import Config
        
        config = Config(
            openai_api_key="test_key",
            max_iterations=3,
            workspace_dir="test_workspace"
        )
        
        assert config.max_iterations == 3
        assert config.workspace_dir == "test_workspace"
        
        print("  ✓ Config creation and access")
        print("\n✅ Configuration tests passed!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Config error: {e}\n")
        return False


def test_execution_module():
    """Test execution module without running code"""
    print("Testing execution module...")
    
    try:
        from src.modules.execution import ExecutionModule
        
        # Create execution module
        exec_module = ExecutionModule(workspace_dir="test_workspace", timeout=10)
        
        # Check workspace creation
        assert exec_module.workspace_dir.exists()
        print("  ✓ Workspace directory created")
        
        # Test code extraction
        test_code = "print('Hello, World!')"
        test_program = {"code": test_code, "design": {}, "status": "test"}
        
        print("  ✓ Execution module initialized")
        print("\n✅ Execution module tests passed!\n")
        
        # Cleanup
        import shutil
        if exec_module.workspace_dir.exists():
            shutil.rmtree(exec_module.workspace_dir)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Execution error: {e}\n")
        return False


def test_programming_module():
    """Test programming module code extraction"""
    print("Testing programming module...")
    
    try:
        from src.modules.programming import ProgrammingModule
        from src.llm_client import LLMClient
        
        # Create mock client (won't actually call API)
        class MockLLMClient:
            def generate(self, prompt, system_prompt=None, temperature=0.7):
                return "```python\nprint('test')\n```"
        
        prog_module = ProgrammingModule(MockLLMClient())
        
        # Test code extraction
        test_response = "```python\nprint('Hello')\n```"
        extracted = prog_module._extract_code(test_response)
        assert extracted == "print('Hello')"
        print("  ✓ Code extraction from markdown blocks")
        
        # Test plain code
        plain_code = "def test():\n    pass"
        extracted = prog_module._extract_code(plain_code)
        assert "def test()" in extracted
        print("  ✓ Code extraction from plain text")
        
        print("\n✅ Programming module tests passed!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Programming module error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_structure():
    """Test directory structure"""
    print("Testing directory structure...")
    
    base_dir = Path(__file__).parent.parent
    
    required_files = [
        "main.py",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "README.md",
        "src/config.py",
        "src/llm_client.py",
        "src/orchestrator.py",
        "src/modules/understanding.py",
        "src/modules/design.py",
        "src/modules/programming.py",
        "src/modules/execution.py",
        "src/modules/diagnosis.py",
        "src/modules/repair.py",
        "examples/demo.py",
        "examples/tasks.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (missing)")
            all_exist = False
    
    if all_exist:
        print("\n✅ All required files present!\n")
    else:
        print("\n⚠️  Some files are missing\n")
    
    return all_exist


def run_all_tests():
    """Run all tests"""
    print("="*70)
    print("SELF-EVOLVING SYSTEM - STRUCTURE TESTS")
    print("="*70)
    print()
    
    results = []
    
    # Run tests
    results.append(("Structure", test_structure()))
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Execution Module", test_execution_module()))
    results.append(("Programming Module", test_programming_module()))
    
    # Summary
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print()
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
    
    print()
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("🎉 All tests passed!")
        print("\nThe Self-Evolving System is properly set up.")
        print("To use it, configure your API key in .env file")
        print()
        return 0
    else:
        print("⚠️  Some tests failed")
        print()
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
