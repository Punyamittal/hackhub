from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, Role
from app.schemas.user import UserResponse, UserUpdate
from app.api.routes.auth import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/roles", response_model=List[Role])
async def get_all_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available roles (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    roles = db.query(Role).all()
    return roles

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all users (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/data-providers", response_model=List[UserResponse])
async def get_data_providers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all data provider users"""
    if current_user.role.name not in ["admin", "data_provider"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    data_provider_role = db.query(Role).filter(Role.name == "data_provider").first()
    if not data_provider_role:
        return []
    
    users = db.query(User).filter(User.role_id == data_provider_role.id).all()
    return users

@router.get("/contributors", response_model=List[UserResponse])
async def get_contributors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all contributor users"""
    if current_user.role.name not in ["admin", "contributor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    contributor_role = db.query(Role).filter(Role.name == "contributor").first()
    if not contributor_role:
        return []
    
    users = db.query(User).filter(User.role_id == contributor_role.id).all()
    return users
