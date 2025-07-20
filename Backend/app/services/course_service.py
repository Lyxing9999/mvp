from app.models.course import CourseModel
from app.error.exceptions import NotFoundError, ValidationError, DatabaseError, ExceptionFactory, InternalServerError, AppBaseException, BadRequestError, ErrorCategory, ErrorSeverity , AppTypeError
from app.utils.objectid import ObjectId # type: ignore
from typing import Optional, List, Dict, Any , Union
from app.utils.dict_utils import flatten_dict
from datetime import datetime, timezone
from app.utils.console import console
from app.utils.model_utils import default_model_utils
from pymongo.database import Database # type: ignore
from abc import ABC, abstractmethod
from app.utils.convert import convert_serializable , convert_objectid_to_str
import logging

logger = logging.getLogger(__name__)

class CourseService(ABC):
    @abstractmethod
    def create_course(self, _id: ObjectId | str, data: Dict[str, Any]) -> Optional[CourseModel]:
        pass

class MongoCourseService(CourseService):
    def __init__(self, db: Database, collection_name: str = CourseModel._collection_name):
        self.db = db
        self.collection = self.db[collection_name]
        self.now = datetime.now(timezone.utc)
        self.model_utils =  default_model_utils

    def _to_course(self, data: Dict[str, Any]) -> Optional[CourseModel]:
        return self.model_utils.to_model(data, CourseModel)
    
    def _to_course_list(self, data: List[Dict[str, Any]]) -> List[CourseModel]:
        return [self._to_course(doc) for doc in data]
    
    def _initialize_update_history(self) -> List[datetime]:
        return [self.now]
    
    def _validate_object_id(self, id_val: Union[str, ObjectId, None]) -> ObjectId:
        return self.model_utils.validate_object_id(id_val)
    
    def _convert_to_response_model(self, data: Dict[str, Any]) -> Optional[CourseModel]:
        return self.model_utils.convert_to_response_model(data, CourseModel)

    def _convert_to_response_model_list(self, data_list: List[Dict[str, Any]]) -> List[CourseModel]:
        return [self._convert_to_response_model(doc) for doc in data_list]
    
    def _insert_many(self, docs: List[Dict[str, Any]]) -> List[ObjectId]:
        return self.model_utils.insert_many(docs)
    
    def _prepare_safe_update(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.model_utils.prepare_safe_update(update_data)
    
    def create_course(self, _id: ObjectId | str, data: Dict[str, Any]) -> Optional[CourseModel]:
        try:
            data = self._prepare_safe_update(data)
            data["created_at"] = self.now
            data["updated_at"] = self.now
            data["created_by"] = self._validate_object_id(_id)
            data["updated_by"] = self._validate_object_id(_id)
            data["update_history"] = self._initialize_update_history()
            inserted_ids = self._insert_many([data])
            return self._fetch_first_inserted(inserted_ids)
        except Exception as e:
            logger.error(f"Error creating course: {e}")
            raise InternalServerError(
                message="Failed to create course",
                error=str(e),
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.DATABASE,
            )
    
    def get_course_by_id(self, _id: ObjectId | str) -> Optional[CourseModel]:
        try:
            _id = self._validate_object_id(_id)
            course = self.collection.find_one({"_id": _id})
            if not course:
                raise NotFoundError(
                    message="Course not found",
                    severity=ErrorSeverity.ERROR,
                    category=ErrorCategory.DATABASE,
                )
            return self._convert_to_response_model(course)
        except Exception as e:
            logger.error(f"Error getting course by id: {e}")
            raise InternalServerError(
                message="Failed to get course by id",
                error=str(e),
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.DATABASE,
            )