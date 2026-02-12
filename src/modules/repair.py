"""
Automatic Repair Module - Fix code issues automatically
"""
from typing import Dict, Any
from src.llm_client import LLMClient


class RepairModule:
    """Module for automatically repairing code"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def repair(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Repair code based on diagnosis
        
        Args:
            diagnosis: Output from DiagnosisModule
            
        Returns:
            Dictionary containing repaired code
        """
        if not diagnosis['needs_repair']:
            return {
                "diagnosis": diagnosis,
                "code": diagnosis['execution']['program']['code'],
                "repaired": False,
                "status": "no_repair_needed"
            }
        
        code = diagnosis['execution']['program']['code']
        diagnosis_text = diagnosis['diagnosis']
        error = diagnosis['error_details']['error']
        
        system_prompt = """You are an expert at fixing code issues.
Generate corrected Python code that fixes the identified issues.
Maintain the same functionality while fixing the errors.
Only output the corrected Python code, nothing else."""

        prompt = f"""Fix this code based on the diagnosis:

ORIGINAL CODE:
```python
{code}
```

ERROR:
{error}

DIAGNOSIS:
{diagnosis_text}

Generate the corrected Python code that fixes these issues while maintaining the same functionality."""

        response = self.llm_client.generate(prompt, system_prompt=system_prompt, temperature=0.3)
        
        # Extract code from markdown blocks if present
        repaired_code = self._extract_code(response)
        
        return {
            "diagnosis": diagnosis,
            "code": repaired_code,
            "raw_response": response,
            "repaired": True,
            "status": "repaired"
        }
    
    def _extract_code(self, response: str) -> str:
        """Extract Python code from response, handling markdown code blocks"""
        lines = response.strip().split('\n')
        code_lines = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```python'):
                in_code_block = True
                continue
            elif line.strip().startswith('```'):
                in_code_block = False
                continue
            elif in_code_block or (not line.strip().startswith('```') and code_lines):
                code_lines.append(line)
        
        # If we found code in blocks, return it
        if code_lines:
            return '\n'.join(code_lines).strip()
        
        # Otherwise return the whole response (might be pure code)
        return response.strip()
