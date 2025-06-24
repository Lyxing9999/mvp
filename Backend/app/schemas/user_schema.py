from pydantic import BaseModel, Field # type: ignore

from typing import Optional
from datetime import datetime, timezone
from app.enums.roles import Role


class UserCreateSchema(BaseModel):
    username: str
    email: Optional[str] = None
    password: str
    role: Role
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

class UserResponseSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[Role] = None
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }