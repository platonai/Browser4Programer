"""
Execution Module - Run generated code safely
"""
import subprocess
import sys
import os
from typing import Dict, Any, Tuple
from pathlib import Path


class ExecutionModule:
    """Module for executing generated code"""
    
    def __init__(self, workspace_dir: str = "workspace", timeout: int = 300):
        self.workspace_dir = Path(workspace_dir)
        self.timeout = timeout
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, program: Dict[str, Any], iteration: int = 0) -> Dict[str, Any]:
        """
        Execute the generated code
        
        Args:
            program: Output from ProgrammingModule
            iteration: Current iteration number
            
        Returns:
            Dictionary containing execution results
        """
        code = program['code']
        
        # Save code to file
        code_file = self.workspace_dir / f"generated_code_iter_{iteration}.py"
        with open(code_file, 'w') as f:
            f.write(code)
        
        # Execute the code
        success, output, error = self._run_code(code_file)
        
        return {
            "program": program,
            "code_file": str(code_file),
            "success": success,
            "output": output,
            "error": error,
            "iteration": iteration,
            "status": "executed"
        }
    
    def _run_code(self, code_file: Path) -> Tuple[bool, str, str]:
        """
        Run Python code file and capture output
        
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            result = subprocess.run(
                [sys.executable, str(code_file)],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.workspace_dir
            )
            
            success = result.returncode == 0
            output = result.stdout
            error = result.stderr
            
            return success, output, error
            
        except subprocess.TimeoutExpired:
            return False, "", f"Execution timed out after {self.timeout} seconds"
        except Exception as e:
            return False, "", f"Execution error: {str(e)}"
