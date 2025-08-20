"""
Agent Coordinator for Asset Management System
Organizes and coordinates different a2a agents for optimal workflow
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class AgentType(Enum):
    """Types of agents in the system."""
    BILLING_ANALYZER = "billing_analyzer"
    CATEGORY_MANAGER = "category_manager" 
    REPORT_GENERATOR = "report_generator"
    DATA_VALIDATOR = "data_validator"
    NOTIFICATION_AGENT = "notification_agent"

@dataclass
class AgentTask:
    """Represents a task for an agent."""
    agent_type: AgentType
    task_id: str
    description: str
    input_data: Dict[str, Any]
    dependencies: List[str] = None
    priority: int = 1  # 1-5, where 1 is highest priority
    status: str = "pending"  # pending, running, completed, failed
    result: Dict[str, Any] = None
    created_at: datetime = None
    completed_at: datetime = None

class AgentCoordinator:
    """Coordinates multiple agents for asset management workflows."""
    
    def __init__(self):
        self.agents = {
            AgentType.BILLING_ANALYZER: BillingAnalyzerAgent(),
            AgentType.CATEGORY_MANAGER: CategoryManagerAgent(),
            AgentType.REPORT_GENERATOR: ReportGeneratorAgent(),
            AgentType.DATA_VALIDATOR: DataValidatorAgent(),
            AgentType.NOTIFICATION_AGENT: NotificationAgent()
        }
        self.task_queue = []
        self.completed_tasks = []
    
    def create_workflow(self, workflow_type: str) -> List[AgentTask]:
        """Create a workflow with multiple coordinated tasks."""
        workflows = {
            "monthly_analysis": self._create_monthly_analysis_workflow,
            "category_review": self._create_category_review_workflow,
            "data_validation": self._create_data_validation_workflow,
            "comprehensive_report": self._create_comprehensive_report_workflow
        }
        
        if workflow_type not in workflows:
            raise ValueError(f"Unknown workflow: {workflow_type}")
        
        return workflows[workflow_type]()
    
    def _create_monthly_analysis_workflow(self) -> List[AgentTask]:
        """Create workflow for monthly billing analysis."""
        tasks = [
            AgentTask(
                agent_type=AgentType.DATA_VALIDATOR,
                task_id="validate_billing_data",
                description="Validate billing files and data integrity",
                input_data={"billing_folder": "billing"},
                priority=1
            ),
            AgentTask(
                agent_type=AgentType.BILLING_ANALYZER,
                task_id="analyze_billing",
                description="Analyze billing data and generate insights",
                input_data={"include_categorization": True},
                dependencies=["validate_billing_data"],
                priority=2
            ),
            AgentTask(
                agent_type=AgentType.CATEGORY_MANAGER,
                task_id="identify_uncategorized",
                description="Identify merchants requiring categorization",
                input_data={},
                dependencies=["analyze_billing"],
                priority=2
            ),
            AgentTask(
                agent_type=AgentType.REPORT_GENERATOR,
                task_id="generate_monthly_report",
                description="Generate comprehensive monthly report",
                input_data={"format": "json", "include_visualizations": True},
                dependencies=["analyze_billing", "identify_uncategorized"],
                priority=3
            ),
            AgentTask(
                agent_type=AgentType.NOTIFICATION_AGENT,
                task_id="notify_completion",
                description="Notify completion and any required actions",
                input_data={"notify_categorization_needed": True},
                dependencies=["generate_monthly_report"],
                priority=4
            )
        ]
        
        for task in tasks:
            task.created_at = datetime.now()
        
        return tasks
    
    def _create_category_review_workflow(self) -> List[AgentTask]:
        """Create workflow for category review and management."""
        return [
            AgentTask(
                agent_type=AgentType.CATEGORY_MANAGER,
                task_id="load_uncategorized",
                description="Load merchants requiring categorization",
                input_data={},
                priority=1,
                created_at=datetime.now()
            ),
            AgentTask(
                agent_type=AgentType.CATEGORY_MANAGER,
                task_id="suggest_categories",
                description="Use LLM to suggest categories for unknown merchants",
                input_data={"use_llm": True},
                dependencies=["load_uncategorized"],
                priority=2,
                created_at=datetime.now()
            ),
            AgentTask(
                agent_type=AgentType.NOTIFICATION_AGENT,
                task_id="notify_review_ready",
                description="Notify that categories are ready for human review",
                input_data={"review_type": "categorization"},
                dependencies=["suggest_categories"],
                priority=3,
                created_at=datetime.now()
            )
        ]
    
    def _create_data_validation_workflow(self) -> List[AgentTask]:
        """Create workflow for data validation and cleanup."""
        return [
            AgentTask(
                agent_type=AgentType.DATA_VALIDATOR,
                task_id="check_file_integrity",
                description="Check integrity of billing files",
                input_data={"billing_folder": "billing"},
                priority=1,
                created_at=datetime.now()
            ),
            AgentTask(
                agent_type=AgentType.DATA_VALIDATOR,
                task_id="validate_data_consistency",
                description="Validate data consistency across files",
                input_data={"check_duplicates": True, "check_anomalies": True},
                dependencies=["check_file_integrity"],
                priority=2,
                created_at=datetime.now()
            ),
            AgentTask(
                agent_type=AgentType.REPORT_GENERATOR,
                task_id="generate_validation_report",
                description="Generate data validation report",
                input_data={"format": "json"},
                dependencies=["validate_data_consistency"],
                priority=3,
                created_at=datetime.now()
            )
        ]
    
    def _create_comprehensive_report_workflow(self) -> List[AgentTask]:
        """Create workflow for comprehensive reporting."""
        return [
            AgentTask(
                agent_type=AgentType.BILLING_ANALYZER,
                task_id="analyze_trends",
                description="Analyze spending trends and patterns",
                input_data={"include_trends": True, "lookback_months": 6},
                priority=1,
                created_at=datetime.now()
            ),
            AgentTask(
                agent_type=AgentType.CATEGORY_MANAGER,
                task_id="category_analysis",
                description="Analyze spending by category over time",
                input_data={"include_category_trends": True},
                dependencies=["analyze_trends"],
                priority=2,
                created_at=datetime.now()
            ),
            AgentTask(
                agent_type=AgentType.REPORT_GENERATOR,
                task_id="generate_executive_summary",
                description="Generate executive summary with insights",
                input_data={"format": "markdown", "include_recommendations": True},
                dependencies=["analyze_trends", "category_analysis"],
                priority=3,
                created_at=datetime.now()
            )
        ]
    
    def execute_workflow(self, workflow_type: str) -> Dict[str, Any]:
        """Execute a complete workflow."""
        print(f"🚀 Starting workflow: {workflow_type}")
        
        tasks = self.create_workflow(workflow_type)
        self.task_queue.extend(tasks)
        
        results = []
        
        while self.task_queue:
            # Find next ready task (dependencies met)
            ready_tasks = [
                task for task in self.task_queue
                if task.status == "pending" and self._dependencies_met(task)
            ]
            
            if not ready_tasks:
                # Check if any tasks are still running
                running_tasks = [task for task in self.task_queue if task.status == "running"]
                if not running_tasks:
                    print("❌ Workflow deadlock - no ready tasks and none running")
                    break
                continue
            
            # Execute highest priority ready task
            task = min(ready_tasks, key=lambda t: t.priority)
            result = self._execute_task(task)
            results.append(result)
            
            # Move completed task
            self.task_queue.remove(task)
            self.completed_tasks.append(task)
        
        print(f"✅ Workflow '{workflow_type}' completed")
        return {
            "workflow_type": workflow_type,
            "tasks_completed": len(self.completed_tasks),
            "results": results,
            "completed_at": datetime.now().isoformat()
        }
    
    def _dependencies_met(self, task: AgentTask) -> bool:
        """Check if task dependencies are met."""
        if not task.dependencies:
            return True
        
        completed_task_ids = {t.task_id for t in self.completed_tasks if t.status == "completed"}
        return all(dep in completed_task_ids for dep in task.dependencies)
    
    def _execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a single task."""
        print(f"  🔄 Executing: {task.description}")
        
        task.status = "running"
        
        try:
            agent = self.agents[task.agent_type]
            result = agent.execute(task)
            
            task.status = "completed"
            task.result = result
            task.completed_at = datetime.now()
            
            print(f"  ✅ Completed: {task.description}")
            return result
            
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            
            print(f"  ❌ Failed: {task.description} - {e}")
            return {"error": str(e)}

# Agent implementations (simplified for demonstration)

class BaseAgent:
    """Base class for all agents."""
    
    def execute(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a task and return results."""
        raise NotImplementedError

class BillingAnalyzerAgent(BaseAgent):
    """Agent for billing analysis tasks."""
    
    def execute(self, task: AgentTask) -> Dict[str, Any]:
        from billing_agent import BillingAgent
        
        agent = BillingAgent()
        
        if task.task_id == "analyze_billing":
            return agent.process_monthly_billing()
        elif task.task_id == "analyze_trends":
            # Extended analysis with trends
            result = agent.process_monthly_billing()
            # Add trend analysis here
            return result
        
        return {"status": "completed", "task_id": task.task_id}

class CategoryManagerAgent(BaseAgent):
    """Agent for category management tasks."""
    
    def execute(self, task: AgentTask) -> Dict[str, Any]:
        if task.task_id == "identify_uncategorized":
            # Logic to identify uncategorized merchants
            return {"uncategorized_count": 0, "status": "completed"}
        elif task.task_id == "suggest_categories":
            # Logic to suggest categories using LLM
            return {"suggestions_generated": True, "status": "completed"}
        
        return {"status": "completed", "task_id": task.task_id}

class ReportGeneratorAgent(BaseAgent):
    """Agent for report generation tasks."""
    
    def execute(self, task: AgentTask) -> Dict[str, Any]:
        report_data = {
            "report_type": task.input_data.get("format", "json"),
            "generated_at": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # Generate actual report based on task
        filename = f"report_{task.task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return {"report_file": filename, "status": "completed"}

class DataValidatorAgent(BaseAgent):
    """Agent for data validation tasks."""
    
    def execute(self, task: AgentTask) -> Dict[str, Any]:
        # Implement data validation logic
        return {
            "validation_passed": True,
            "issues_found": 0,
            "status": "completed",
            "task_id": task.task_id
        }

class NotificationAgent(BaseAgent):
    """Agent for notifications and alerts."""
    
    def execute(self, task: AgentTask) -> Dict[str, Any]:
        # Implement notification logic
        print(f"📢 Notification: {task.description}")
        return {"notification_sent": True, "status": "completed"}

if __name__ == "__main__":
    # Test the coordinator
    coordinator = AgentCoordinator()
    result = coordinator.execute_workflow("monthly_analysis")
    print(json.dumps(result, indent=2, default=str))