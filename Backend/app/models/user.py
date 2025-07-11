# app/models/user_model.py
from typing import Optional
from pydantic import BaseModel, Field # type: ignore
from datetime import datetime, timezone
from app.utils.pyobjectid import PyObjectId 
from app.enums.roles import Role
from app.utils.objectid import ObjectId # type: ignore


class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    role: Role = Role.STUDENT
    username: Optional[str] = Field(default=None, min_length=1, max_length=50)
    email: Optional[str] = None
    password: Optional[str] = Field(None, strip_whitespace=True, min_length=6)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) 
    updated_at: Optional[datetime] = None
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "use_enum_values": True,
        "from_attributes": True,
   
    }

    def to_dict(self, include_password: bool = False) -> dict:
        data = self.model_dump(exclude_none=True)
        if not include_password:
            data.pop("password", None)
        return data
