from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, UUID4, Field

# ML Model schemas
class MLModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str  # e.g., 'ecg', 'pneumonia', 'breast_cancer'
    version: str

class MLModelCreate(MLModelBase):
    huggingface_id: Optional[str] = None

class MLModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    huggingface_id: Optional[str] = None
    accuracy: Optional[float] = None
    f1_score: Optional[float] = None
    precision_score: Optional[float] = None
    recall_score: Optional[float] = None

class MLModelResponse(MLModelBase):
    id: int
    status: str
    model_path: Optional[str] = None
    huggingface_id: Optional[str] = None
    accuracy: Optional[float] = None
    f1_score: Optional[float] = None
    precision_score: Optional[float] = None
    recall_score: Optional[float] = None
    created_by_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Dataset schemas
class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None
    data_type: str  # e.g., 'image', 'time_series', 'tabular'
    size_bytes: Optional[int] = None
    num_samples: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class DatasetCreate(DatasetBase):
    pass

class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DatasetResponse(DatasetBase):
    id: int
    data_provider_id: UUID4
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Model Performance schemas
class ModelPerformanceBase(BaseModel):
    model_id: int
    accuracy: Optional[float] = None
    f1_score: Optional[float] = None
    precision_score: Optional[float] = None
    recall_score: Optional[float] = None
    loss: Optional[float] = None
    test_dataset_id: int

class ModelPerformanceCreate(ModelPerformanceBase):
    round_id: Optional[int] = None

class ModelPerformanceResponse(ModelPerformanceBase):
    id: int
    round_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True 