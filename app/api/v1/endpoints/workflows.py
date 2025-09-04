"""
Workflow management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.document import Workflow
from app.schemas.document import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse
)
from app.services.workflow_service import WorkflowService

router = APIRouter()

@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new workflow
    """
    try:
        workflow_service = WorkflowService(db)
        workflow = await workflow_service.create_workflow(workflow_data)
        return workflow
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating workflow: {str(e)}")

@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    db: Session = Depends(get_db)
):
    """
    List all workflows
    """
    try:
        workflow_service = WorkflowService(db)
        workflows = await workflow_service.list_workflows()
        return workflows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing workflows: {str(e)}")

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific workflow
    """
    try:
        workflow_service = WorkflowService(db)
        workflow = await workflow_service.get_workflow(workflow_id)
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return workflow
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving workflow: {str(e)}")

@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    workflow_update: WorkflowUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a workflow
    """
    try:
        workflow_service = WorkflowService(db)
        workflow = await workflow_service.update_workflow(workflow_id, workflow_update)
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return workflow
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating workflow: {str(e)}")

@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a workflow
    """
    try:
        workflow_service = WorkflowService(db)
        success = await workflow_service.delete_workflow(workflow_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {"message": "Workflow deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting workflow: {str(e)}")

@router.post("/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Execute a workflow
    """
    try:
        workflow_service = WorkflowService(db)
        
        # Check if workflow exists
        workflow = await workflow_service.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Start workflow execution in background
        background_tasks.add_task(
            workflow_service.execute_workflow,
            workflow_id
        )
        
        return {"message": "Workflow execution started", "workflow_id": workflow_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing workflow: {str(e)}")
