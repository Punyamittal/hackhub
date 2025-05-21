from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import requests
import os
import json
from datetime import datetime

from app.db.session import get_db
from app.models.federated_learning import FLRound, FLParticipant
from app.models.ml_model import MLModel
from app.models.user import User
from app.schemas.federated_learning import (
    FLRoundCreate, 
    FLRoundResponse, 
    FLParticipantResponse,
    FLParticipantUpdate
)
from app.core.config import settings
from app.api.routes.auth import get_current_user

router = APIRouter()

# FLRound endpoints
@router.get("/rounds", response_model=List[FLRoundResponse])
async def get_all_rounds(
    skip: int = 0,
    limit: int = 100,
    model_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all federated learning rounds with optional filters"""
    query = db.query(FLRound)
    
    if model_id:
        query = query.filter(FLRound.model_id == model_id)
    
    if status:
        query = query.filter(FLRound.status == status)
    
    rounds = query.order_by(FLRound.round_number.desc()).offset(skip).limit(limit).all()
    return rounds

@router.get("/rounds/{round_id}", response_model=FLRoundResponse)
async def get_round(
    round_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific federated learning round by ID"""
    fl_round = db.query(FLRound).filter(FLRound.id == round_id).first()
    if not fl_round:
        raise HTTPException(status_code=404, detail="Federated learning round not found")
    
    return fl_round

@router.post("/rounds", response_model=FLRoundResponse)
async def create_round(
    round_data: FLRoundCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new federated learning round"""
    if current_user.role.name not in ["admin", "data_provider"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create FL rounds"
        )
    
    # Verify the model exists
    model = db.query(MLModel).filter(MLModel.id == round_data.model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Get the highest round number for this model
    latest_round = db.query(FLRound).filter(
        FLRound.model_id == round_data.model_id
    ).order_by(FLRound.round_number.desc()).first()
    
    new_round_number = 1
    if latest_round:
        new_round_number = latest_round.round_number + 1
    
    # Create new round
    new_round = FLRound(
        model_id=round_data.model_id,
        round_number=new_round_number,
        status="pending",
        start_time=datetime.utcnow()
    )
    
    db.add(new_round)
    db.commit()
    db.refresh(new_round)
    
    # Add participants in the background
    background_tasks.add_task(add_participants_to_round, new_round.id, db)
    
    return new_round

@router.put("/rounds/{round_id}/start", response_model=FLRoundResponse)
async def start_round(
    round_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a federated learning round"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can start FL rounds"
        )
    
    fl_round = db.query(FLRound).filter(FLRound.id == round_id).first()
    if not fl_round:
        raise HTTPException(status_code=404, detail="Federated learning round not found")
    
    if fl_round.status != "pending":
        raise HTTPException(status_code=400, detail=f"Round is already in {fl_round.status} state")
    
    # Check if we have enough participants
    participants_count = db.query(FLParticipant).filter(
        FLParticipant.round_id == round_id,
        FLParticipant.status == "accepted"
    ).count()
    
    if participants_count < 2:  # Minimum required for federated learning
        raise HTTPException(
            status_code=400, 
            detail=f"Not enough participants ({participants_count}). Minimum 2 required."
        )
    
    # Update round status
    fl_round.status = "in_progress"
    db.commit()
    db.refresh(fl_round)
    
    # Here we would trigger the actual federated learning process
    # This would normally call the federated learning server
    
    return fl_round

# FLParticipant endpoints
@router.get("/participants", response_model=List[FLParticipantResponse])
async def get_all_participants(
    round_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all federated learning participants with optional filters"""
    query = db.query(FLParticipant)
    
    if round_id:
        query = query.filter(FLParticipant.round_id == round_id)
    
    if status:
        query = query.filter(FLParticipant.status == status)
    
    # If user is not admin, only show own participations
    if current_user.role.name != "admin":
        query = query.filter(FLParticipant.user_id == current_user.id)
    
    participants = query.all()
    return participants

@router.put("/participants/{participant_id}/respond", response_model=FLParticipantResponse)
async def respond_to_invitation(
    participant_id: int,
    response: FLParticipantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Respond to a federated learning invitation (accept/decline)"""
    participant = db.query(FLParticipant).filter(FLParticipant.id == participant_id).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    # Check if this is the current user's invitation
    if participant.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only respond to your own invitations"
        )
    
    # Check if the status is valid
    if response.status not in ["accepted", "declined"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid status. Must be 'accepted' or 'declined'"
        )
    
    # Check if the round is still pending
    fl_round = db.query(FLRound).filter(FLRound.id == participant.round_id).first()
    if fl_round.status != "pending":
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot respond to invitation when round is in {fl_round.status} state"
        )
    
    # Update participant status
    participant.status = response.status
    db.commit()
    db.refresh(participant)
    
    return participant

@router.put("/participants/{participant_id}/complete", response_model=FLParticipantResponse)
async def complete_training(
    participant_id: int,
    training_metrics: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a participant's training as complete"""
    participant = db.query(FLParticipant).filter(FLParticipant.id == participant_id).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    # Check if this is the current user's participation
    if participant.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only complete your own training"
        )
    
    # Check if the round is in progress
    fl_round = db.query(FLRound).filter(FLRound.id == participant.round_id).first()
    if fl_round.status != "in_progress":
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot complete training when round is in {fl_round.status} state"
        )
    
    # Update participant
    participant.status = "completed"
    participant.training_metrics = training_metrics
    participant.training_end = datetime.utcnow()
    db.commit()
    db.refresh(participant)
    
    # Check if all participants have completed
    incomplete_count = db.query(FLParticipant).filter(
        FLParticipant.round_id == fl_round.id,
        FLParticipant.status == "accepted"
    ).count()
    
    if incomplete_count == 0:
        # All participants have completed, mark round as completed
        fl_round.status = "completed"
        fl_round.end_time = datetime.utcnow()
        db.commit()
    
    return participant

# Helper functions (would normally be in a separate module)
def add_participants_to_round(round_id: int, db: Session):
    """Add eligible participants to a round (contributor role users)"""
    # Get the round
    fl_round = db.query(FLRound).filter(FLRound.id == round_id).first()
    if not fl_round:
        return
    
    # Find users with contributor role
    from sqlalchemy.orm import joinedload
    contributor_users = db.query(User).join(User.role).filter(
        User.role.has(name="contributor"),
        User.active == True
    ).all()
    
    # Add them as participants
    for user in contributor_users:
        participant = FLParticipant(
            round_id=round_id,
            user_id=user.id,
            status="invited",
            training_start=None,
            training_end=None
        )
        db.add(participant)
    
    db.commit() 