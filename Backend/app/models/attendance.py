from typing import  Optional
from app.db import get_db
from datetime import date, datetime, timezone
from pydantic import BaseModel, Field # type: ignore
from enums.status import AttendanceStatus
from bson import ObjectId # type: ignore
class AttendanceRecordModel(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    student_id: str
    class_id: str
    date: date
    status: AttendanceStatus = AttendanceStatus.PRESENT
    recorded_by: Optional[str] = None 
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "use_enum_values": True,
    }