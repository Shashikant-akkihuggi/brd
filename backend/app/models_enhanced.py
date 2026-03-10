from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum, Float, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from datetime import datetime
import enum
from app.database import Base

# Association tables
project_members = Table(
    'project_members',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('project_id', Integer, ForeignKey('projects.id', ondelete='CASCADE')),
    Column('role', String, default='viewer'),
    Column('joined_at', DateTime, default=datetime.utcnow)
)

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class ProjectRole(str, enum.Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"

class RequirementType(str, enum.Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    BUSINESS_OBJECTIVE = "business_objective"
    ASSUMPTION = "assumption"
    RISK = "risk"
    TIMELINE = "timeline"
    SUCCESS_METRIC = "success_metric"

class RequirementPriority(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RequirementStatus(str, enum.Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"

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
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    owned_projects = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="refresh_tokens")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    keywords = Column(ARRAY(String), default=[])
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="owned_projects", foreign_keys=[owner_id])
    messages = relationship("Message", back_populates="project", cascade="all, delete-orphan")
    requirements = relationship("Requirement", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    conflicts = relationship("Conflict", back_populates="project", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    author_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    content = Column(Text, nullable=False)
    source_type = Column(String)  # email, slack, meeting, manual
    source_metadata = Column(JSON)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    edited_at = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="messages")
    author = relationship("User", back_populates="messages")
    requirements = relationship("Requirement", back_populates="source_message")

class Requirement(Base):
    __tablename__ = "requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    requirement_type = Column(SQLEnum(RequirementType))
    content = Column(Text, nullable=False)
    priority = Column(SQLEnum(RequirementPriority), default=RequirementPriority.MEDIUM)
    status = Column(SQLEnum(RequirementStatus), default=RequirementStatus.DRAFT)
    confidence_score = Column(Float, default=0.0)
    ai_generated = Column(Boolean, default=False)
    tags = Column(ARRAY(String), default=[])
    version = Column(Integer, default=1)
    parent_id = Column(Integer, ForeignKey("requirements.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="requirements")
    source_message = relationship("Message", back_populates="requirements")
    comments = relationship("Comment", back_populates="requirement", cascade="all, delete-orphan")
    history = relationship("RequirementHistory", back_populates="requirement", cascade="all, delete-orphan")
    parent = relationship("Requirement", remote_side=[id], backref="children")

class RequirementHistory(Base):
    __tablename__ = "requirement_history"
    
    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id", ondelete="CASCADE"))
    content = Column(Text)
    changed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    change_type = Column(String)  # created, updated, status_changed
    version = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    requirement = relationship("Requirement", back_populates="history")

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id", ondelete="CASCADE"))
    author_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    requirement = relationship("Requirement", back_populates="comments")
    author = relationship("User", back_populates="comments")

class Conflict(Base):
    __tablename__ = "conflicts"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    requirement1_id = Column(Integer, ForeignKey("requirements.id", ondelete="CASCADE"))
    requirement2_id = Column(Integer, ForeignKey("requirements.id", ondelete="CASCADE"))
    description = Column(Text)
    similarity_score = Column(Float)
    conflict_type = Column(String)  # contradiction, duplicate, overlap
    resolved = Column(Boolean, default=False)
    resolution_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="conflicts")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    version = Column(Integer, default=1)
    content = Column(JSON)
    template_id = Column(String, default="default")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="documents")
