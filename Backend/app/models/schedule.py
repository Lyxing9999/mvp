from typing import Optional
from pydantic import BaseModel , Field # type: ignore
from app.enums.day import Day, Shift
from app.utils.objectid import ObjectId # type: ignore
from datetime import time # type: ignore
 
class ScheduleItemModel(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    day: Day
    shift: Shift
    start_time: time = Field(..., description="Format: HH:MM")
    end_time: time = Field(..., description="Format: HH:MM")
    room: str
    
    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "use_enum_values": True,
    }