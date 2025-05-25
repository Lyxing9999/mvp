from app.models.user import User
from datetime import datetime , timezone

class Course:
    def __init__(self, data: dict):
        if isinstance(data, dict):
            self.name = data.get("name", "")
            self.score = data.get("score", None)
        else:
            self.name = str(data)
            self.score = None
    def to_dict(self):
        return {
            "name": self.name,
            "score": self.score
        }
class StudentInfo:
    def __init__(self, data: dict):
        if not isinstance(data, dict): data = {} 
        self.grade = data.get("grade", "")
        self.major = data.get("major", "")
        self.school_id = data.get("school_id", "")
        self.courses = [Course(c) for c in data.get("courses", [])]
    def to_dict(self):
        return{
            "grade": self.grade,
            "major": self.major,
            "school_id" : self.school_id,
            "courses" : [c.to_dict() for c in self.courses]
        }
        
        
        
        
        
        
class Student(User):
    def __init__(self, data: dict):
        if not isinstance(data, dict): data = {} 
        super().__init__(data)
        self.phone_number: str = data.get("phone_number", "")
        self.student_info = StudentInfo(data.get("student_info", {}))
    def to_dict(self) -> dict :
        base_dict = super().to_dict()
        base_dict["phone_number"] = self.phone_number
        base_dict["student_info"] = self.student_info.to_dict()
        return base_dict
    
    
