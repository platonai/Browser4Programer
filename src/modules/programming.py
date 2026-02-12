"""
Programming Module - Generate code from design
"""
from typing import Dict, Any
from src.llm_client import LLMClient


class ProgrammingModule:
    """Module for generating code"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def program(self, design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate code based on the design
        
        Args:
            design: Output from DesignModule
            
        Returns:
            Dictionary containing the generated code
        """
        system_prompt = """You are an expert Python programmer.
Generate clean, efficient, well-documented Python code.
Include:
1. Proper imports
2. Clear function/class definitions
3. Docstrings
4. Error handling
5. Type hints where appropriate

Only output the Python code, nothing else."""

        prompt = f"""Based on this design:

{design['design']}

Generate complete, runnable Python code that implements this design.
Include a main() function that demonstrates the solution.
Make sure the code is production-quality with proper error handling."""

        response = self.llm_client.generate(prompt, system_prompt=system_prompt, temperature=0.3)
        
        # Extract code from markdown blocks if present
        code = self._extract_code(response)
        
        return {
            "design": design,
            "code": code,
            "raw_response": response,
            "status": "programmed"
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
            elif in_code_block:
                code_lines.append(line)
        
        # If we found code in blocks, return it
        if code_lines:
            return '\n'.join(code_lines).strip()
        
        # Otherwise return the whole response (might be pure code)
        return response.strip()
