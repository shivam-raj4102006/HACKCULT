from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: str = Field(default="viewer", pattern="^(admin|researcher|viewer|verifier)$")
    organization: Optional[str] = "National Heritage Trust"

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password at least 6 characters")

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
