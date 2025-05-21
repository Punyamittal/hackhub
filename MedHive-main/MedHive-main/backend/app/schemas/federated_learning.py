from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, UUID4

# Federated Learning Round schemas
class FLRoundBase(BaseModel):
    model_id: int

class FLRoundCreate(FLRoundBase):
    pass

class FLRoundUpdate(BaseModel):
    status: Optional[str] = None
    aggregated_model_path: Optional[str] = None

class FLRoundResponse(FLRoundBase):
    id: int
    round_number: int
    status: str
    aggregated_model_path: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Federated Learning Participant schemas
class FLParticipantBase(BaseModel):
    round_id: int
    user_id: UUID4

class FLParticipantCreate(FLParticipantBase):
    pass

class FLParticipantUpdate(BaseModel):
    status: str
    local_model_path: Optional[str] = None
    training_metrics: Optional[Dict[str, Any]] = None

class FLParticipantResponse(FLParticipantBase):
    id: int
    status: str
    local_model_path: Optional[str] = None
    training_metrics: Optional[Dict[str, Any]] = None
    training_start: Optional[datetime] = None
    training_end: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 