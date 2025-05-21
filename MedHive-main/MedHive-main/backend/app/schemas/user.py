from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, UUID4, Field

# Role schemas
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    organization: Optional[str] = None
    role_id: int = Field(default=4)  # Default to regular user

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    organization: Optional[str] = None
    active: Optional[bool] = None
    role_id: Optional[int] = None

class UserResponse(UserBase):
    id: UUID4
    active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    role: Optional[RoleResponse] = None

    class Config:
        from_attributes = True 