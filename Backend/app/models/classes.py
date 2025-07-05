from datetime import datetime, timezone
from typing import  Optional, List
from pydantic import BaseModel, Field, HttpUrl  # type: ignore
from app.models.schedule import ScheduleItemModel  # type: ignore
from app.utils.objectid import ObjectId # type: ignore
from app.utils.pyobjectid import PyObjectId

class ClassInfoModel(BaseModel):
    course_code: str
    course_title: str
    lecturer: str
    email: Optional[str] = None
    phone_number: str
    hybrid: bool = False
    schedule: Optional[List[ScheduleItemModel]] = None
    credits: Optional[int] = 0
    link_telegram: Optional[HttpUrl] = None 
    department: Optional[str] = ""
    description: Optional[str] = ""
    year: Optional[int] = Field(default_factory=lambda: datetime.now().year)

class ClassesModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    class_info: Optional[ClassInfoModel] = None  
    students_enrolled: List[str] = Field(default_factory=list) 
    max_students: Optional[int] = 30 
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    update_history: List[datetime] = Field(default_factory=list)

    model_config = {
        "extra": "allow",
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "arbitrary_types_allowed": True,
    }
    def record_update(self):
        self.update_history.append(datetime.now(timezone.utc))

    @classmethod
    def create_from_class_info(cls, class_info: ClassInfoModel, **overrides):
        data = {
            "class_info": class_info,
            "students_enrolled": [],
            "max_students": 30,
            "created_at": datetime.now(timezone.utc),
            "update_history": [],
        }
        data.update(overrides)
        return cls(**data)

    @classmethod
    def create_minimal(cls, _id: PyObjectId, **overrides):
        data = {
            "_id": _id,
            "class_info": ClassInfoModel.create_minimal(),
            "students_enrolled": [],
            "max_students": 30,
            "created_at": datetime.now(timezone.utc),
            "update_history": [],
        }
        data.update(overrides)
        return cls(**data)
    