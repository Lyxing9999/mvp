from app.models.user import User
from typing import List

class Schedule:
    def __init__(self, data: dict):
        if not isinstance(data, dict): data = {} 
        self.day: str = data.get("day", "")
        self.time: str = data.get("time", "")
        self.subject: str = data.get("subject", "")
        self.class_id: str = data.get("class_id", "")
        
    def to_dict(self):
        return {
            "day": self.day,
            "time": self.time,
            "subject": self.subject,
            "class_id": self.class_id
        }



class TeacherInfo:
    def __init__(self, data: dict):
        if not isinstance(data, dict): data = {} 
        self.employee_id: str = data.get("employee_id", "")
        self.subjects: List[str] = data.get ("subjects", [])    
        self.schedule: List[Schedule] = [Schedule(s) for s in data.get("schedule", [])]
    def to_dict(self):
        return{
            "employee_id" : self.employee_id,
            "subjects" : self.subjects,
            "schedule" : [s.to_dict() for s in self.schedule]
        }
        
class Teacher(User):
    def __init__(self, data):
        if not isinstance(data, dict): data = {} 
        super().__init__(data)
        self.phone_number:str = data.get('phone_number', "")
        self.teacher_info = TeacherInfo(data.get("teacher_info", {}))
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["phone_number"] = self.phone_number
        base_dict["teacher_info"] = self.teacher_info.to_dict()
        return base_dict
    