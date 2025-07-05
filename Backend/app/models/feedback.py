from pydantic import (BaseModel, Field) # type: ignore
from typing import Optional
from datetime import datetime, timezone
from app.utils.objectid import ObjectId # type: ignore  
from enums.roles import FeedbackRole
from enums.category import Category
from enums.status import FeedbackStatus

class FeedbackResponseModel(BaseModel):
    responder_id: Optional[str] = None
    message: Optional[str] = None
    responded_at: Optional[datetime] = None

    @classmethod
    def create_minimal(cls, **overrides):
        data = {
            "responder_id": None,
            "message": None,
            "responded_at": None,
        }
        data.update(overrides)
        return cls(**data)

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

    @classmethod
    def create_minimal(cls, autofilled_data: Optional[dict] = None, **overrides):
        data = {
            "sender_id": "",
            "receiver_id": None,
            "role": FeedbackRole.STUDENT,
            "category": Category.SUGGESTION,
            "message": "",
            "status": FeedbackStatus.UNREAD,
            "response": FeedbackResponseModel.create_minimal(),
            "created_at": datetime.now(timezone.utc),
        }
        if autofilled_data:
            data.update(autofilled_data)
        data.update(overrides)
        return cls(**data)
