"""
LLM Client for interacting with Language Models
"""
from typing import Optional
import os


class LLMClient:
    """Client for interacting with LLM providers"""
    
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.client = None
        
        if provider == "openai":
            try:
                import openai
                self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
                self.model = model or os.getenv("OPENAI_MODEL", "gpt-4")
            except ImportError:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
        elif provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
                self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
            except ImportError:
                raise ImportError("Anthropic package not installed. Run: pip install anthropic")
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generate text using the LLM"""
        if self.provider == "openai":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        
        elif self.provider == "anthropic":
            kwargs = {"model": self.model, "max_tokens": 4096, "temperature": temperature}
            if system_prompt:
                kwargs["system"] = system_prompt
            kwargs["messages"] = [{"role": "user", "content": prompt}]
            
            response = self.client.messages.create(**kwargs)
            return response.content[0].text
        
        raise ValueError(f"Unsupported provider: {self.provider}")
