from pydantic import (BaseModel, Field) # type: ignore
from typing import Optional
from datetime import datetime, timezone
from app.utils.objectid import ObjectId
from enums.roles import FeedbackRole
from enums.category import Category
from enums.status import FeedbackStatus

class FeedbackResponseModel(BaseModel):
    responder_id: Optional[str] = None
    message: Optional[str] = None
    responded_at: Optional[datetime] = None

class FeedbackModel(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    sender_id: str
    receiver_id: Optional[str] = None
    role: FeedbackRole
    category: Category
    message: str = Field(..., min_length=5, max_length=1000)
    status: FeedbackStatus
    response: Optional[FeedbackResponseModel] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "use_enum_values": True,
    }