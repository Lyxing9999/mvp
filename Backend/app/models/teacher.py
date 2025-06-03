from typing import List, Optional
from pydantic import BaseModel, Field # type: ignore
from datetime import datetime , timezone
from app.utils.objectid import ObjectId
class TeacherInfo(BaseModel):
    teacher_id: str
    lecturer_name: Optional[str] = None
    subjects: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    model_config = {
        "extra": "forbid"
    }

class TeacherModel(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str 
    phone_number: Optional[str] = None 
    teacher_info: TeacherInfo
    model_config = {
        "extra": "forbid",
        "populate_by_name": True
    }
