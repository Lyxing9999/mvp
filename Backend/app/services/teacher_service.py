import logging
from typing import Optional, List, Dict, Any, Union
from app.services.user_service import UserService  # type: ignore
from pymongo.database import Database # type: ignore
from bson import ObjectId  # type: ignore
from bson.errors import InvalidId  # type: ignore
from app.models.teacher import TeacherModel, TeacherInfoModel  # type: ignore
from app.models.classes import ClassesModel  # type: ignore
from app.models.student import StudentModel  # type: ignore
from app.utils.dict_utils import flatten_dict # type: ignore
from datetime import datetime, timezone # type: ignore
from app.utils.exceptions import NotFoundError, ValidationError, DatabaseError, AuthenticationError, BadRequestError, InternalServerError, UnauthorizedError, ForbiddenError # type: ignore 
logger = logging.getLogger(__name__)
from pymongo import ReturnDocument # type: ignore

class TeacherService:
    def __init__(self, db: Database):
        self.db = db
        self.user_service = UserService()
        self.collection = self.db.teacher_info

    def _to_teacher(self, data: Optional[Dict[str, Any]]) -> Optional[TeacherModel]:
        if not isinstance(data, dict) or not data:
            return None
         
        try:
            return TeacherModel(**data)
        except Exception as e:
            logger.warning(f"Failed to convert data to TeacherModel: {e}")
            return None

    def _to_teachers(self, data_list: List[Dict[str, Any]]) -> List[TeacherModel]:
        return [teacher for data in data_list if (teacher := self._to_teacher(data))]
    def _to_classes(self, data: Optional[Dict[str, Any]]) -> Optional[ClassesModel]:
        if not isinstance(data, dict) or not data:
            return None
        return ClassesModel(**data)
    
    def _to_classes_list(self, data_list: List[Dict[str, Any]]) -> List[ClassesModel]:
        return [classes for data in data_list if (classes := self._to_classes(data))]
    def _to_objectid(self, id_val: Union[str, ObjectId]) -> Optional[ObjectId]:
        if isinstance(id_val, ObjectId):
            return id_val
        try:
            return ObjectId(id_val)
        except Exception as e:
            logger.error(f"Invalid ObjectId: {e}")
            return None

    def create_teacher(self, data: Dict[str, Any]) -> Optional[TeacherModel]:

        try:
            teacher = self._to_teacher(data)
            if not teacher:
                raise ValueError("Invalid teacher data provided")
    
            user_result = self.user_service.create_user(teacher.model_dump())
            
            if not user_result or not user_result.get("status"):
                logger.error(f"Failed to create user for teacher: {user_result}")
                return None
            created_user = user_result.get("user")
            return self._to_teacher(created_user) if created_user else None
            
        except Exception as e:
            logger.error(f"Error creating teacher: {str(e)}")
            raise

    def get_teacher_by_id(self, teacher_id: ObjectId) -> Optional[TeacherModel]:

        try:
            if not self._to_objectid(teacher_id):
                logger.warning(f"Invalid teacher ID format: {teacher_id}")
                return None
            
            result = self.collection.find_one({"_id": teacher_id})
            return self._to_teacher(result)
            
        except Exception as e:
            logger.error(f"Error fetching teacher {teacher_id}: {str(e)}")
            return None

    def get_all_teachers(self, page: int = 1, page_size: int = 10) -> List[TeacherModel]:
        try:
            skip = (page - 1) * page_size
            cursor = self.collection.find().skip(skip).limit(page_size)
            results = list(cursor)
            return self._to_teachers(results)
            
        except Exception as e:
            logger.error(f"Error fetching teachers: {str(e)}")
            return []

    def patch_teacher(self, teacher_id: ObjectId, update_data: Dict[str, Any]) -> Optional[TeacherModel]:

        try:
            if not self._to_objectid(teacher_id):
                logger.warning(f"Invalid teacher ID format: {teacher_id}")
                return None
            blacklist = {"_id", "role", "user_id", "userId", "created_at", "updated_at"}
            allowed_top_level_keys = set(TeacherModel.model_fields.keys())
            allowed_teacher_info_keys = set(TeacherInfoModel.model_fields.keys())
            safe_update: Dict[str, Any] = {}
            for key, value in update_data.items():
                if key in blacklist or value is None:
                    continue
                if key in allowed_top_level_keys and key != "teacher_info":
                    safe_update[key] = value
                elif key == "teacher_info" and isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if sub_key in allowed_teacher_info_keys and sub_value is not None:
                            safe_update[f"teacher_info.{sub_key}"] = sub_value

            if not safe_update:
                logger.warning("No valid update data provided")
                return None
    

            result = self.collection.find_one_and_update(
                {"_id": teacher_id},
                {"$set": safe_update},
                return_document=ReturnDocument.AFTER
            )

            return self._to_teacher(result)
            
        except Exception as e:
            logger.error(f"Error updating teacher {teacher_id}: {str(e)}")
            return None

    def update_teacher(self, teacher_id: ObjectId, update_data: Dict[str, Any]) -> Optional[TeacherModel]:

        try:
            if not self._to_objectid(teacher_id):
                logger.warning(f"Invalid teacher ID format: {teacher_id}")
                return None
            
            clean_data = flatten_dict(update_data)
            if not clean_data:
                logger.warning("No valid update data provided")
                return None
            
            result = self.collection.find_one_and_update(
                {"_id": teacher_id},
                {"$set": clean_data},
                return_document=ReturnDocument.AFTER
            )
            
            return self._to_teacher(result)
            
        except Exception as e:
            logger.error(f"Error updating teacher {teacher_id}: {str(e)}")
            return None

    def delete_teacher(self, user_id: ObjectId | str) -> bool:
        try:
            if not self._to_objectid(user_id):
                logger.warning(f"Invalid teacher ID format: {user_id}")
                return False
            
            result = self.collection.delete_one({"_id": user_id.id})
            return result.deleted_count > 0 if result else False
            
        except Exception as e:
            logger.error(f"Error deleting teacher {user_id}: {str(e)}")
            return False

    def search_teachers(self, query: str, page: int = 1, page_size: int = 10) -> List[TeacherModel]:

        try:
            if not query or not query.strip():
                return []
            
            skip = (page - 1) * page_size
            search_filter = {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"email": {"$regex": query, "$options": "i"}},
                    {"username": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = self.collection.find(search_filter).skip(skip).limit(page_size)
            results = list(cursor)
            return self._to_teachers(results)
            
        except Exception as e:
            logger.error(f"Error searching teachers with query '{query}': {str(e)}")
            return []

    def get_teacher_count(self) -> int:

        try:
            return self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Error counting teachers: {str(e)}")
            return 0

    def get_teachers_by_subject(self, subject: str) -> List[TeacherModel]:

        try:
            if not subject or not subject.strip():
                return []
            
            cursor = self.collection.find({"subjects": {"$in": [subject]}})
            results = list(cursor)
            return self._to_teachers(results)
            
        except Exception as e:
            logger.error(f"Error fetching teachers by subject '{subject}': {str(e)}")
            return []

    def get_classes_by_teacher_id(self, user_id: ObjectId | str) -> List[ClassesModel]:
        """
        Get all classes assigned to the teacher.

        Raises:
            NotFoundError: If teacher not found or has no classes
            ValidationError: If teacher_id is invalid
            DatabaseError: On database failure
        """
        try:
            user_id = self._to_objectid(user_id)
            if not user_id:
                raise ValidationError("Invalid teacher ID format")

            teacher = self.collection.find_one({"_id": user_id})
            if not teacher:
                raise NotFoundError("Teacher not found")

            class_ids = teacher.get("classes", [])
            if not class_ids:
                raise NotFoundError("No classes found for this teacher")

            class_cursor = self.db.classes.find({"_id": {"$in": class_ids}})
            class_docs = list(class_cursor)
            return self._to_classes_list(class_docs)

        except ValidationError as e:
            logger.warning(str(e))
            raise

        except NotFoundError as e:
            logger.info(str(e))
            raise

        except Exception as e:
            logger.error(f"Error fetching classes by teacher ID {user_id}: {str(e)}")
            raise DatabaseError("Failed to fetch teacher classes")
    

    
    def get_class_by_id(self, _id: List[ClassesModel]) -> Optional[ClassesModel]:
        """
        Get a class by its ID.
        :return: ClassesModel
        :raises: NotFoundError, ValidationError, DatabaseError
        """
        try:
            _id = self._to_objectid(_id)

            if not _id:
                raise ValidationError("Invalid class ID format")
            
            result = self.db.classes.find_one({"_id": _id})

            return self._to_classes(result) if result else None

        except ValidationError as e:
            logger.warning(str(e))
            raise
        except Exception as e:
            logger.error(f"Error fetching class by ID {_id}: {str(e)}")
            raise DatabaseError("Failed to fetch class")














def get_teacher_service(db: Database) -> TeacherService:
    return TeacherService(db)





