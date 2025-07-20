import logging
from typing import Optional, List, Dict, Any, Union
from pymongo.database import Database # type: ignore
from bson import ObjectId  # type: ignore
from app.models.teacher import TeacherModel  # type: ignore
from app.models.classes import ClassesModel  # type: ignore
from app.models.user import UserModel
from abc import ABC, abstractmethod
from app.error.exceptions import AppBaseException,ExceptionFactory, ValidationError, InternalServerError, NotFoundError, DatabaseError
logger = logging.getLogger(__name__)
from pymongo import ReturnDocument # type: ignore
from app.utils.model_utils import default_model_utils
from app.enums.roles import Role
from app.models.feedback import FeedbackModel
class TeacherService(ABC):
    pass
    # @abstractmethod
    # def create_teacher(self, data: Dict[str, Any]) -> Optional[UserModel]:
    #     pass

    # @abstractmethod
    # def get_teacher_by_id(self, _id: ObjectId) -> Optional[TeacherModel]:
    #     pass

    # @abstractmethod
    # def patch_teacher(self, _id: ObjectId, update_data: Dict[str, Any]) -> Optional[TeacherModel]:
    #     pass

    # @abstractmethod
    # def delete_teacher(self, _id: ObjectId | str) -> bool:
    #     pass

    @abstractmethod
    def teacher_create_classes(self, data: Dict[str, Any]) -> Optional[ClassesModel]:
        pass
class MongoTeacherService(TeacherService):
    def __init__(self, db: Database, collection_name: str = TeacherModel._collection_name):   
        self.db = db
        self.collection = self.db[collection_name]
        self.model_utils = default_model_utils
        self._classes_service = None
        self._user_service = None
        self._feedback_service = None

    @property
    def classes_service(self):
        if self._classes_service is None:
            from app.services.classes_service import get_classes_service
            self._classes_service = get_classes_service(self.db)
        return self._classes_service
    
    @property
    def user_service(self):
        if self._user_service is None:
            from app.services.user_service import get_user_service 
            self._user_service = get_user_service(self.db)
        return self._user_service
    
    @property
    def feedback_service(self):
        if self._feedback_service is None:
            from app.services.feedback_service import MongoFeedbackService
            self._feedback_service = MongoFeedbackService(self.db)
        return self._feedback_service


    def _to_teacher(self, data: Dict[str, Any]) -> Optional[TeacherModel]:
        return self.model_utils.to_model(data, TeacherModel)

    def _to_teachers(self, data_list: List[Dict[str, Any]]) -> List[TeacherModel]:
        return self.model_utils.to_model_list(data_list, TeacherModel)  

    def _is_non_empty_dict(self, data: Dict[str, Any]) -> bool:
        return isinstance(data, dict) and bool(data)

    def _to_classes(self, data: Dict[str, Any]) -> Optional[ClassesModel]:
        return self.classes_service._to_classes(data)
    
    def _to_classes_list(self, data_list: List[Dict[str, Any]]) -> List[ClassesModel]:
        return self.classes_service._to_classes_list(data_list)

    def _check_dict(self, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict) or not data:
            raise ValidationError(
                message="Data must be a non-empty dictionary",
                details=data,
                user_message="Invalid input data"
            )

    def _convert_to_response_model(self, data: Dict[str, Any]) -> Optional[TeacherModel]:
        return self.model_utils.convert_to_response_model(data, TeacherModel)
    
    def _to_objectid(self, id_val: Union[str, ObjectId]) -> Optional[ObjectId]:
        return self.model_utils.validate_object_id(id_val)
    
    def _prepare_safe_update(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.model_utils.prepare_safe_update(update_data)

    def create_teacher(self, data: dict) -> Optional[UserModel]:
        self._check_dict(data)
        data["role"] = Role.TEACHER.value
        user_model = self.user_service.create_user(data)
        return user_model

    def get_teacher_by_id(self, _id: Union[str, ObjectId]) -> TeacherModel:
        try:
            validated_id = self._to_objectid(_id)
            result = self.collection.find_one({"_id": validated_id})
            if not result:
                raise ExceptionFactory.not_found(resource_type="Teacher", resource_id=str(_id))
            return self._convert_to_response_model(result)           
        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError(
                message="Unexpected error occurred while fetching teacher",
                cause=e
        )


    def patch_teacher(self, _id: ObjectId, update_data: Dict[str, Any]) -> Optional[TeacherModel]:
        try:
            validated_id = self._to_objectid(_id)
            if not validated_id:
                raise ExceptionFactory.validation_failed(field="_id", value=_id, reason="Invalid teacher ID format")
            safe_update = self._prepare_safe_update(update_data)
            if "teacher_info" in safe_update and isinstance(safe_update["teacher_info"], dict):
                teacher_info_updates = safe_update.pop("teacher_info")
                for key, value in teacher_info_updates.items():
                    safe_update[f"teacher_info.{key}"] = value
            if not safe_update:
                raise ExceptionFactory.validation_failed(field="update_data", value=update_data, reason="No valid update data provided")

            result = self.collection.find_one_and_update(
                {"_id": validated_id},
                {"$set": safe_update},
                return_document=ReturnDocument.AFTER
            )

            return self._convert_to_response_model(result)

        except AppBaseException:
            raise 
        except Exception as e:
            raise InternalServerError(
                message="Unexpected error occurred while updating teacher",
                cause=e
            )


    def delete_teacher(self, _id: Union[ObjectId, str]) -> bool:
        validated_id = self._to_objectid(_id)
        try:
            result = self.collection.delete_one({"_id": validated_id})
            return result.deleted_count > 0 if result else False
        
        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError(
                message="Unexpected error occurred while deleting teacher",
                cause=e
            )

    def find_all_classes(self) -> List[ClassesModel]:
        logger.info('receive from find_all_classes')
        return self.classes_service.find_all_classes()
    
    
    def find_classes_by_teacher_id(self, _id: Union[ObjectId, str]) -> List[ClassesModel]:
        logger.info('receive from find_classes_by_teacher_id', _id)
        return self.classes_service.find_classes_by_teacher_id(_id)
    
    def find_classes_by_id(self, _id: Union[ObjectId, str]) -> ClassesModel:

        return self.classes_service.find_classes_by_id(_id)


    def teacher_create_classes(self, _id: Union[ObjectId, str], class_data: Dict[str, Any]) ->  Optional[ClassesModel]:
        return self.classes_service.create_classes(_id, class_data)

    def teacher_update_class(self, _id: Union[ObjectId, str], class_data: Dict[str, Any]) ->  ClassesModel:
        logger.info('receive from teacher_update_class', class_data)
        return self.classes_service.update_classes(_id, class_data)

    def teacher_create_feedback(self,feedback_data: Dict[str, Any]) -> Optional[FeedbackModel]:
        logger.info('receive from teacher_create_feedback', feedback_data)
        return self.feedback_service.create_feedback(feedback_data)

def get_teacher_service(db: Database) -> MongoTeacherService:
    return MongoTeacherService(db)





