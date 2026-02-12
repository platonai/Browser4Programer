"""
Configuration Management for the Self-Evolving System
"""
import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv


class Config(BaseModel):
    """System configuration"""
    
    # API Configuration
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4")
    anthropic_api_key: Optional[str] = Field(default=None)
    anthropic_model: str = Field(default="claude-3-sonnet-20240229")
    
    # System Configuration
    max_iterations: int = Field(default=5, description="Maximum number of repair iterations")
    timeout_seconds: int = Field(default=300, description="Timeout for code execution")
    workspace_dir: str = Field(default="workspace", description="Directory for generated code")
    
    # LLM Provider
    llm_provider: str = Field(default="openai", description="LLM provider to use (openai or anthropic)")
    
    class Config:
        extra = "allow"
    
    @classmethod
    def load_from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        load_dotenv()
        
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
            max_iterations=int(os.getenv("MAX_ITERATIONS", "5")),
            timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", "300")),
            workspace_dir=os.getenv("WORKSPACE_DIR", "workspace"),
            llm_provider=os.getenv("LLM_PROVIDER", "openai")
        )


# Global configuration instance
config = Config.load_from_env()
