from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Project, User
from app.schemas import ProjectCreate, ProjectResponse
from app.auth import (
    get_current_user, 
    require_admin, 
    require_editor, 
    require_viewer,
    verify_project_ownership,
    get_user_project,
    get_user_projects
)

router = APIRouter()

@router.post("/", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate, 
    current_user: dict = Depends(require_editor()),
    db: Session = Depends(get_db)
):
    """
    Create a new project.
    Automatically assigns current user as owner.
    Requires: Editor or Admin role.
    """
    try:
        owner_id = int(current_user["sub"])
        
        # Create project with current user as owner
        db_project = Project(
            owner_id=owner_id,
            name=project.name,
            description=project.description,
            keywords=project.keywords,
            start_date=project.start_date,
            end_date=project.end_date
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        return db_project
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

@router.get("/my-projects", response_model=List[ProjectResponse])
def get_my_projects(
    skip: int = 0, 
    limit: int = 100, 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all projects owned by the current user.
    Returns only projects where current user is the owner.
    Requires: Any authenticated user.
    """
    owner_id = int(current_user["sub"])
    projects = get_user_projects(db, owner_id, skip, limit)
    return projects

@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    skip: int = 0, 
    limit: int = 100, 
    current_user: dict = Depends(require_viewer()),
    db: Session = Depends(get_db)
):
    """
    List all projects owned by current user.
    Users can only see their own projects.
    Requires: Any authenticated user (Viewer, Editor, or Admin).
    """
    owner_id = int(current_user["sub"])
    projects = get_user_projects(db, owner_id, skip, limit)
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int, 
    current_user: dict = Depends(require_viewer()),
    db: Session = Depends(get_db)
):
    """
    Get a specific project.
    Users can only access projects they own.
    Requires: Any authenticated user (Viewer, Editor, or Admin).
    """
    owner_id = int(current_user["sub"])
    project = get_user_project(db, project_id, owner_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you don't have access to it"
        )
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectCreate,
    current_user: dict = Depends(require_editor()),
    db: Session = Depends(get_db)
):
    """
    Update a project.
    Users can only update projects they own.
    Requires: Editor or Admin role.
    """
    owner_id = int(current_user["sub"])
    project = get_user_project(db, project_id, owner_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you don't have access to it"
        )
    
    # Verify ownership
    if not verify_project_ownership(project, owner_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this project"
        )
    
    # Update fields
    project.name = project_update.name
    project.description = project_update.description
    project.keywords = project_update.keywords
    project.start_date = project_update.start_date
    project.end_date = project_update.end_date
    
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}")
def delete_project(
    project_id: int, 
    current_user: dict = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Delete a project.
    Users can only delete projects they own.
    Requires: Admin role only.
    """
    owner_id = int(current_user["sub"])
    project = get_user_project(db, project_id, owner_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you don't have access to it"
        )
    
    # Verify ownership
    if not verify_project_ownership(project, owner_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this project"
        )
    
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully"}

@router.get("/{project_id}/owner", response_model=dict)
def get_project_owner(
    project_id: int,
    current_user: dict = Depends(require_viewer()),
    db: Session = Depends(get_db)
):
    """
    Get project owner information.
    Users can only access projects they own.
    Requires: Any authenticated user.
    """
    owner_id = int(current_user["sub"])
    project = get_user_project(db, project_id, owner_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you don't have access to it"
        )
    
    # Get owner information
    owner = db.query(User).filter(User.id == project.owner_id).first()
    
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )
    
    return {
        "project_id": project.id,
        "project_name": project.name,
        "owner": {
            "id": owner.id,
            "username": owner.username,
            "email": owner.email,
            "full_name": owner.full_name
        }
    }
