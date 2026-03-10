from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models_enhanced import Requirement, RequirementHistory, Comment, User, Project
from app.core.security import get_current_user
from app.services.gemini_engine import gemini_engine
from app.core.logging import logger
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Schemas
class RequirementCreate(BaseModel):
    content: str
    message_id: Optional[int] = None
    tags: Optional[List[str]] = []

class RequirementUpdate(BaseModel):
    content: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None

class CommentCreate(BaseModel):
    content: str

class AIRewriteRequest(BaseModel):
    instruction: str

@router.post("/{project_id}/requirements")
async def create_requirement(
    project_id: int,
    req: RequirementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new requirement with AI classification."""
    # Verify project access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # AI classification
    classification = await ai_engine.classify_requirement(req.content)
    
    # Create requirement
    requirement = Requirement(
        project_id=project_id,
        message_id=req.message_id,
        content=req.content,
        requirement_type=classification['type'],
        priority=classification['priority'],
        confidence_score=classification['confidence'],
        ai_generated=True,
        tags=req.tags or []
    )
    
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    
    # Create history entry
    history = RequirementHistory(
        requirement_id=requirement.id,
        content=req.content,
        changed_by=current_user.id,
        change_type="created",
        version=1
    )
    db.add(history)
    db.commit()
    
    logger.info(f"Requirement {requirement.id} created for project {project_id}")
    
    return {
        "id": requirement.id,
        "content": requirement.content,
        "type": requirement.requirement_type,
        "priority": requirement.priority,
        "confidence": requirement.confidence_score,
        "tags": requirement.tags,
        "created_at": requirement.created_at
    }

@router.get("/{project_id}/requirements")
async def list_requirements(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    requirement_type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List requirements with filtering and pagination."""
    # Verify project access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Build query
    query = db.query(Requirement).filter(Requirement.project_id == project_id)
    
    if requirement_type:
        query = query.filter(Requirement.requirement_type == requirement_type)
    if status:
        query = query.filter(Requirement.status == status)
    if priority:
        query = query.filter(Requirement.priority == priority)
    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
        query = query.filter(Requirement.tags.overlap(tag_list))
    
    total = query.count()
    requirements = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": r.id,
                "content": r.content,
                "type": r.requirement_type,
                "priority": r.priority,
                "status": r.status,
                "confidence": r.confidence_score,
                "tags": r.tags,
                "version": r.version,
                "created_at": r.created_at,
                "updated_at": r.updated_at
            }
            for r in requirements
        ]
    }

@router.put("/{project_id}/requirements/{requirement_id}")
async def update_requirement(
    project_id: int,
    requirement_id: int,
    update: RequirementUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a requirement."""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.project_id == project_id
    ).first()
    
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    # Verify project access
    project = db.query(Project).filter(Project.id == project_id).first()
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update fields
    if update.content:
        requirement.content = update.content
        requirement.version += 1
        
        # Create history entry
        history = RequirementHistory(
            requirement_id=requirement.id,
            content=update.content,
            changed_by=current_user.id,
            change_type="updated",
            version=requirement.version
        )
        db.add(history)
    
    if update.priority:
        requirement.priority = update.priority
    if update.status:
        requirement.status = update.status
        history = RequirementHistory(
            requirement_id=requirement.id,
            content=requirement.content,
            changed_by=current_user.id,
            change_type="status_changed",
            version=requirement.version
        )
        db.add(history)
    if update.tags is not None:
        requirement.tags = update.tags
    
    requirement.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(requirement)
    
    return {"message": "Requirement updated", "version": requirement.version}

@router.delete("/{project_id}/requirements/{requirement_id}")
async def delete_requirement(
    project_id: int,
    requirement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a requirement."""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.project_id == project_id
    ).first()
    
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    # Verify project access
    project = db.query(Project).filter(Project.id == project_id).first()
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(requirement)
    db.commit()
    
    return {"message": "Requirement deleted"}

@router.get("/{project_id}/requirements/{requirement_id}/history")
async def get_requirement_history(
    project_id: int,
    requirement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get requirement version history."""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.project_id == project_id
    ).first()
    
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    history = db.query(RequirementHistory).filter(
        RequirementHistory.requirement_id == requirement_id
    ).order_by(RequirementHistory.created_at.desc()).all()
    
    return {
        "requirement_id": requirement_id,
        "current_version": requirement.version,
        "history": [
            {
                "version": h.version,
                "content": h.content,
                "change_type": h.change_type,
                "changed_by": h.changed_by,
                "created_at": h.created_at
            }
            for h in history
        ]
    }

@router.post("/{project_id}/requirements/{requirement_id}/comments")
async def add_comment(
    project_id: int,
    requirement_id: int,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to a requirement."""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.project_id == project_id
    ).first()
    
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    new_comment = Comment(
        requirement_id=requirement_id,
        author_id=current_user.id,
        content=comment.content
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return {
        "id": new_comment.id,
        "content": new_comment.content,
        "author_id": current_user.id,
        "created_at": new_comment.created_at
    }

@router.post("/{project_id}/requirements/{requirement_id}/ai-rewrite")
async def ai_rewrite(
    project_id: int,
    requirement_id: int,
    request: AIRewriteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Use AI to rewrite a requirement."""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.project_id == project_id
    ).first()
    
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    # Verify project access
    project = db.query(Project).filter(Project.id == project_id).first()
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # AI rewrite
    rewritten = await ai_engine.rewrite_requirement(requirement.content, request.instruction)
    
    return {
        "original": requirement.content,
        "rewritten": rewritten,
        "instruction": request.instruction
    }

@router.post("/{project_id}/requirements/detect-duplicates")
async def detect_duplicates(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Detect duplicate requirements using AI."""
    # Verify project access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()
    
    req_list = [{"id": r.id, "content": r.content} for r in requirements]
    duplicates = ai_engine.detect_duplicates(req_list)
    
    return {"duplicates": duplicates, "count": len(duplicates)}

@router.post("/{project_id}/requirements/detect-conflicts")
async def detect_conflicts(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Detect conflicting requirements using AI."""
    # Verify project access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()
    
    req_list = [{"id": r.id, "content": r.content} for r in requirements]
    conflicts = ai_engine.detect_conflicts(req_list)
    
    return {"conflicts": conflicts, "count": len(conflicts)}

@router.post("/{project_id}/requirements/bulk-update")
async def bulk_update_requirements(
    project_id: int,
    requirement_ids: List[int],
    update: RequirementUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk update multiple requirements."""
    # Verify project access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    requirements = db.query(Requirement).filter(
        Requirement.id.in_(requirement_ids),
        Requirement.project_id == project_id
    ).all()
    
    updated_count = 0
    for req in requirements:
        if update.priority:
            req.priority = update.priority
        if update.status:
            req.status = update.status
        if update.tags is not None:
            req.tags = update.tags
        req.updated_at = datetime.utcnow()
        updated_count += 1
    
    db.commit()
    
    return {"message": f"Updated {updated_count} requirements"}
