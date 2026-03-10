from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Project, DataSource, ExtractedItem, Conflict
from app.schemas import DataSourceCreate
from app.services.ingestion import DataIngestionService
from app.services.extractor import InformationExtractor
from app.auth import require_editor, require_viewer
import tempfile
import os

router = APIRouter()
ingestion_service = DataIngestionService()
extractor = InformationExtractor()

@router.post("/{project_id}/upload")
async def upload_file(
    project_id: int, 
    file: UploadFile = File(...), 
    current_user: dict = Depends(require_editor()),  # Editor or Admin can upload
    db: Session = Depends(get_db)
):
    """
    Upload and process a file.
    Requires: Editor or Admin role.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Ingest file
        file_ext = os.path.splitext(file.filename)[1].lstrip('.')
        ingested_data = await ingestion_service.ingest_file(tmp_path, file_ext)
        
        # Save to database
        data_source = DataSource(
            project_id=project_id,
            source_type=ingested_data["source_type"],
            source_id=file.filename,
            content=ingested_data["content"],
            source_metadata=ingested_data["source_metadata"],
            timestamp=ingested_data["timestamp"]
        )
        db.add(data_source)
        db.commit()
        db.refresh(data_source)
        
        # Extract requirements
        extracted = extractor.extract_requirements(
            ingested_data["content"],
            project.keywords
        )
        
        # Save extracted items
        for item in extracted:
            extracted_item = ExtractedItem(
                project_id=project_id,
                source_id=data_source.id,
                item_type=item["type"],
                content=item["content"],
                confidence_score=item["confidence"],
                sentiment=item["sentiment"]
            )
            db.add(extracted_item)
        
        db.commit()
        
        return {
            "message": "File processed successfully",
            "source_id": data_source.id,
            "extracted_count": len(extracted)
        }
    finally:
        os.unlink(tmp_path)

@router.post("/{project_id}/manual")
def add_manual_data(
    project_id: int, 
    data: DataSourceCreate, 
    current_user: dict = Depends(require_editor()),  # Editor or Admin can add data
    db: Session = Depends(get_db)
):
    """
    Manually add data source.
    Requires: Editor or Admin role.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    data_source = DataSource(
        project_id=project_id,
        source_type=data.source_type,
        source_id=data.source_id,
        content=data.content,
        source_metadata=data.source_metadata,
        timestamp=data.timestamp,
        author=data.author
    )
    db.add(data_source)
    db.commit()
    db.refresh(data_source)
    
    # Extract requirements
    extracted = extractor.extract_requirements(data.content, project.keywords)
    
    for item in extracted:
        extracted_item = ExtractedItem(
            project_id=project_id,
            source_id=data_source.id,
            item_type=item["type"],
            content=item["content"],
            confidence_score=item["confidence"],
            sentiment=item["sentiment"]
        )
        db.add(extracted_item)
    
    db.commit()
    
    return {
        "message": "Data added successfully",
        "source_id": data_source.id,
        "extracted_count": len(extracted)
    }

@router.post("/{project_id}/detect-conflicts")
def detect_conflicts(
    project_id: int, 
    current_user: dict = Depends(require_viewer()),  # All users can detect conflicts
    db: Session = Depends(get_db)
):
    """
    Detect conflicts in extracted requirements.
    Requires: Any authenticated user.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    items = db.query(ExtractedItem).filter(ExtractedItem.project_id == project_id).all()
    
    items_data = [{"content": item.content, "id": item.id} for item in items]
    conflicts = extractor.detect_conflicts(items_data)
    
    for idx1, idx2, description in conflicts:
        conflict = Conflict(
            project_id=project_id,
            item1_id=items_data[idx1]["id"],
            item2_id=items_data[idx2]["id"],
            description=description
        )
        db.add(conflict)
    
    db.commit()
    
    return {"message": f"Detected {len(conflicts)} conflicts", "count": len(conflicts)}
