"""
Design Module - Create solution design
"""
from typing import Dict, Any
from src.llm_client import LLMClient


class DesignModule:
    """Module for designing solutions"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def design(self, understanding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design a solution based on the understanding
        
        Args:
            understanding: Output from UnderstandingModule
            
        Returns:
            Dictionary containing the solution design
        """
        system_prompt = """You are an expert software architect.
Design a clean, maintainable, and efficient solution.
Include:
1. Architecture overview
2. Key functions/classes needed
3. Data structures
4. Algorithm approach
5. Error handling strategy"""

        prompt = f"""Based on this task analysis:

{understanding['analysis']}

Design a solution including:
- Architecture: Overall structure
- Components: Key functions/classes needed
- Data Structures: What data structures to use
- Algorithm: Step-by-step algorithm
- Error Handling: How to handle errors"""

        response = self.llm_client.generate(prompt, system_prompt=system_prompt)
        
        return {
            "understanding": understanding,
            "design": response,
            "status": "designed"
        }
