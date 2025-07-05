from typing import Optional
from pydantic import BaseModel, Field   # type: ignore
from datetime import datetime, timezone
from app.utils.objectid import ObjectId # type: ignore

class CourseModel(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    course_code: str
    course_title: str
    credits: Optional[int] = Field(default=0, ge=0)
    department: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "extra": "forbid",
        "populate_by_name": True,
    }
    
    @classmethod
    def create_minimal(cls, **overrides):
        data = {
            "course_code": "",
            "course_title": "",
            "credits": 0,
            "department": None,
            "description": None,
        }
        data.update(overrides)
        return cls(**data)
    
