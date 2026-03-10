from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class UserRole(str, enum.Enum):
    """User roles for RBAC system."""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="admin", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    projects = relationship("Project", back_populates="owner")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="refresh_tokens")

class SourceType(str, enum.Enum):
    GMAIL = "gmail"
    SLACK = "slack"
    MEETING = "meeting"
    FILE = "file"

class RequirementType(str, enum.Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    BUSINESS_OBJECTIVE = "business_objective"
    ASSUMPTION = "assumption"
    SUCCESS_METRIC = "success_metric"

class SentimentType(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    keywords = Column(JSON)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="projects")
    sources = relationship("DataSource", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    extracted_items = relationship("ExtractedItem", back_populates="project", cascade="all, delete-orphan")
    raw_messages = relationship("RawMessage", back_populates="project", cascade="all, delete-orphan")
    extracted_requirements = relationship("ExtractedRequirement", back_populates="project", cascade="all, delete-orphan")

class RawMessage(Base):
    __tablename__ = "raw_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    content = Column(Text, nullable=False)
    source_type = Column(String, default="file")
    sender = Column(String, default="uploaded_user")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="raw_messages")

class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    source_type = Column(SQLEnum(SourceType))
    source_id = Column(String)
    content = Column(Text)
    source_metadata = Column(JSON)
    timestamp = Column(DateTime)
    author = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="sources")
    extracted_items = relationship("ExtractedItem", back_populates="source")

class ExtractedItem(Base):
    __tablename__ = "extracted_items"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    source_id = Column(Integer, ForeignKey("data_sources.id"))
    item_type = Column(SQLEnum(RequirementType))
    content = Column(Text)
    confidence_score = Column(Integer)
    sentiment = Column(SQLEnum(SentimentType), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="extracted_items")
    source = relationship("DataSource", back_populates="extracted_items")
    conflicts = relationship("Conflict", foreign_keys="[Conflict.item1_id]", back_populates="item1")

class ExtractedRequirement(Base):
    __tablename__ = "extracted_requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    content = Column(Text, nullable=False)
    requirement_type = Column(String, default="functional")
    priority = Column(String, default="medium")
    confidence_score = Column(Integer, default=80)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="extracted_requirements")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    version = Column(Integer, default=1)
    content = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="documents")

class Conflict(Base):
    __tablename__ = "conflicts"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    item1_id = Column(Integer, ForeignKey("extracted_items.id"))
    item2_id = Column(Integer, ForeignKey("extracted_items.id"))
    description = Column(Text)
    resolved = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    item1 = relationship("ExtractedItem", foreign_keys=[item1_id], back_populates="conflicts")
