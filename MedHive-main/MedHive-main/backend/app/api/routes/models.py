from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
import json
import os
from datetime import datetime

from app.db.session import get_db
from app.models.ml_model import MLModel, Dataset, ModelPerformance
from app.models.user import User
from app.schemas.model import (
    MLModelCreate, 
    MLModelResponse, 
    MLModelUpdate, 
    DatasetCreate, 
    DatasetResponse
)
from app.api.routes.auth import get_current_user

router = APIRouter()

# ML Models endpoints
@router.get("/", response_model=List[MLModelResponse])
async def get_all_models(
    skip: int = 0,
    limit: int = 100,
    model_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all ML models with optional filters"""
    query = db.query(MLModel)
    
    if model_type:
        query = query.filter(MLModel.type == model_type)
    
    if status:
        query = query.filter(MLModel.status == status)
    
    models = query.offset(skip).limit(limit).all()
    return models

@router.get("/{model_id}", response_model=MLModelResponse)
async def get_model(
    model_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific ML model by ID"""
    model = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return model

@router.post("/", response_model=MLModelResponse)
async def create_model(
    model_data: MLModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new ML model"""
    if current_user.role.name not in ["admin", "data_provider"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create models"
        )
    
    db_model = MLModel(
        name=model_data.name,
        description=model_data.description,
        type=model_data.type,
        version=model_data.version,
        status="draft",
        huggingface_id=model_data.huggingface_id,
        created_by_id=current_user.id
    )
    
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    return db_model

@router.put("/{model_id}", response_model=MLModelResponse)
async def update_model(
    model_id: int,
    model_data: MLModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing ML model"""
    db_model = db.query(MLModel).filter(MLModel.id == model_id).first()
    
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Only admin or the creator can update the model
    if current_user.role.name != "admin" and db_model.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this model"
        )
    
    # Update model fields
    for key, value in model_data.dict(exclude_unset=True).items():
        setattr(db_model, key, value)
    
    db_model.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_model)
    
    return db_model

@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an ML model"""
    db_model = db.query(MLModel).filter(MLModel.id == model_id).first()
    
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Only admin or the creator can delete the model
    if current_user.role.name != "admin" and db_model.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this model"
        )
    
    db.delete(db_model)
    db.commit()
    
    return None

# Dataset endpoints
@router.get("/datasets", response_model=List[DatasetResponse])
async def get_all_datasets(
    skip: int = 0,
    limit: int = 100,
    data_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all datasets with optional filters"""
    query = db.query(Dataset)
    
    if data_type:
        query = query.filter(Dataset.data_type == data_type)
    
    # If not admin, only show own datasets for data providers
    if current_user.role.name != "admin":
        if current_user.role.name == "data_provider":
            query = query.filter(Dataset.data_provider_id == current_user.id)
        else:
            # Regular users only see approved datasets
            query = query.filter(Dataset.status == "approved")
    
    datasets = query.offset(skip).limit(limit).all()
    return datasets

@router.post("/datasets", response_model=DatasetResponse)
async def create_dataset(
    dataset_data: DatasetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new dataset"""
    if current_user.role.name not in ["admin", "data_provider"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to upload datasets"
        )
    
    db_dataset = Dataset(
        name=dataset_data.name,
        description=dataset_data.description,
        data_provider_id=current_user.id,
        data_type=dataset_data.data_type,
        size_bytes=dataset_data.size_bytes,
        num_samples=dataset_data.num_samples,
        metadata=dataset_data.metadata,
        status="pending" if current_user.role.name != "admin" else "approved"
    )
    
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    
    return db_dataset
