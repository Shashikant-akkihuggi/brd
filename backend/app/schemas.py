from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import SourceType, RequirementType, SentimentType

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ProjectResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str]
    keywords: Optional[List[str]]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class DataSourceCreate(BaseModel):
    source_type: SourceType
    source_id: str
    content: str
    source_metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    author: Optional[str] = None

class ExtractedItemResponse(BaseModel):
    id: int
    item_type: RequirementType
    content: str
    confidence_score: float
    sentiment: Optional[SentimentType]
    source_id: int
    
    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: int
    project_id: int
    version: int
    content: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

class EditRequest(BaseModel):
    section: Optional[str] = None
    instruction: str

class ConflictResponse(BaseModel):
    id: int
    item1_content: str
    item2_content: str
    description: str
    resolved: bool
    
    class Config:
        from_attributes = True
