"""
Self-Evolving Programming Automation System

A Python automation program that performs:
understanding → design → programming → execution → diagnosis → automatic repair
forming a sustainable and iterative self-evolving closed loop.

Main Components:
- config: Configuration management
- llm_client: LLM provider interface
- orchestrator: Main closed loop orchestrator
- modules: Core phase implementations

Example:
    from src.orchestrator import SelfEvolvingOrchestrator
    
    orchestrator = SelfEvolvingOrchestrator()
    result = orchestrator.run("Write a function to calculate fibonacci")
"""

__version__ = "1.0.0"
