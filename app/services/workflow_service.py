"""
Workflow service for automation and pipeline management
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.document import Workflow
from app.schemas.document import WorkflowCreate, WorkflowUpdate, WorkflowResponse

class WorkflowService:
    """Service for workflow operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_workflow(self, workflow_data: WorkflowCreate) -> WorkflowResponse:
        """Create a new workflow"""
        
        # Convert steps to dict for storage
        steps_data = [step.dict() for step in workflow_data.steps]
        
        db_workflow = Workflow(
            name=workflow_data.name,
            description=workflow_data.description,
            trigger_type=workflow_data.trigger_type,
            trigger_config=workflow_data.trigger_config,
            steps=steps_data,
            organization_id=1  # Default organization
        )
        
        self.db.add(db_workflow)
        self.db.commit()
        self.db.refresh(db_workflow)
        
        return WorkflowResponse.from_orm(db_workflow)
    
    async def get_workflow(self, workflow_id: int) -> Optional[WorkflowResponse]:
        """Get a workflow by ID"""
        workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            return None
        
        return WorkflowResponse.from_orm(workflow)
    
    async def list_workflows(self) -> List[WorkflowResponse]:
        """List all workflows"""
        workflows = self.db.query(Workflow).filter(Workflow.is_active == True).all()
        return [WorkflowResponse.from_orm(workflow) for workflow in workflows]
    
    async def update_workflow(
        self,
        workflow_id: int,
        workflow_update: WorkflowUpdate
    ) -> Optional[WorkflowResponse]:
        """Update a workflow"""
        workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            return None
        
        # Update fields
        update_data = workflow_update.dict(exclude_unset=True)
        
        # Handle steps conversion
        if "steps" in update_data and update_data["steps"]:
            update_data["steps"] = [step.dict() for step in update_data["steps"]]
        
        for field, value in update_data.items():
            setattr(workflow, field, value)
        
        workflow.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(workflow)
        
        return WorkflowResponse.from_orm(workflow)
    
    async def delete_workflow(self, workflow_id: int) -> bool:
        """Delete a workflow"""
        workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            return False
        
        # Soft delete by setting is_active to False
        workflow.is_active = False
        workflow.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    async def execute_workflow(self, workflow_id: int):
        """Execute a workflow"""
        try:
            workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
            if not workflow:
                print(f"❌ Workflow {workflow_id} not found")
                return
            
            print(f"🚀 Executing workflow: {workflow.name}")
            
            # Update run statistics
            workflow.total_runs += 1
            
            # Execute each step in the workflow
            for step_data in workflow.steps:
                step_id = step_data.get("step_id")
                step_type = step_data.get("step_type")
                config = step_data.get("config", {})
                
                print(f"  📋 Executing step: {step_id} ({step_type})")
                
                # Execute step based on type
                success = await self._execute_step(step_type, config)
                
                if not success:
                    print(f"  ❌ Step {step_id} failed")
                    workflow.failed_runs += 1
                    self.db.commit()
                    return
            
            # Mark as successful
            workflow.successful_runs += 1
            self.db.commit()
            print(f"✅ Workflow {workflow.name} completed successfully")
            
        except Exception as e:
            print(f"❌ Error executing workflow {workflow_id}: {e}")
            if workflow:
                workflow.failed_runs += 1
                self.db.commit()
    
    async def _execute_step(self, step_type: str, config: dict) -> bool:
        """Execute a single workflow step"""
        try:
            if step_type == "text_extraction":
                return await self._execute_text_extraction_step(config)
            elif step_type == "ai_analysis":
                return await self._execute_ai_analysis_step(config)
            elif step_type == "categorization":
                return await self._execute_categorization_step(config)
            elif step_type == "notification":
                return await self._execute_notification_step(config)
            else:
                print(f"  ⚠️ Unknown step type: {step_type}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error executing step {step_type}: {e}")
            return False
    
    async def _execute_text_extraction_step(self, config: dict) -> bool:
        """Execute text extraction step"""
        # Simulate text extraction
        await asyncio.sleep(1)  # Simulate processing time
        print(f"    📄 Text extraction completed")
        return True
    
    async def _execute_ai_analysis_step(self, config: dict) -> bool:
        """Execute AI analysis step"""
        # Simulate AI analysis
        await asyncio.sleep(2)  # Simulate processing time
        print(f"    🤖 AI analysis completed")
        return True
    
    async def _execute_categorization_step(self, config: dict) -> bool:
        """Execute categorization step"""
        # Simulate categorization
        await asyncio.sleep(1)  # Simulate processing time
        print(f"    🏷️ Categorization completed")
        return True
    
    async def _execute_notification_step(self, config: dict) -> bool:
        """Execute notification step"""
        # Simulate notification
        await asyncio.sleep(0.5)  # Simulate processing time
        print(f"    📧 Notification sent")
        return True
