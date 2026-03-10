from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum, Boolean, Float, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

# Enums
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class ProjectRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class SourceType(str, enum.Enum):
    GMAIL = "gmail"
    SLACK = "slack"
    MEETING = "meeting"
    FILE = "file"
    MANUAL = "manual"

class RequirementType(str, enum.Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    BUSINESS_OBJECTIVE = "business_objective"
    ASSUMPTION = "assumption"
    SUCCESS_METRIC = "success_metric"
    TIMELINE = "timeline"
    RISK = "risk"

class RequirementPriority(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SentimentType(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owned_projects = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    project_members = relationship("ProjectMember", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    comments = relationship("RequirementComment", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="refresh_tokens")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    keywords = Column(JSON)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="owned_projects", foreign_keys=[owner_id])
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="project", cascade="all, delete-orphan")
    requirements = relationship("Requirement", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="project", cascade="all, delete-orphan")

class ProjectMember(Base):
    __tablename__ = "project_members"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(SQLEnum(ProjectRole), default=ProjectRole.VIEWER)
    invited_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_members")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    source_type = Column(SQLEnum(SourceType))
    content = Column(Text)
    metadata = Column(JSON)
    author = Column(String)
    timestamp = Column(DateTime)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="messages")
    requirements = relationship("Requirement", back_populates="source_message")

class Requirement(Base):
    __tablename__ = "requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    requirement_type = Column(SQLEnum(RequirementType))
    content = Column(Text)
    priority = Column(SQLEnum(RequirementPriority), default=RequirementPriority.MEDIUM)
    confidence_score = Column(Float)
    sentiment = Column(SQLEnum(SentimentType), nullable=True)
    tags = Column(JSON)
    embedding = Column(JSON, nullable=True)  # Store vector embedding for similarity
    version = Column(Integer, default=1)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="requirements")
    source_message = relationship("Message", back_populates="requirements")
    comments = relationship("RequirementComment", back_populates="requirement", cascade="all, delete-orphan")
    history = relationship("RequirementHistory", back_populates="requirement", cascade="all, delete-orphan")
    conflicts = relationship("Conflict", foreign_keys="[Conflict.requirement1_id]", back_populates="requirement1")

class RequirementComment(Base):
    __tablename__ = "requirement_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    requirement = relationship("Requirement", back_populates="comments")
    user = relationship("User", back_populates="comments")

class RequirementHistory(Base):
    __tablename__ = "requirement_history"
    
    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"))
    version = Column(Integer)
    content = Column(Text)
    changed_by = Column(String)
    change_description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    requirement = relationship("Requirement", back_populates="history")

class Conflict(Base):
    __tablename__ = "conflicts"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    requirement1_id = Column(Integer, ForeignKey("requirements.id"))
    requirement2_id = Column(Integer, ForeignKey("requirements.id"))
    description = Column(Text)
    similarity_score = Column(Float)
    resolved = Column(Boolean, default=False)
    resolution_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    requirement1 = relationship("Requirement", foreign_keys=[requirement1_id], back_populates="conflicts")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    version = Column(Integer, default=1)
    content = Column(JSON)
    template_name = Column(String, default="default")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="documents")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(Integer)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="activity_logs")
    user = relationship("User", back_populates="activity_logs")
