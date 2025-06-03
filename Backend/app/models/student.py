from datetime import datetime, timezone, date
from pydantic import BaseModel, EmailStr, Field  # type: ignore
from typing import Optional, List, Dict
from app.models.user import UserModel
from app.enums.status import AttendanceStatus
from app.utils.objectid import ObjectId
class StudentInfoModel(BaseModel):
    student_id: str
    grade: Optional[str] = None
    class_ids: List[str] = Field(default_factory=list)
    major: Optional[str] = None
    birth_date: Optional[date] = None
    batch: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    attendance_record: Dict[str, AttendanceStatus] = Field(default_factory=dict)
    courses_enrolled: List[str] = Field(default_factory=list)
    scholarships: List[str] = Field(default_factory=list)
    current_gpa: float = 0.0
    remaining_credits: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "use_enum_values": True,
    }

class Student(UserModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    student_info: StudentInfoModel
  
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }