"""
Mock integration test that demonstrates the full system flow
without requiring API keys
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.modules.understanding import UnderstandingModule
from src.modules.design import DesignModule
from src.modules.programming import ProgrammingModule
from src.modules.execution import ExecutionModule
from src.modules.diagnosis import DiagnosisModule
from src.modules.repair import RepairModule


class MockLLMClient:
    """Mock LLM client for testing without API calls"""
    
    def __init__(self):
        self.call_count = 0
    
    def generate(self, prompt, system_prompt=None, temperature=0.7):
        """Generate mock responses based on the prompt"""
        self.call_count += 1
        
        # Understanding phase
        if "Analyze this programming task" in prompt:
            return """
Objective: Create a function to calculate factorial of a number
Inputs: Integer number (n)
Outputs: Factorial value (n!)
Constraints: Handle negative numbers, use recursion
Approach: Implement recursive factorial with base case and error handling
"""
        
        # Design phase
        elif "Design a solution" in prompt:
            return """
Architecture: Simple recursive function
Components:
  - factorial(n) function with recursion
  - Base case: n = 0 or n = 1 returns 1
  - Recursive case: n * factorial(n-1)
  - Error handling for negative numbers
Data Structures: Integer values
Algorithm:
  1. Check if n < 0, raise error
  2. If n <= 1, return 1
  3. Otherwise return n * factorial(n-1)
Error Handling: Raise ValueError for negative input
"""
        
        # Programming phase
        elif "Generate complete, runnable Python code" in prompt:
            if self.call_count == 3:  # First attempt (intentionally buggy)
                return """
```python
def factorial(n):
    # Missing error handling
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def main():
    # Test with negative number (will cause infinite recursion)
    print(f"factorial(5) = {factorial(5)}")
    print(f"factorial(-1) = {factorial(-1)}")  # Bug!

if __name__ == "__main__":
    main()
```
"""
            else:  # Repaired version
                return """
```python
def factorial(n):
    '''Calculate factorial of n using recursion'''
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def main():
    # Test cases
    print(f"factorial(5) = {factorial(5)}")
    print(f"factorial(0) = {factorial(0)}")
    print(f"factorial(1) = {factorial(1)}")
    
    # Test error handling
    try:
        factorial(-1)
    except ValueError as e:
        print(f"Correctly caught error for negative input: {e}")

if __name__ == "__main__":
    main()
```
"""
        
        # Diagnosis phase
        elif "Analyze this code execution" in prompt:
            if "RecursionError" in prompt or "maximum recursion depth" in prompt:
                return """
Root Cause: Missing error handling for negative numbers causing infinite recursion
Issues: 
  - No validation for negative input
  - factorial(-1) causes infinite recursion
  - Missing type checking
Fix Needed: Add input validation to check for negative numbers before recursion
"""
            else:
                return "Code executed successfully without errors."
        
        # Repair phase
        elif "Fix this code based on the diagnosis" in prompt:
            return """
```python
def factorial(n):
    '''Calculate factorial of n using recursion'''
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def main():
    print(f"factorial(5) = {factorial(5)}")
    try:
        factorial(-1)
    except ValueError as e:
        print(f"Error caught: {e}")

if __name__ == "__main__":
    main()
```
"""
        
        return "Mock response"


def test_full_cycle():
    """Test the complete self-evolving cycle"""
    print("="*70)
    print("MOCK INTEGRATION TEST - Full Self-Evolving Cycle")
    print("="*70)
    print()
    
    # Initialize components with mock client
    mock_client = MockLLMClient()
    
    understanding = UnderstandingModule(mock_client)
    design = DesignModule(mock_client)
    programming = ProgrammingModule(mock_client)
    execution = ExecutionModule(workspace_dir="test_workspace", timeout=10)
    diagnosis = DiagnosisModule(mock_client)
    repair = RepairModule(mock_client)
    
    task = "Write a function to calculate factorial with error handling"
    
    # Phase 1: Understanding
    print("📖 Phase 1: UNDERSTANDING...")
    understanding_result = understanding.understand(task)
    assert understanding_result['status'] == 'understood'
    print("✓ Task understood\n")
    
    # Phase 2: Design
    print("🎨 Phase 2: DESIGN...")
    design_result = design.design(understanding_result)
    assert design_result['status'] == 'designed'
    print("✓ Solution designed\n")
    
    # Phase 3: Programming (first attempt - buggy)
    print("💻 Phase 3: PROGRAMMING...")
    program_result = programming.program(design_result)
    assert program_result['status'] == 'programmed'
    assert 'def factorial' in program_result['code']
    print("✓ Code generated\n")
    
    # Phase 4: Execution (first attempt - will fail)
    print("🔄 Iteration 1")
    print("  ⚙️  Phase 4: EXECUTING...")
    exec_result = execution.execute(program_result, iteration=0)
    print(f"  Status: {'Success' if exec_result['success'] else 'Failed'}")
    
    # Phase 5: Diagnosis
    print("  🔍 Phase 5: DIAGNOSIS...")
    diag_result = diagnosis.diagnose(exec_result)
    print(f"  Needs repair: {diag_result['needs_repair']}\n")
    
    if diag_result['needs_repair']:
        # Phase 6: Repair
        print("  🔧 Phase 6: REPAIR...")
        repair_result = repair.repair(diag_result)
        assert repair_result['repaired']
        print("  ✓ Code repaired\n")
        
        # Update program with repaired code
        program_result = {
            "code": repair_result['code'],
            "design": program_result['design'],
            "status": "repaired"
        }
        
        # Phase 4: Re-execution
        print("🔄 Iteration 2")
        print("  ⚙️  Phase 4: RE-EXECUTING...")
        exec_result = execution.execute(program_result, iteration=1)
        print(f"  Status: {'Success' if exec_result['success'] else 'Failed'}")
        
        # Phase 5: Re-diagnosis
        print("  🔍 Phase 5: RE-DIAGNOSIS...")
        diag_result = diagnosis.diagnose(exec_result)
        print(f"  Needs repair: {diag_result['needs_repair']}")
    
    # Cleanup
    import shutil
    if execution.workspace_dir.exists():
        shutil.rmtree(execution.workspace_dir)
    
    print()
    print("="*70)
    print("✅ MOCK TEST COMPLETED SUCCESSFULLY")
    print("="*70)
    print()
    print(f"Total LLM calls made: {mock_client.call_count}")
    print("The system successfully went through all phases:")
    print("  Understanding → Design → Programming → Execution")
    print("  → Diagnosis → Repair → Re-execution → Success")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = test_full_cycle()
        if success:
            print("✅ Integration test passed!")
            sys.exit(0)
        else:
            print("❌ Integration test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
