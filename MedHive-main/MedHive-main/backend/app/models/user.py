import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Boolean, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="role")
    
    def __repr__(self):
        return f"Role(id={self.id}, name={self.name})"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    role = relationship("Role", back_populates="users")
    datasets = relationship("Dataset", back_populates="data_provider")
    ml_models = relationship("MLModel", back_populates="created_by")
    fl_participants = relationship("FLParticipant", back_populates="user")
    chat_history = relationship("ChatHistory", back_populates="user")
    
    def __repr__(self):
        return f"User(id={self.id}, email={self.email}, role_id={self.role_id})"