from datetime import datetime, timezone
from typing import Optional
from pydantic import (BaseModel, Field, computed_field)  # type: ignore
from bson import ObjectId # type: ignore
class GradeModel(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    teacher_id: str
    student_id: str
    student_name: Optional[str] = None
    class_id: str 
    course_id: Optional[str] = None
    
    attendance: Optional[float] = 0.0
    assignment: Optional[float] = 0.0
    quiz: Optional[float] = 0.0
    project: Optional[float] = 0.0
    midterm: Optional[float] = 0.0
    final_exam: Optional[float] = 0.0 
    extra_exam: Optional[float] = 0.0
    
    term: Optional[str] = "Term 1"
    remark: Optional[str] = None
    
    created_at:datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    @computed_field(include=True)
    def total(self) -> float:
        return (
            (self.attendance or 0) +
            (self.assignment or 0) +
            (self.quiz or 0) +
            (self.project or 0) +
            (self.midterm or 0) +
            (self.final_exam or 0) + 
            (self.extra_exam or 0)
        )
    def is_passing(self, passing_grade: float = 60.0) -> bool:
        return self.total >= passing_grade
        
    def get_letter_grade(self) -> str:
        
        total = self.total
        if total >= 97:
            return "A+"
        elif total >= 93:
            return "A"
        elif total >= 90:
            return "A-"
        elif total >= 87:
            return "B+"
        elif total >= 83:
            return "B"
        elif total >= 80:
            return "B-"
        elif total >= 77:
            return "C+"
        elif total >= 73:
            return "C"
        elif total >= 70:
            return "C-"
        elif total >= 67:
            return "D+"
        elif total >= 63:
            return "D"
        elif total >= 60:
            return "D-"
        else:
            return "F"

        
    model_config = {
        "extra": "forbid",
        "from_attributes": True,
    }
