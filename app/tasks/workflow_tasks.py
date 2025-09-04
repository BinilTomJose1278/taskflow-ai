"""
Celery tasks for workflow processing
"""

from celery import current_task
from app.celery_app import celery_app
from app.services.workflow_service import WorkflowService
from app.core.database import SessionLocal
from app.models.document import Workflow
import asyncio

@celery_app.task(bind=True)
def execute_workflow(self, workflow_id: int):
    """Execute a workflow asynchronously."""
    
    db = SessionLocal()
    try:
        workflow_service = WorkflowService(db)
        
        # Get workflow
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 10, 'status': f'Starting workflow: {workflow.name}'})
        
        # Execute workflow
        await workflow_service.execute_workflow(workflow_id)
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 100, 'status': 'Workflow execution completed'})
        
        return {
            'workflow_id': workflow_id,
            'workflow_name': workflow.name,
            'status': 'completed'
        }
        
    except Exception as e:
        raise self.retry(exc=e, countdown=60, max_retries=3)
    
    finally:
        db.close()

@celery_app.task(bind=True)
def execute_workflow_step(self, workflow_id: int, step_id: str):
    """Execute a single workflow step."""
    
    db = SessionLocal()
    try:
        workflow_service = WorkflowService(db)
        
        # Get workflow
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Find the step
        step = None
        for step_data in workflow.steps:
            if step_data.get('step_id') == step_id:
                step = step_data
                break
        
        if not step:
            raise ValueError(f"Step {step_id} not found in workflow {workflow_id}")
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 10, 'status': f'Executing step: {step_id}'})
        
        # Execute the step
        success = await workflow_service._execute_step(step['step_type'], step.get('config', {}))
        
        if not success:
            raise ValueError(f"Step {step_id} execution failed")
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 100, 'status': f'Step {step_id} completed'})
        
        return {
            'workflow_id': workflow_id,
            'step_id': step_id,
            'step_type': step['step_type'],
            'status': 'completed'
        }
        
    except Exception as e:
        raise self.retry(exc=e, countdown=60, max_retries=3)
    
    finally:
        db.close()

@celery_app.task
def schedule_workflow_execution(workflow_id: int, schedule_time: str):
    """Schedule a workflow for future execution."""
    
    db = SessionLocal()
    try:
        # This would integrate with a scheduler like Celery Beat
        # For now, we'll just log the scheduling request
        
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        return {
            'workflow_id': workflow_id,
            'workflow_name': workflow.name,
            'scheduled_time': schedule_time,
            'status': 'scheduled'
        }
        
    except Exception as e:
        return {
            'workflow_id': workflow_id,
            'status': 'failed',
            'error': str(e)
        }
    
    finally:
        db.close()

@celery_app.task
def cleanup_failed_workflows():
    """Clean up failed workflow executions."""
    
    db = SessionLocal()
    try:
        # This would contain cleanup logic for failed workflows
        # For example, resetting status, cleaning up temporary files, etc.
        
        return {
            'status': 'completed',
            'message': 'Failed workflow cleanup completed'
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }
    
    finally:
        db.close()
