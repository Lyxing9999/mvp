from bson import ObjectId  # type: ignore
from app.db import get_db
from typing import Optional , List  
from app.models.grade import GradeModel
from pymongo.errors import PyMongoError # type: ignore
db = get_db()
class GradeService:
    @staticmethod
    def _to_grade(data: Optional[dict]) -> Optional[GradeModel]:
        if not isinstance(data, dict):
            return None
        return GradeModel(**data)

    @staticmethod
    def create_grade(data: dict) -> dict:
        try:
            grade = GradeModel(**data)
            doc = grade.to_dict()
            result = db.grades.insert_one(doc)
            return {"_id": str(result.inserted_id), **doc}
        except PyMongoError as e:
            raise Exception("Database insert failed") from e
    
    @staticmethod
    def get_grade_by_student_class(student_id: str, class_id: str) -> Optional[GradeModel]:
        if not student_id or not class_id:
            return None
        grade_data = db.grades.find_one({"student_id": student_id, "class_id": class_id})
        return GradeService._to_grade(grade_data)

    @staticmethod
    def update_grade(grade_id: str, update_data: dict) -> dict:
        try:
            result = db.grades.update_one(
                {"_id": ObjectId(grade_id)},
                {"$set": update_data}
            )
            if result.matched_count == 0:
                return {"msg": "Grade not found"}
            return {"msg": "Grade updated successfully"}
        except PyMongoError as e:
            raise Exception("Failed to update grade") from e

    @staticmethod
    def delete_grade(grade_id: str) -> dict:
        try:
            result = db.grades.delete_one({"_id": ObjectId(grade_id)})
            if result.deleted_count == 0:
                return {"msg": "Grade not found"}
            return {"msg": "Grade deleted successfully"}
        except PyMongoError as e:
            raise Exception("Failed to delete grade") from e

    @staticmethod
    def get_grades_by_student_id(student_id: str) -> List[GradeModel]:
        if not student_id:
            return []
        grades_data = db.grades.find({"student_id": student_id})
        return [GradeService._to_grade(grade) for grade in grades_data]
    
    @staticmethod
    def get_grades_by_class_id(class_id: str) -> List[GradeModel]:
        if not class_id:
            return []
        grades_data = db.grades.find({"class_id": class_id})
        return [GradeService._to_grade(grade) for grade in grades_data]
    
    @staticmethod
    def get_grades_by_student_id_and_class_id(student_id: str, class_id: str) -> List[GradeModel]:
        if not student_id or not class_id:
            return []
        grades_data = db.grades.find({"student_id": student_id, "class_id": class_id})
        return [GradeService._to_grade(grade) for grade in grades_data]
    
    @staticmethod
    def get_grades_by_student_id_and_course_id(student_id: str, course_id: str) -> List[GradeModel]:
        if not student_id or not course_id:
            return []
        grades_data = db.grades.find({"student_id": student_id, "course_id": course_id})
        return [GradeService._to_grade(grade) for grade in grades_data]
    
    @staticmethod
    def get_grades_by_class_id_and_course_id(class_id: str, course_id: str) -> List[GradeModel]:
        if not class_id or not course_id:
            return []
        grades_data = db.grades.find({"class_id": class_id, "course_id": course_id})
        return [GradeService._to_grade(grade) for grade in grades_data]