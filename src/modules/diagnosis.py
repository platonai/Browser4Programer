"""
Diagnosis Module - Analyze execution results
"""
from typing import Dict, Any
from src.llm_client import LLMClient


class DiagnosisModule:
    """Module for diagnosing execution results"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def diagnose(self, execution: Dict[str, Any]) -> Dict[str, Any]:
        """
        Diagnose execution results
        
        Args:
            execution: Output from ExecutionModule
            
        Returns:
            Dictionary containing diagnosis
        """
        success = execution['success']
        output = execution['output']
        error = execution['error']
        code = execution['program']['code']
        
        if success and not error:
            return {
                "execution": execution,
                "diagnosis": "Code executed successfully without errors.",
                "needs_repair": False,
                "status": "diagnosed",
                "issues": []
            }
        
        # Analyze the error
        system_prompt = """You are an expert at diagnosing code issues.
Analyze the error and provide:
1. Root cause of the issue
2. Specific problems in the code
3. What needs to be fixed"""

        prompt = f"""Analyze this code execution:

CODE:
```python
{code}
```

OUTPUT:
{output}

ERROR:
{error}

Provide diagnosis:
- Root Cause: What caused the error
- Issues: Specific problems in the code
- Fix Needed: What needs to be changed"""

        response = self.llm_client.generate(prompt, system_prompt=system_prompt)
        
        return {
            "execution": execution,
            "diagnosis": response,
            "needs_repair": True,
            "status": "diagnosed",
            "error_details": {
                "output": output,
                "error": error
            }
        }
