from app.models.user import UserModel
from app.enums.roles import Role
from app.utils.objectid import ObjectId # type: ignore
from typing import List, Optional, Dict, Any, Union
from werkzeug.security import generate_password_hash  # type: ignore
from app.models.student import StudentModel
import logging
from abc import ABC, abstractmethod
from app.utils.dict_utils import flatten_dict # type: ignore
from pydantic import ValidationError # type: ignore
from app.models.teacher import TeacherModel
from datetime import datetime, timedelta, timezone
from app.utils.console import console
from app.utils.exceptions import NotFoundError, ValidationError, DatabaseError, AuthenticationError, BadRequestError, InternalServerError, UnauthorizedError, ForbiddenError # type: ignore 
from pymongo.database import Database # type: ignore
from app.utils.date_utils import ensure_date
from app.repositories.user_repository import UserRepository, UserRepositoryImpl
from app.utils.model_utils import to_model, to_model_list, to_objectid, prepare_safe_update, validate_object_id # type: ignore
from app.database.db import get_db
from functools import lru_cache
logger = logging.getLogger(__name__)

class UserService(ABC):
    @property
    @abstractmethod
    def user_repo(self) -> UserRepositoryImpl:
        pass
    @abstractmethod
    def create_user(self, data: dict) -> Optional[UserModel]:
        pass
    
    @abstractmethod
    def patch_user(self, _id: Union[str, ObjectId], update_data: Dict[str, Any]) -> Optional[UserModel]:
        pass
    
    @abstractmethod
    def delete_user(self, _id: str) -> bool:
        pass
    @abstractmethod
    def patch_user_detail(self, _id: Union[str, ObjectId], user_update_data: dict) -> Optional[dict]:
        pass

class MongoUserService(UserService):
    def __init__(self, db: Database, user_repo: UserRepositoryImpl):
        self.db = db
        self.collection = self.db["users"]
        self._user_repo = user_repo
        self._role_collections = {
            Role.TEACHER.value: self.db["teacher"],
            Role.STUDENT.value: self.db["student"],
            Role.ADMIN.value: self.db["admin"]
        }
    def _get_role_collection(self, role: str):
        collection = self._role_collections.get(role)
        if collection is None:
            raise InternalServerError(f"Collection for role '{role}' not found")
        return collection     

    @property
    def user_repo(self) -> UserRepositoryImpl:
        return self._user_repo
    @staticmethod       
    def _to_user(data: dict) -> Optional[UserModel]:
        return to_model(data, UserModel)

    @staticmethod
    def _to_user_list(data_list: List[dict]) -> List[UserModel]:
        return to_model_list(data_list, UserModel)

    @staticmethod
    def _to_objectid(id_val: Union[str, ObjectId]) -> Optional[ObjectId]:
        return to_objectid(id_val)
        
    @staticmethod
    def _prepare_safe_update(user_update_data: dict) -> dict:
        return prepare_safe_update(user_update_data)

    @staticmethod
    def _validate_object_id(_id: Union[str, ObjectId]) -> ObjectId:
        return validate_object_id(_id)



    @staticmethod
    def ensure_date(value: Any) -> Any:
        return ensure_date(value)

    def _update_role_info(self, role: str, update_data: dict, original_data: dict) -> dict:
        now = datetime.now(timezone.utc)
        role_field = f"{role}"
        role_data = update_data.get(role_field, {})
        role_data["updated_at"] = now

        if role == Role.STUDENT.value:
            role_data["birth_date"] = ensure_date(role_data.get("birth_date"))

        if role == Role.TEACHER.value:
            update_data["phone_number"] = original_data.get("phone_number")

        update_data[role_field] = role_data
        return update_data

    def _create_role_specific_data(self, _id: ObjectId, role: Union[Role, str]) -> None:
        """Create minimal role-specific data for a new user based on their role."""
        if isinstance(role, str):
            role = Role(role)
        role_collection = self._get_role_collection(role)
        if role == Role.STUDENT:
            new_student = StudentModel.create_minimal(_id=_id)
            data = new_student.model_dump(by_alias=True)
        elif role == Role.TEACHER:
            new_teacher = TeacherModel.create_minimal(_id=_id)
            data = new_teacher.model_dump(by_alias=True)
        elif role == Role.ADMIN:
            data = {"_id": _id}
        
        data["_id"] = data.pop("id", None) or _id
        if isinstance(data["_id"], str):
            data["_id"] = ObjectId(data["_id"])
        logger.info(f"Creating {role} info for user_id: {_id}")
        role_collection.insert_one(data)

    def create_user(self, data: dict) -> Optional[UserModel]:
        data["created_at"] = datetime.utcnow()
        if "password" in data and data["password"]:
            data["password"] = generate_password_hash(data["password"])
        username = data.get("username")
        email = data.get("email")
        role = data.get("role", Role.STUDENT.value)

        if role not in [r.value for r in Role]:
            raise BadRequestError("Invalid role provided")

        try:
            if username and self.collection.find_one({"username": username}):
                raise BadRequestError("Username already exists")
            if email and self.collection.find_one({"email": email}):
                raise BadRequestError("Email already exists")
            result = self.collection.insert_one(data)
            if not result.acknowledged:
                raise InternalServerError("Failed to create user")
            _id = result.inserted_id
            self._create_role_specific_data(_id, role)
            data["id"] = str(_id)
            data.pop("password", None)  
            return self._to_user(data)
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise InternalServerError(f"Failed to create user: {e}")


    def patch_user(self, _id: Union[str, ObjectId], update_data: Dict[str, Any]) -> Optional[UserModel]:
        if isinstance(_id, str):
            _id = validate_object_id(_id)
            if not _id:
                logger.error(f"Invalid ObjectId string: {_id}")
                raise BadRequestError(f"Invalid ObjectId string: {_id}")
        update_data = self._prepare_safe_update(update_data)
        if "password" in update_data and update_data["password"]:
            update_data["password"] = generate_password_hash(update_data["password"])
        existing_user = self.collection.find_one({"_id": _id})
        if not existing_user:
            logger.error(f"User not found with _id: {_id}")
            raise NotFoundError(f"User not found with _id: {_id}")
        if "username" in update_data:
            conflict = self.collection.find_one({
                "username": update_data["username"],
                "_id": {"$ne": _id}  
            })
            if conflict:
                logger.error(f"Username {update_data['username']} already taken by another user")
                raise BadRequestError(f"Username {update_data['username']} already taken by another user")

        if "email" in update_data:
            if update_data["email"] is not None and update_data["email"] != "":
                conflict = self.collection.find_one({
                    "email": update_data["email"],
                    "_id": {"$ne": _id}
                })
                if conflict:
                    logger.error(f"Email {update_data['email']} already taken by another user")
                    raise BadRequestError(f"Email {update_data['email']} already taken by another user")

        try:
            UserModel.model_validate(existing_user)
        except Exception as e:
            logger.error(f"Pydantic validation failed on existing user: {e}")
            raise BadRequestError(f"Pydantic validation failed on existing user: {e}")

        try:
            updated_data = {**existing_user, **update_data}
            UserModel.model_validate(updated_data)
        except Exception as e:
            logger.error(f"Pydantic validation failed on updated data: {e}")
            raise BadRequestError(f"Pydantic validation failed on updated data: {e}")
        result = self.collection.update_one({"_id": _id}, {"$set": update_data})
        if result.matched_count > 0:
            updated_user = self.collection.find_one({"_id": _id})
            return self._to_user(updated_user)
        logger.error(f"Update failed for user with _id: {_id}")
        raise InternalServerError(f"Update failed for user with _id: {_id}")



    def delete_user(self, _id: str) -> bool:
        try:
            _id = self._validate_object_id(_id)
            user = self.collection.find_one({"_id": _id})
            if not user:
                logger.warning(f"Delete failed, user not found with _id: {_id}")
                raise NotFoundError(f"Delete failed, user not found with _id: {_id}")

            role = user.get("role")
            role_collection = self._get_role_collection(role)
            if role == Role.STUDENT.value:
                role_collection.delete_one({"_id": _id})
            elif role == Role.TEACHER.value:
                role_collection.delete_one({"_id": _id})
            elif role == Role.ADMIN.value:
                role_collection.delete_one({"_id": _id})

            result = self.collection.delete_one({"_id": _id})
            return result.deleted_count > 0

        except Exception as e:
            logger.error(f"Exception while deleting user: {e}")
            raise InternalServerError(f"Exception while deleting user: {e}")


  
    def patch_user_detail(self, _id: Union[str, ObjectId], user_update_data: dict) -> Optional[dict]:
        obj_id = self._to_objectid(_id)
        if not obj_id:
            logger.error(f"Invalid ObjectId: {_id}")
            raise BadRequestError(f"Invalid ObjectId: {_id}")
        try:
            full_user = self._user_repo.find_user_detail(obj_id)
            if not full_user:
                logger.error(f"User not found with _id: {obj_id}")
                raise NotFoundError(f"User not found with _id: {obj_id}")
            base_user = full_user["profile"]
            role = base_user.get("role")
            logger.info(f"User found with role: {role}")
            role_collection = self._get_role_collection(role)
            safe_update = dict(user_update_data)
            safe_update = prepare_safe_update(safe_update)

            if not safe_update:
                logger.warning("No valid fields to update.")
                return None

            safe_update = self._update_role_info(role, safe_update, base_user)

            flat_update = flatten_dict(safe_update)

            attendance_prefix = "student.attendance_record."
            keys_to_remove = [k for k in flat_update if k.startswith(attendance_prefix)]

            if keys_to_remove:
                for k in keys_to_remove:
                    flat_update.pop(k)

                full_attendance = (
                    user_update_data.get("student", {})
                    .get("attendance_record")
                )
                if full_attendance is not None:
                    flat_update["student.attendance_record"] = full_attendance

            update_result = role_collection.update_one(
                {"_id": obj_id},
                {"$set": flat_update}
            )
            if update_result.modified_count > 0:
                return {"status": True, "msg": "User info updated successfully"}
            else:
                return {"status": True, "msg": "No changes detected"}

        except Exception as e:
            logger.exception(f"Exception in edit_user_detail: {e}")
            raise InternalServerError(f"Exception in edit_user_detail: {e}")


@lru_cache(maxsize=1)   
def get_user_service() -> UserService:
    db = get_db()
    user_repo = UserRepositoryImpl(db)
    return  MongoUserService(db, user_repo)