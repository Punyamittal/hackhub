from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Integer, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, VECTOR
from sqlalchemy.orm import relationship

from app.db.session import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    is_user = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chat_history")
    
    def __repr__(self):
        return f"ChatHistory(id={self.id}, user_id={self.user_id}, is_user={self.is_user})"

class VectorEmbedding(Base):
    __tablename__ = "vector_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    embedding = Column(VECTOR(1536))  # Using vector type for embeddings
    content = Column(Text, nullable=False)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"VectorEmbedding(id={self.id}, content_id={self.content_id}, content_type={self.content_type})" 