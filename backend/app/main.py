from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.api import projects, documents, ingestion, editing, auth
from app.database import engine, Base, get_db
from app.models import User, Project, DataSource, ExtractedItem, Document, Conflict, SourceType, RawMessage, ExtractedRequirement
from app.services.gemini_engine import gemini_engine
from app.auth import get_current_user
from app.core.logging import logger
from dotenv import load_dotenv
import os

load_dotenv()


# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BRD Generation Platform",
    description="Automated Business Requirements Document generation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(ingestion.router, prefix="/api/ingestion", tags=["ingestion"])
app.include_router(editing.router, prefix="/api/editing", tags=["editing"])

@app.get("/")
def read_root():
    return {"message": "BRD Generation Platform API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "ai_enabled": gemini_engine.enabled}

# STEP 2: Direct Gemini Test Endpoint
@app.get("/test-gemini")
def test_gemini():
    """Test basic Gemini API connectivity."""
    try:
        if not gemini_engine.enabled:
            return {"error": "Gemini engine not enabled - check API key"}
        
        response = gemini_engine.model.generate_content("Say: Gemini integration successful")
        return {"result": response.text, "status": "success"}
    except Exception as e:
        logger.error(f"Gemini test error: {e}")
        return {"error": str(e), "status": "failed"}

# STEP 4: Test Gemini Extraction Logic
@app.get("/test-gemini-extraction")
def test_gemini_extraction():
    """Test Gemini structured extraction."""
    try:
        if not gemini_engine.enabled:
            return {"error": "Gemini engine not enabled - check API key"}
        
        sample_text = """
        The system must allow user login.
        The platform should launch by December.
        Assume users have internet access.
        """
        
        prompt = f"""Extract requirements from this text.
Categorize each as functional, timeline, or assumption.
Return JSON array with structure:
[{{"content": "...", "type": "functional|timeline|assumption"}}]

Text:
{sample_text}

Return ONLY valid JSON array, no markdown."""
        
        response = gemini_engine.model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Clean markdown if present
        if result_text.startswith('```'):
            lines = result_text.split('\n')
            result_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else result_text
            if result_text.startswith('json'):
                result_text = result_text[4:].strip()
        
        return {
            "result": result_text,
            "status": "success",
            "contains_functional": "functional" in result_text.lower(),
            "contains_timeline": "timeline" in result_text.lower(),
            "contains_assumption": "assumption" in result_text.lower()
        }
    except Exception as e:
        logger.error(f"Gemini extraction test error: {e}")
        return {"error": str(e), "status": "failed"}

# Ingest endpoint - fixed version
@app.post("/ingest")
def ingest_data(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ingest raw data into the system."""
    project_id = data.get("project_id")
    source_type = data.get("source_type", "text")
    content = data.get("content")
    sender = data.get("sender", "user")
    
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id is required")
    
    if not content:
        raise HTTPException(status_code=400, detail="content is required")
    
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify user has access
    owner_id = int(current_user["sub"])
    if project.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    try:
        # Create RawMessage
        message = RawMessage(
            project_id=project_id,
            content=content,
            source_type=source_type,
            sender=sender
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        return {
            "message": "Data ingested successfully",
            "message_id": message.id,
            "project_id": project_id
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Ingest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Smart extract endpoint using Gemini
@app.post("/smart-extract/{project_id}")
def smart_extract(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Smart extraction using Gemini AI - combines all messages and extracts intelligently."""
    # Verify project exists and user has access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    owner_id = int(current_user["sub"])
    if project.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    # Fetch all messages
    messages = db.query(RawMessage).filter(RawMessage.project_id == project_id).all()
    
    if not messages:
        raise HTTPException(status_code=400, detail="No messages found. Please upload data first.")
    
    try:
        # Combine all messages
        combined_text = "\n".join([msg.content for msg in messages])
        
        # Use Gemini for smart extraction
        extracted_items = gemini_engine.extract_requirements(combined_text)
        
        # Clear existing requirements for this project (optional - for re-extraction)
        # db.query(ExtractedRequirement).filter(ExtractedRequirement.project_id == project_id).delete()
        
        # Save new requirements
        saved_count = 0
        for item in extracted_items:
            requirement = ExtractedRequirement(
                project_id=project_id,
                content=item["content"],
                requirement_type=item.get("type", "functional"),
                priority=item.get("priority", "medium"),
                confidence_score=item.get("confidence", 0.8)
            )
            db.add(requirement)
            saved_count += 1
        
        db.commit()
        
        return {
            "message": "Smart extraction completed",
            "extracted_count": saved_count,
            "requirements": extracted_items,
            "ai_powered": gemini_engine.enabled
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Smart extract error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Generate BRD endpoint using Gemini
@app.get("/generate-brd/{project_id}")
def generate_brd(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate Business Requirements Document using Gemini AI."""
    # Verify project exists and user has access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    owner_id = int(current_user["sub"])
    if project.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    # Get all requirements
    requirements = db.query(ExtractedRequirement).filter(
        ExtractedRequirement.project_id == project_id
    ).all()
    
    if not requirements:
        raise HTTPException(
            status_code=400, 
            detail="No requirements found. Please extract requirements first."
        )
    
    try:
        # Get requirement texts
        req_texts = [req.content for req in requirements]
        
        # Use Gemini to generate BRD
        brd_content = gemini_engine.generate_brd_summary(req_texts)
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "total_requirements": len(requirements),
            "brd": brd_content,
            "ai_powered": gemini_engine.enabled
        }
    except Exception as e:
        logger.error(f"BRD generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# File upload endpoint
@app.post("/upload-file/{project_id}")
async def upload_file(
    project_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a file and store its content in RawMessage table. Supports TXT, PDF, DOCX, JSON."""
    # Verify project exists and user has access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    owner_id = int(current_user["sub"])
    if project.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    try:
        # Read file content
        content = await file.read()
        
        # Get file extension
        file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
        
        # Extract text based on file type
        text = ""
        
        if file_ext == "txt":
            # Text files - decode with error handling
            text = content.decode("utf-8", errors="ignore")
        
        elif file_ext == "json":
            # JSON files
            text = content.decode("utf-8", errors="ignore")
        
        elif file_ext == "pdf":
            # PDF files - extract text
            try:
                from PyPDF2 import PdfReader
                from io import BytesIO
                
                pdf_reader = PdfReader(BytesIO(content))
                text_parts = []
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                text = "\n".join(text_parts)
                
                if not text.strip():
                    raise HTTPException(
                        status_code=400, 
                        detail="PDF appears to be empty or contains only images. Text extraction failed."
                    )
            except Exception as pdf_error:
                logger.error(f"PDF extraction error: {pdf_error}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to extract text from PDF: {str(pdf_error)}"
                )
        
        elif file_ext in ["doc", "docx"]:
            # DOCX files - extract text
            try:
                from docx import Document
                from io import BytesIO
                
                doc = Document(BytesIO(content))
                text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
                text = "\n".join(text_parts)
                
                if not text.strip():
                    raise HTTPException(
                        status_code=400, 
                        detail="DOCX file appears to be empty."
                    )
            except Exception as docx_error:
                logger.error(f"DOCX extraction error: {docx_error}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to extract text from DOCX: {str(docx_error)}"
                )
        
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: .{file_ext}. Supported formats: TXT, PDF, DOCX, JSON"
            )
        
        # Validate extracted text
        if not text.strip():
            raise HTTPException(
                status_code=400, 
                detail="File appears to be empty or contains no extractable text."
            )
        
        # Split content into lines
        lines = text.split("\n")
        
        message_count = 0
        for line in lines:
            if line.strip():  # Only process non-empty lines
                message = RawMessage(
                    project_id=project_id,
                    content=line.strip(),
                    source_type="file",
                    sender="uploaded_user"
                )
                db.add(message)
                message_count += 1
        
        # Commit once after loop
        db.commit()
        
        logger.info(f"File uploaded: {file.filename}, type: {file_ext}, lines: {message_count}")
        
        return {
            "message": "File processed and messages saved",
            "filename": file.filename,
            "file_type": file_ext,
            "lines_processed": message_count
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing file {file.filename}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"File processing failed: {str(e)}"
        )

# Extract requirements endpoint using Gemini AI
@app.post("/extract-requirements/{project_id}")
def extract_requirements(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extract requirements from RawMessage entries using Gemini AI."""
    # Verify project exists and user has access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    owner_id = int(current_user["sub"])
    if project.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    # Fetch RawMessage by project_id
    messages = db.query(RawMessage).filter(RawMessage.project_id == project_id).all()
    
    if len(messages) == 0:
        raise HTTPException(
            status_code=400, 
            detail="No messages found for this project. Please upload a file first."
        )
    
    try:
        # Combine all messages into single text block for Gemini
        combined_text = "\n".join([msg.content for msg in messages])
        
        logger.info(f"Extracting requirements for project {project_id} using Gemini AI")
        
        # Use Gemini to extract requirements
        extracted_items = gemini_engine.extract_requirements(combined_text)
        
        total_extracted = 0
        for item in extracted_items:
            # Check if already exists
            existing = db.query(ExtractedRequirement).filter(
                ExtractedRequirement.project_id == project_id,
                ExtractedRequirement.content == item["content"]
            ).first()
            
            if existing:
                continue  # Skip duplicates
            
            # Create new requirement
            requirement = ExtractedRequirement(
                project_id=project_id,
                content=item["content"],
                requirement_type=item.get("type", "functional"),
                priority=item.get("priority", "medium"),
                confidence_score=item.get("confidence", 0.7)
            )
            db.add(requirement)
            total_extracted += 1
        
        # Commit all at once
        db.commit()
        
        logger.info(f"Successfully extracted {total_extracted} requirements")
        
        return {
            "message": "Requirements extracted successfully using Gemini AI",
            "total_messages": len(messages),
            "total_extracted": total_extracted,
            "ai_powered": gemini_engine.enabled
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error extracting requirements: {e}")
        raise HTTPException(status_code=500, detail=f"Error extracting requirements: {str(e)}")

# Get requirements endpoint
@app.get("/requirements/{project_id}")
def get_requirements(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all extracted requirements for a project."""
    # Verify project exists and user has access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    owner_id = int(current_user["sub"])
    if project.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    # Get all extracted requirements
    requirements = db.query(ExtractedRequirement).filter(
        ExtractedRequirement.project_id == project_id
    ).all()
    
    return {
        "total": len(requirements),
        "items": [
            {
                "id": req.id,
                "content": req.content,
                "type": req.requirement_type,
                "priority": req.priority,
                "confidence": req.confidence_score,
                "created_at": req.created_at.isoformat()
            }
            for req in requirements
        ]
    }
