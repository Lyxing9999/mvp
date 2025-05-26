from app.models.user_model import User
from typing import List


class TeacherInfo:
    def __init__(self, data: dict):
        if not isinstance(data, dict): data = {} 
        self.teacher_id: str = data.get("teacher_id", "")
        self.subjects: List[str] = data.get ("subjects", [])    
    def to_dict(self):
        return{
            "teacher_id" : self.teacher_id,
            "subjects" : self.subjects,
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
    