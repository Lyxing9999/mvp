from app.utils.objectid import ObjectId
from typing import Optional , List, Dict, Any, Union
from app.models.grade import GradeModel
from pymongo.errors import PyMongoError # type: ignore
from pymongo.database import Database # type: ignore
from app.error.exceptions import NotFoundError, ValidationError, DatabaseError, AuthenticationError, BadRequestError, InternalServerError, UnauthorizedError, ForbiddenError, ExceptionFactory, AppBaseException, ErrorSeverity, ErrorCategory # type: ignore
from abc import ABC, abstractmethod
from app.utils.model_utils import default_model_utils
from app.utils.pyobjectid import PyObjectId
import logging

logger = logging.getLogger(__name__)

class GradeService(ABC):
    @abstractmethod
    def create(self, student_id: PyObjectId, class_id: PyObjectId, data: Dict[str, Any]) -> Optional[GradeModel]: 
        pass

    @abstractmethod
    def get_by_student_class(self, student_id: str, class_id: str) -> Optional[GradeModel]: 
        pass

    @abstractmethod
    def update(self, grade_id: str, update_data: dict) -> GradeModel: 
        pass

    @abstractmethod
    def delete(self, grade_id: str) -> GradeModel: 
        pass


class MongoGradeService(GradeService):
    def __init__(self, db: Database):
        self.db = db
        self.model_utils = default_model_utils
        self.collection = self.db.grades

    def _to_grade(self, data: Dict[str, Any]) -> Optional[GradeModel]:
        return self.model_utils.to_model(data, GradeModel)

    def _to_grade_list(self, data_list: List[Dict[str, Any]]) -> List[GradeModel]:
        return self.model_utils.to_model_list(data_list, GradeModel)

    def _to_objectid(self, id_val: Union[str, ObjectId]) -> Optional[ObjectId]:
        return self.model_utils.validate_object_id(id_val)

    def _prepare_safe_update(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.model_utils.prepare_safe_update(update_data)
    
    def _convert_to_response_model(self, data: Dict[str, Any]) -> Optional[GradeModel]:
        return self.model_utils.convert_to_response_model(data, GradeModel)


    def create_grade(self, student_id: ObjectId, teacher_id: ObjectId, class_id: ObjectId, course_id: ObjectId, data: Dict[str, Any]) -> Optional[GradeModel]:
        ids = {
            "student_id": student_id,
            "teacher_id": teacher_id,
            "class_id": class_id,
            "course_id": course_id
        }
        validated_ids = {}
        for field, id_val in ids.items():
            validated_id = self._to_objectid(id_val)
            if not validated_id:
                raise ExceptionFactory.validation_failed(field=field, value=id_val, reason=f"Invalid {field} format")
            validated_ids[field] = validated_id

        try:
            data.update(validated_ids)
            
            grade = self._to_grade(data)
            if not grade:
                raise ExceptionFactory.validation_failed(field="data", value=data, reason="Invalid grade data")

            result = self.collection.insert_one(grade.model_dump(by_alias=True))
            if not result.acknowledged:
                raise InternalServerError("Insert failed")
            to_doc = self.collection.find_one({"_id": result.inserted_id})
            return self._convert_to_response_model(to_doc) if to_doc else None

        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError("Failed to create grade", cause=e)

    def get_grade_by_id(self, _id: Union[str, ObjectId]) -> Optional[GradeModel]:
        validated_id = self._to_objectid(_id)
        result =  self.collection.find_one({"_id": validated_id})
        if not result:
            raise NotFoundError(message="Grade not found", severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE, status_code=404)
        return self._convert_to_response_model(result)
    
    def get_grade_by_student_class(self, student_id: str, class_id: str) -> Optional[GradeModel]:
        pass
    
    def update_grade(self, _id: Union[str, ObjectId], update_data: Dict[str, Any]) -> Optional[GradeModel]:
        # take Object or str and update by POST method
        pass
    def delete_grade(self, _id: Union[str, ObjectId]) -> bool:
        return self.collection.delete_one({"_id": _id})

