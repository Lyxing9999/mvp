from pydantic import BaseModel, Field # type: ignore
from datetime import datetime, timezone
from app.utils.objectid import ObjectId # type: ignore  
from app.enums.roles import FeedbackRole
from app.enums.category import Category
from app.enums.status import FeedbackStatus
from app.utils.pyobjectid import PyObjectId
class FeedbackResponseModel(BaseModel):
    __collection_name__ = "feedback_response"
    
    id: PyObjectId | None = Field(None, alias="_id")
    responder_id: str | None = None
    message: str | None = None
    responded_at: datetime | None = None


class FeedbackModel(BaseModel):
    
    id: PyObjectId | None = Field(None, alias="_id")
    sender_id: str
    receiver_id: str | None = None
    role: FeedbackRole
    category: Category
    message: str = Field(..., min_length=5, max_length=1000)
    status: FeedbackStatus
    response: FeedbackResponseModel | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {
        "extra": "allow",
        "from_attributes": True,
        "use_enum_values": True,
        "arbitrary_types_allowed": True, 
    }
