"""
Self-Evolving Orchestrator - Main closed loop controller

This orchestrator manages the complete cycle:
understanding → design → programming → execution → diagnosis → automatic repair
"""
from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from src.config import Config
from src.llm_client import LLMClient
from src.modules.understanding import UnderstandingModule
from src.modules.design import DesignModule
from src.modules.programming import ProgrammingModule
from src.modules.execution import ExecutionModule
from src.modules.diagnosis import DiagnosisModule
from src.modules.repair import RepairModule


class SelfEvolvingOrchestrator:
    """
    Main orchestrator for the self-evolving closed loop system
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the orchestrator with configuration"""
        self.config = config or Config.load_from_env()
        
        # Initialize LLM client
        self.llm_client = LLMClient(
            provider=self.config.llm_provider,
            api_key=self.config.openai_api_key if self.config.llm_provider == "openai" else self.config.anthropic_api_key,
            model=self.config.openai_model if self.config.llm_provider == "openai" else self.config.anthropic_model
        )
        
        # Initialize modules
        self.understanding = UnderstandingModule(self.llm_client)
        self.design = DesignModule(self.llm_client)
        self.programming = ProgrammingModule(self.llm_client)
        self.execution = ExecutionModule(
            workspace_dir=self.config.workspace_dir,
            timeout=self.config.timeout_seconds
        )
        self.diagnosis = DiagnosisModule(self.llm_client)
        self.repair = RepairModule(self.llm_client)
        
        # State tracking
        self.history = []
    
    def run(self, task_description: str, save_history: bool = True) -> Dict[str, Any]:
        """
        Run the complete self-evolving closed loop
        
        Args:
            task_description: Natural language description of the programming task
            save_history: Whether to save execution history to file
            
        Returns:
            Dictionary containing the final result and execution history
        """
        print(f"\n{'='*60}")
        print(f"SELF-EVOLVING PROGRAMMING SYSTEM")
        print(f"{'='*60}\n")
        
        # Phase 1: Understanding
        print("📖 Phase 1: UNDERSTANDING the task...")
        understanding = self.understanding.understand(task_description)
        self.history.append(("understanding", understanding))
        print("✓ Task understood\n")
        
        # Phase 2: Design
        print("🎨 Phase 2: DESIGNING the solution...")
        design = self.design.design(understanding)
        self.history.append(("design", design))
        print("✓ Solution designed\n")
        
        # Phase 3: Programming
        print("💻 Phase 3: PROGRAMMING the solution...")
        program = self.programming.program(design)
        self.history.append(("programming", program))
        print("✓ Code generated\n")
        
        # Closed loop: Execute → Diagnose → Repair (if needed)
        iteration = 0
        max_iterations = self.config.max_iterations
        
        while iteration < max_iterations:
            print(f"🔄 Iteration {iteration + 1}/{max_iterations}")
            
            # Phase 4: Execution
            print("  ⚙️  Phase 4: EXECUTING the code...")
            execution = self.execution.execute(program, iteration)
            self.history.append(("execution", execution))
            
            if execution['success']:
                print(f"  ✓ Execution successful!")
                print(f"\n  OUTPUT:\n{execution['output']}")
            else:
                print(f"  ✗ Execution failed")
                print(f"  ERROR: {execution['error']}")
            
            # Phase 5: Diagnosis
            print("  🔍 Phase 5: DIAGNOSING results...")
            diagnosis = self.diagnosis.diagnose(execution)
            self.history.append(("diagnosis", diagnosis))
            
            if not diagnosis['needs_repair']:
                print("  ✓ No issues found - SUCCESS!\n")
                result = {
                    "success": True,
                    "final_code": program['code'],
                    "output": execution['output'],
                    "iterations": iteration + 1,
                    "history": self.history
                }
                break
            
            print(f"  ⚠️  Issues detected, repair needed\n")
            
            # Phase 6: Automatic Repair
            print("  🔧 Phase 6: REPAIRING the code...")
            repair = self.repair.repair(diagnosis)
            self.history.append(("repair", repair))
            
            # Update program with repaired code for next iteration
            program = {
                "code": repair['code'],
                "design": program['design'],
                "status": "repaired"
            }
            
            print("  ✓ Code repaired, retrying...\n")
            
            iteration += 1
        else:
            # Max iterations reached without success
            print(f"⚠️  Maximum iterations ({max_iterations}) reached without success\n")
            result = {
                "success": False,
                "final_code": program['code'],
                "error": "Maximum repair iterations exceeded",
                "iterations": iteration,
                "history": self.history
            }
        
        # Save history if requested
        if save_history:
            self._save_history(task_description, result)
        
        print(f"{'='*60}")
        print(f"PROCESS COMPLETE")
        print(f"{'='*60}\n")
        
        return result
    
    def _save_history(self, task_description: str, result: Dict[str, Any]):
        """Save execution history to file"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_dir / f"history_{timestamp}.json"
        
        history_data = {
            "task": task_description,
            "result": {
                "success": result['success'],
                "iterations": result['iterations'],
                "final_code": result.get('final_code', ''),
                "output": result.get('output', ''),
                "error": result.get('error', '')
            },
            "timestamp": timestamp
        }
        
        with open(filename, 'w') as f:
            json.dump(history_data, f, indent=2)
        
        print(f"💾 History saved to: {filename}")
