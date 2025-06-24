from datetime import datetime, timezone
from typing import  Optional, List
from pydantic import BaseModel, Field, HttpUrl  # type: ignore
from app.models.schedule import ScheduleItem  # type: ignore
from bson import ObjectId # type: ignore
class ClassInfoModel(BaseModel):
    course_code: str
    course_title: str
    lecturer: str
    email: Optional[str] = None
    phone_number: str
    hybrid: bool = False
    schedule: Optional[List[ScheduleItem]] = None
    credits: Optional[int] = 0
    link_telegram: Optional[HttpUrl] = None 
    department: Optional[str] = ""
    description: Optional[str] = ""
    year: Optional[int] = Field(default_factory=lambda: datetime.now().year)

class ClassModel(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    class_id: str = Field(default_factory=lambda: str(ObjectId()))
    class_info: ClassInfoModel
    students_enrolled: List[str] = Field(default_factory=list) 
    max_students: Optional[int] = 30 
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    update_history: List[datetime] = Field(default_factory=list)
    model_config = {
        "extra": "forbid",
        "arbitrary_types_allowed": True,
    }
    def record_update(self):
        self.update_history.append(datetime.now(timezone.utc))

        