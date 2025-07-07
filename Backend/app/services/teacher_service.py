import logging
from typing import Optional, List, Dict, Any, Union
from app.services.user_service import MongoUserService  # type: ignore
from pymongo.database import Database # type: ignore
from bson import ObjectId  # type: ignore
from bson.errors import InvalidId  # type: ignore
from app.models.teacher import TeacherModel, TeacherInfoModel  # type: ignore
from app.models.classes import ClassesModel  # type: ignore
from app.models.user import UserModel
from app.models.student import StudentModel  # type: ignore
from app.utils.dict_utils import flatten_dict # type: ignore
from abc import ABC, abstractmethod
from datetime import datetime, timezone # type: ignore
from app.utils.exceptions import NotFoundError, ValidationError, DatabaseError, AuthenticationError, BadRequestError, InternalServerError, UnauthorizedError, ForbiddenError # type: ignore 
logger = logging.getLogger(__name__)
from pymongo import ReturnDocument # type: ignore
from app.services.user_service import MongoUserService
from app.repositories.user_repository import UserRepositoryImpl
from app.enums.roles import Role
class TeacherService(ABC):
    @abstractmethod
    def create_teacher(self, data: Dict[str, Any]) -> Optional[UserModel]:
        pass

    @abstractmethod
    def get_teacher_by_id(self, _id: ObjectId) -> Optional[TeacherModel]:
        pass

    @abstractmethod
    def patch_teacher(self, _id: ObjectId, update_data: Dict[str, Any]) -> Optional[TeacherModel]:
        pass

    @abstractmethod
    def delete_teacher(self, _id: ObjectId | str) -> bool:
        pass

class MongoTeacherService(TeacherService):
    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db.teacher_info
        self.user_service = MongoUserService(db, UserRepositoryImpl(db))
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
    
    def _to_teacher_model(self, user_dict: dict) -> UserModel:
        return UserModel(**user_dict)

    def create_teacher(self, data: dict) -> UserModel:
        if not isinstance(data, dict) or not data:
            raise ValidationError("Data must be a dictionary")

        data["role"] = Role.TEACHER.value
        user_model = self.user_service.create_user(data)  # returns UserModel instance

        if not user_model:
            raise InternalServerError("Failed to create teacher user")

        return user_model


    def get_teacher_by_id(self, _id: ObjectId) -> Optional[TeacherModel]:

        try:
            teacher_id = self._to_objectid(_id)
            if not teacher_id:
                logger.warning(f"Invalid teacher ID format: {_id}")
                return None
            
            result = self.collection.find_one({"_id": teacher_id})
            return self._to_teacher(result)
            
        except Exception as e:
            logger.error(f"Error fetching teacher {_id}: {str(e)}")
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




    def patch_teacher(self, _id: ObjectId, update_data: Dict[str, Any]) -> Optional[TeacherModel]:
        """
        Patch a teacher's information.
        :param teacher_id: The ID of the teacher to patch
        :param update_data: The data to update
        :return: The updated teacher
        :raises: NotFoundError, ValidationError, DatabaseError
        """
        try:
            teacher_id = self._to_objectid(_id)
            if not teacher_id:
                logger.warning(f"Invalid teacher ID format: {_id}")
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
    
            print(safe_update)
            find_teacher = self.collection.find_one({"_id": teacher_id})
            print(find_teacher)
            result = self.collection.find_one_and_update(
                {"_id": teacher_id},
                {"$set": safe_update},
                return_document=ReturnDocument.AFTER
            )

            return self._to_teacher(result)
            
        except Exception as e:
            logger.error(f"Error updating teacher {teacher_id}: {str(e)}")
            return None

    def delete_teacher(self, _id: ObjectId | str) -> bool:
        """
        Delete a teacher.
        :param _id: The ID of the teacher to delete
        :return: True if the teacher was deleted, False otherwise
        :raises: NotFoundError, ValidationError, DatabaseError
        """
        try:
            if not self._to_objectid(_id):
                logger.warning(f"Invalid teacher ID format: {_id}")
                return False
            
            result = self.collection.delete_one({"_id": _id})
            return result.deleted_count > 0 if result else False
            
        except Exception as e:
            logger.error(f"Error deleting teacher {_id}: {str(e)}")
            return False

    def search_teachers(self, query: str, page: int = 1, page_size: int = 10) -> List[TeacherModel]:
        """
        Search for teachers by name, email, or username.
        :param query: The query to search for
        :param page: The page number
        :param page_size: The number of teachers per page
        :return: A list of teachers
        :raises: NotFoundError, ValidationError, DatabaseError
        """
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
        """
        Get the number of teachers.
        :return: The number of teachers
        :raises: DatabaseError
        """
        try:
            return self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Error counting teachers: {str(e)}")
            return 0

    def get_teachers_by_subject(self, subject: str) -> List[TeacherModel]:
        """
        Get teachers by subject.
        :param subject: The subject to search for
        :return: A list of teachers
        :raises: NotFoundError, ValidationError, DatabaseError
        """
        try:
            if not subject or not subject.strip():
                return []
            
            cursor = self.collection.find({"subjects": {"$in": [subject]}})
            results = list(cursor)
            return self._to_teachers(results)
            
        except Exception as e:
            logger.error(f"Error fetching teachers by subject '{subject}': {str(e)}")
            return []

    def get_classes_by_teacher_id(self, _id: ObjectId | str) -> List[ClassesModel]:
        """
        Get all classes assigned to the teacher.

        Raises:
            NotFoundError: If teacher not found or has no classes
            ValidationError: If teacher_id is invalid
            DatabaseError: On database failure
        """
        try:
            teacher_id = self._to_objectid(_id)
            if not teacher_id:
                raise ValidationError("Invalid teacher ID format")

            teacher = self.collection.find_one({"_id": teacher_id})
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
            logger.error(f"Error fetching classes by teacher ID {teacher_id}: {str(e)}")
            raise DatabaseError("Failed to fetch teacher classes")
    

    
    def get_class_by_id(self, _id: List[ClassesModel]) -> Optional[ClassesModel]:
        """
        Get a class by its ID.
        :return: ClassesModel
        :raises: NotFoundError, ValidationError, DatabaseError
        """
        try:
            class_id = self._to_objectid(_id)

            if not class_id:
                raise ValidationError("Invalid class ID format")
            
            result = self.db.classes.find_one({"_id": class_id})

            return self._to_classes(result) if result else None

        except ValidationError as e:
            logger.warning(str(e))
            raise
        except Exception as e:
            logger.error(f"Error fetching class by ID {class_id}: {str(e)}")
            raise DatabaseError("Failed to fetch class")



    def teacher_enroll_class(self, _id: ObjectId | str, class_id: ObjectId | str) -> Optional[ClassesModel]:
        """
        Enroll a teacher in a class.
        :param _id: The ID of the teacher
        :param class_id: The ID of the class
        :return: The class
        """
        try:
            teacher_id = self._to_objectid(_id)
            if not teacher_id:
                raise ValidationError("Invalid teacher ID format")
            
            class_id = self._to_objectid(class_id)
            if not class_id:
                raise ValidationError("Invalid class ID format")
            
            result = self.db.classes.update_one(
                {"_id": class_id},
                {"$push": {"teachers": teacher_id}}
            )
            return self._to_classes(result)
        except Exception as e:
            logger.error(f"Error enrolling teacher {teacher_id} in class {class_id}: {str(e)}")
            raise DatabaseError("Failed to enroll teacher in class")
    
    def teacher_create_class(self, _id: ObjectId | str, class_data: Dict[str, Any]) -> Optional[ClassesModel]:
        """
        Create a new class.
        :param _id: The ID of the teacher
        :param class_data: The data to create the class with
        :return: The class
        """
        try:
            teacher_id = self._to_objectid(_id)
            if not teacher_id:
                raise ValidationError("Invalid teacher ID format")
            
            class_data["teachers"] = [teacher_id]
            result = self.db.classes.insert_one(class_data) 
            return self._to_classes(result)
        except Exception as e:
            logger.error(f"Error creating class: {str(e)}")
            raise DatabaseError("Failed to create class")
    
    def teacher_update_class(self, _id: ObjectId | str, class_id: ObjectId | str, update_data: Dict[str, Any]) -> Optional[ClassesModel]:
        """
        Update a class.
        :param _id: The ID of the teacher
        :param class_id: The ID of the class
        :param update_data: The data to update the class with
        :return: The class
        """
        try:
            teacher_id = self._to_objectid(_id)
            if not teacher_id:
                raise ValidationError("Invalid teacher ID format")
            
            class_id = self._to_objectid(class_id)
            if not class_id:
                raise ValidationError("Invalid class ID format")
            
            result = self.db.classes.update_one(
                {"_id": class_id},
                {"$set": update_data}
            )
            return self._to_classes(result)
        except Exception as e:
            logger.error(f"Error updating class {class_id}: {str(e)}")
            raise DatabaseError("Failed to update class")













def get_teacher_service(db: Database) -> MongoTeacherService:
    return MongoTeacherService(db)





