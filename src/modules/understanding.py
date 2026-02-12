"""
Understanding Module - Parse and analyze programming tasks
"""
from typing import Dict, Any
from src.llm_client import LLMClient


class UnderstandingModule:
    """Module for understanding programming tasks"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def understand(self, task_description: str) -> Dict[str, Any]:
        """
        Understand the programming task and extract key information
        
        Args:
            task_description: Natural language description of the task
            
        Returns:
            Dictionary containing structured understanding of the task
        """
        system_prompt = """You are an expert at understanding programming tasks.
Analyze the task and extract:
1. Main objective
2. Input requirements
3. Expected output
4. Constraints
5. Key steps needed

Respond in a structured format."""

        prompt = f"""Analyze this programming task:

{task_description}

Provide a structured analysis with:
- Objective: What needs to be accomplished
- Inputs: What inputs are required
- Outputs: What should be produced
- Constraints: Any limitations or requirements
- Approach: High-level approach to solve it"""

        response = self.llm_client.generate(prompt, system_prompt=system_prompt)
        
        return {
            "task_description": task_description,
            "analysis": response,
            "status": "understood"
        }
