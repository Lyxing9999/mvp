from typing import List, Optional
from pydantic import BaseModel, Field   # type: ignore 
from datetime import datetime, timezone
from app.utils.pyobjectid import PyObjectId
from app.utils.objectid import ObjectId  # type: ignore

class TeacherInfoModel(BaseModel):
    lecturer_id: str | None = None
    lecturer_name: str | None = None
    subjects: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) 
    updated_at: Optional[datetime] = None

    model_config = {
        "extra": "ignore",  
        "arbitrary_types_allowed": True,
    }

    @classmethod
    def create_minimal(cls, **overrides):
        data = {
            "lecturer_id":  None,
            "lecturer_name": None,
            "subjects": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
        }
        data.update(overrides)
        return cls(**data)

class TeacherModel(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    phone_number: Optional[str] = None
    teacher_info: TeacherInfoModel

    model_config = {
            "from_attributes": True,
            "populate_by_name": True,
            "arbitrary_types_allowed": True,
            "json_encoders": {ObjectId: str, PyObjectId: str},    
    }
        

    
    @classmethod
    def create_minimal(cls, _id: PyObjectId, **overrides):
        teacher_info = TeacherInfoModel.create_minimal()
        data = {
            "_id": _id,
            "phone_number": None,
            "teacher_info": teacher_info,
        }
        data.update(overrides)
        return cls(**data)