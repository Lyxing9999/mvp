from app.models.student import Student # type: ignore
from app.db import get_db
from typing import Optional, List
from app.utils.objectid import ObjectId # type: ignore
from app.models.classes import ClassesModel # type: ignore
db = get_db()


class StudentService:
    @staticmethod
    def _to_student(data: Optional[dict]) -> Optional[Student]:
        if not isinstance(data, dict):
            return None
        return Student(**data)
    
    @staticmethod
    def _to_students(data_list: list) -> list[Student]:
        
        return [Student(**data) for data in data_list if isinstance(data, dict)]

    
    @classmethod
    def get_student_info_by_id(cls, student_id: str) -> Optional[Student]:
        if not student_id:
            return None
        try:
            student_data = db.students.find_one({"_id": ObjectId(student_id)})
            return cls._to_student(student_data)
        except Exception as e:
            print(f"Error fetching student by ID: {e}")
            return None
    @classmethod
    def get_student_classes(cls, student: Student) -> List[ClassesModel]:
        try:
            class_ids = getattr(student.student_info, "class_ids", [])
            if not class_ids:
                return []
            object_ids = [ObjectId(cid) for cid in class_ids if ObjectId.is_valid(cid)]
            classes_data = db.classes.find({"_id": {"$in": object_ids}})
            return [ClassesModel(**c) for c in classes_data]
        except Exception as e:
            print(f"Error fetching student classes: {e}")
            return []