from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Document
from app.schemas import EditRequest, DocumentResponse
from app.services.editor import DocumentEditor
from app.auth import require_editor

router = APIRouter()
editor = DocumentEditor()

@router.post("/{document_id}/edit", response_model=DocumentResponse)
def edit_document(
    document_id: int, 
    edit_request: EditRequest, 
    current_user: dict = Depends(require_editor()),  # Editor or Admin can edit
    db: Session = Depends(get_db)
):
    """
    Edit document using natural language instruction.
    Requires: Editor or Admin role.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Parse edit request
    parsed_edit = editor.parse_edit_request(edit_request.instruction, edit_request.section)
    
    # Apply edit
    updated_content = editor.apply_edit(document.content, parsed_edit)
    
    # Create new version
    new_version = Document(
        project_id=document.project_id,
        version=document.version + 1,
        content=updated_content
    )
    db.add(new_version)
    db.commit()
    db.refresh(new_version)
    
    return new_version
