from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base

class FLRound(Base):
    __tablename__ = "fl_rounds"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml_models.id"))
    round_number = Column(Integer, nullable=False)
    status = Column(String, default="pending")
    aggregated_model_path = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    model = relationship("MLModel", back_populates="rounds")
    participants = relationship("FLParticipant", back_populates="round")
    performance = relationship("ModelPerformance", back_populates="round")
    
    def __repr__(self):
        return f"FLRound(id={self.id}, model_id={self.model_id}, round_number={self.round_number})"

class FLParticipant(Base):
    __tablename__ = "fl_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    round_id = Column(Integer, ForeignKey("fl_rounds.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    status = Column(String, default="invited")
    local_model_path = Column(Text, nullable=True)
    training_metrics = Column(JSONB, nullable=True)
    training_start = Column(DateTime, nullable=True)
    training_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    round = relationship("FLRound", back_populates="participants")
    user = relationship("User", back_populates="fl_participants")
    
    def __repr__(self):
        return f"FLParticipant(id={self.id}, round_id={self.round_id}, user_id={self.user_id}, status={self.status})" 