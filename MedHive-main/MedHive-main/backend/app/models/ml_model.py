from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base

class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String, nullable=False)
    version = Column(String, nullable=False)
    status = Column(String, default="draft")
    model_path = Column(Text, nullable=True)
    huggingface_id = Column(String, nullable=True)
    accuracy = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    precision_score = Column(Float, nullable=True)
    recall_score = Column(Float, nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = relationship("User", back_populates="ml_models")
    rounds = relationship("FLRound", back_populates="model")
    model_performances = relationship("ModelPerformance", back_populates="model")
    
    def __repr__(self):
        return f"MLModel(id={self.id}, name={self.name}, type={self.type}, version={self.version})"

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    data_provider_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    size_bytes = Column(Integer, nullable=True)
    num_samples = Column(Integer, nullable=True)
    data_type = Column(String, nullable=True)
    metadata = Column(JSONB, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    data_provider = relationship("User", back_populates="datasets")
    model_performances = relationship("ModelPerformance", back_populates="test_dataset")
    
    def __repr__(self):
        return f"Dataset(id={self.id}, name={self.name}, data_provider_id={self.data_provider_id})"

class ModelPerformance(Base):
    __tablename__ = "model_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml_models.id"))
    round_id = Column(Integer, ForeignKey("fl_rounds.id"), nullable=True)
    accuracy = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    precision_score = Column(Float, nullable=True)
    recall_score = Column(Float, nullable=True)
    loss = Column(Float, nullable=True)
    test_dataset_id = Column(Integer, ForeignKey("datasets.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    model = relationship("MLModel", back_populates="model_performances")
    round = relationship("FLRound", back_populates="performance")
    test_dataset = relationship("Dataset", back_populates="model_performances")
    
    def __repr__(self):
        return f"ModelPerformance(id={self.id}, model_id={self.model_id}, accuracy={self.accuracy})" 