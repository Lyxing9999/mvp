from app.models.classes import ClassesModel, ClassInfoModel
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

class ClassesService(ABC):
    @abstractmethod
    def create_classes(self, _id: ObjectId | str, data: Union[List[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, Any]:
        pass



class MongoClassesService(ClassesService):
    def __init__(self, db: Database, collection_name: str = ClassesModel._collection_name):
        self.db = db
        self.collection = self.db[collection_name]
        self.now = datetime.now(timezone.utc)
        self.model_utils =  default_model_utils

    def _to_classes(self, data: Dict[str, Any]) -> Optional[ClassesModel]:
        return self.model_utils.to_model(data, ClassesModel)
    
    def _to_classes_list(self, data: List[Dict[str, Any]]) -> List[ClassesModel]:
        return [self._convert_objectid_dict(doc) for doc in data]

    def _initialize_update_history(self) -> List[datetime]:
        return [self.now]

    def _validate_object_id(self, id_val: Union[str, ObjectId, None]) -> ObjectId:
        return self.model_utils.validate_object_id(id_val)

    def _convert_to_response_model(self, data: Dict[str, Any]) -> Optional[ClassesModel]:
        return self.model_utils.convert_to_response_model(data, ClassesModel)
    
    
    
    def _convert_to_response_model_list(self, data_list: List[Dict[str, Any]]) -> List[ClassesModel]:
        return self.model_utils.convert_to_response_model_list(data_list, ClassesModel)
    
    def _fetch_first_inserted(self, inserted_ids: List[ObjectId]) -> ClassesModel:
        if not inserted_ids:
            raise NotFoundError(
                message="No classes inserted",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
                status_code=404
            )
        raw_doc = self.collection.find_one({"_id": inserted_ids[0]})
        if not raw_doc:
            raise NotFoundError(message="No classes inserted", severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE, status_code=404)
        return self._convert_to_response_model(raw_doc)
    
    
     
    def _insert_many(self, docs: List[Dict[str, Any]]) -> List[ObjectId]:
        result = self.collection.insert_many(docs)
        if not result.acknowledged:
            raise InternalServerError("Failed to insert classes", details={"docs": docs})
        return result.inserted_ids


    def create_classes(self, created_by: ObjectId | str, data: Union[List[Dict[str, Any]], Dict[str, Any]]) -> Optional[ClassesModel]:
        created_by_id = self._validate_object_id(created_by)
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list) or not data:
            raise ExceptionFactory.validation_failed(field="data", value=data, reason="Input must be a dict or a non-empty list")
        classes = self._to_classes_list(data)
        for class_model in classes:
            class_model.created_by = created_by_id
        classes_dicts = [
            convert_serializable(class_model.model_dump(by_alias=True, exclude_none=True, mode="json"))
            for class_model in classes
        ]
        if not classes_dicts:
            raise InternalServerError(message="Failed to convert classes to dict", severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE, status_code=500)

        try:
            result = self.collection.insert_many(classes_dicts)
            if not result.acknowledged:
                raise DatabaseError(message="Failed to create classes", details={"data": data}, severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE, status_code=500)
            return self._fetch_first_inserted(result.inserted_ids)
        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError("Unexpected error creating classes", cause=e, details={"data": data})
    
    def update_classes(self, _id: ObjectId | str, data: Dict[str, Any]) -> ClassesModel:
        validated_id = self._validate_object_id(_id)
        data_model = self._to_classes(data)
        if not data_model:
            raise ExceptionFactory.validation_failed(field="data", value=data, reason="Invalid class data")
        result = self.collection.update_one({"_id": validated_id}, {"$set": data_model.model_dump(by_alias=True, exclude_none=True, mode="json")})
        if result.matched_count == 0:
            raise NotFoundError(message=f"Class not found with ID {_id}", category=ErrorCategory.DATABASE, status_code=404)
        raw_doc = self.collection.find_one({"_id": validated_id})
        if not raw_doc:
            raise NotFoundError(message=f"Class not found with ID {_id}", category=ErrorCategory.DATABASE, status_code=404)
        return self._convert_to_response_model(raw_doc)

    
    
    def find_all_classes(self) -> List[ClassesModel]:
        try:
            result = self.collection.find({})
            if result:
                return self._convert_to_response_model_list(list(result))
            return []
        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while finding classes", cause=e, status_code=500)
    
    
    def find_classes_by_id(self, class_id: Union[ObjectId, str]) -> ClassesModel:
        validated_id = self._validate_object_id(class_id)
        try:
            raw_doc = self.collection.find_one({"_id": validated_id})
            if not raw_doc:
                raise NotFoundError(message=f"Class not found with ID {class_id}", category=ErrorCategory.DATABASE , status_code=404)
            return self._convert_to_response_model(raw_doc)
        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while finding classes", cause=e, details={"id": class_id}, status_code=500)



    def find_classes_by_teacher_id(self, created_by: ObjectId | str) -> List[ClassesModel]:
        validated_id = self._validate_object_id(created_by)   
        try:
            result = self.collection.find({"created_by": validated_id})
            return self._to_classes_list(list(result))
        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while finding classes", cause=e, details={"id": created_by})
    

    def _update_student_enrollment(self, _id: ObjectId | str, class_id: ObjectId | str, operation: str) -> Optional[ClassesModel]:
        validated_student_id = self._validate_object_id(_id)
        if not validated_student_id:
            raise ExceptionFactory.validation_failed(field="_id", value=_id, reason="Invalid student ID format") 
        
        validated_class_id = self._validate_object_id(class_id)
        if not validated_class_id:
            raise ExceptionFactory.validation_failed(field="class_id", value=class_id, reason="Invalid class ID format")
        
        mongo_op = {"$addToSet": {"students_enrolled": validated_student_id}} if operation == "enroll" else {"$pull": {"students_enrolled": validated_student_id}}
        
        result = self.collection.update_one({"_id": validated_class_id}, mongo_op)
        if result.matched_count == 0:
            raise NotFoundError("Class not found")
        result = self.collection.find_one({"_id": validated_class_id})
        return self._to_classes(result) if result else None



    def enroll_student_to_class(self, student_id: ObjectId | str, class_id: ObjectId | str) -> Optional[ClassesModel]:
        return self._update_student_enrollment(student_id, class_id, "enroll")

    def unenroll_student_from_class(self, student_id: ObjectId | str, class_id: ObjectId | str) -> Optional[ClassesModel]:
        return self._update_student_enrollment(student_id, class_id, "unenroll")



def get_classes_service(db: Database) -> MongoClassesService:
    return MongoClassesService(db)

