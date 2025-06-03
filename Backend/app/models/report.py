from pydantic import BaseModel, Field # type: ignore
from typing import Optional
from datetime import datetime, timezone
from enums.report import TargetType, ReportReason, Severity
from enums.status import ReportStatus
from bson import ObjectId  # type: ignore
class ReportModel(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    reporter_id: str 
    target_id: Optional[str] = None
    target_type: TargetType
    reason: ReportReason
    description: str = Field(..., min_length = 5, max_length = 1000)
    severity: Severity = Severity.MEDIUM
    status: ReportStatus = ReportStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "use_enum_values": True,
    }