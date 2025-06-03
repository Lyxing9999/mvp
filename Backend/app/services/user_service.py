from app.models.user import UserModel
from app.db import get_db
from app.enums.roles import Role
from app.utils.objectid import ObjectId
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash  # type: ignore
import logging
from pydantic import ValidationError # type: ignore
logger = logging.getLogger(__name__)
db = get_db()

class UserService:

    @staticmethod
    def _to_user(data: dict) -> Optional[UserModel]:
        if not data:
            return None
        try:
            return UserModel.model_validate(data)
        except Exception as e:
            logger.error(f"Error parsing user data: {e}")
            return None
        
        
        
    @staticmethod
    def _to_objectid(id_str: str) -> Optional[ObjectId]:
        
        try:
            return ObjectId(id_str)
        except Exception as e:
            logger.error(f"Invalid ObjectId: {e}")
            return None

    @classmethod
    def create_user(cls, user_data: dict) -> dict:
        try:
            user = UserModel.model_validate(user_data)
        except ValidationError as e:
            return {"status": False, "msg": f"Validation error: {str(e)}"}

        user_dict = user.model_dump(by_alias=True, exclude={"id"})
        if "password" in user_dict and user_dict["password"]:
            user_dict["password"] = generate_password_hash(user_dict["password"])

        # user_dict["created_at"] = datetime.now(timezone.utc)

        role = user_dict.get("role", Role.STUDENT.value)
        role_data = {}
        username = user_dict.get("username")
        email = user_dict.get("email")
        try:
            if not username and not email:
                return {"status": False, "msg": "Username or email is required"}

            if username and db.users.find_one({"username": username}):
                return {"status": False, "msg": "Username already exists"}

            if email and db.users.find_one({"email": email}):
                return {"status": False, "msg": "Email already exists"}
            result = db.users.insert_one(user_dict)

            user_id = result.inserted_id
            user.id = str(user_id)
            role_data["user_id"] = user_id
            if role == Role.STUDENT.value:
                db.student_info.insert_one(role_data)
            elif role == Role.TEACHER.value:
                db.teacher_info.insert_one(role_data)
            elif role == Role.ADMIN.value:
                db.admin_info.insert_one(role_data)
            return {"status": True, "user": user}
        
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return {"status": False, "msg": "Internal server error"}


    @classmethod
    def edit_user(cls, _id: ObjectId | str, update_data: Dict[str, Any]) -> Optional[UserModel]:
        if isinstance(_id, str):
            _id = cls._to_objectid(_id)
            if not _id:
                logger.error(f"Invalid ObjectId string: {_id}")
                return None

        update_data.pop('_id', None)

        if "password" in update_data and update_data["password"]:
            update_data["password"] = generate_password_hash(update_data["password"])

        existing_user = db.users.find_one({"_id": _id})
        if not existing_user:
            logger.error(f"User not found with _id: {_id}")
            return None

   
        if "username" in update_data:
            conflict = db.users.find_one({
                "username": update_data["username"],
                "_id": {"$ne": _id}  
            })
            if conflict:
                logger.error(f"Username {update_data['username']} already taken by another user")
                return None


        if "email" in update_data:
            conflict = db.users.find_one({
                "email": update_data["email"],
                "_id": {"$ne": _id}  
            })
            if conflict:
                logger.error(f"Email {update_data['email']} already taken by another user")
                return None

        try:
            UserModel.model_validate(existing_user)
        except Exception as e:
            logger.error(f"Pydantic validation failed on existing user: {e}")
            return None

        try:
            updated_data = {**existing_user, **update_data}
            UserModel.model_validate(updated_data)
        except Exception as e:
            logger.error(f"Pydantic validation failed on updated data: {e}")
            return None

        result = db.users.update_one({"_id": _id}, {"$set": update_data})

        if result.matched_count > 0:
            updated_user = db.users.find_one({"_id": _id})
            return cls._to_user(updated_user)

        logger.error(f"Update failed for user with _id: {_id}")
        return None



    @classmethod
    def delete_user(cls, _id: str) -> bool:
        try:
            _id = ObjectId(_id)
            user = db.users.find_one({"_id": _id})
            if not user:
                logger.warning(f"Delete failed, user not found with _id: {_id}")
                return False

            role = user.get("role")
            if role == Role.STUDENT.value:
                db.student_info.delete_one({"user_id": _id})
            elif role == Role.TEACHER.value:
                db.teacher_info.delete_one({"user_id": _id})
            elif role == Role.ADMIN.value:
                db.admin_info.delete_one({"user_id": _id})

            result = db.users.delete_one({"_id": _id})
            return result.deleted_count > 0

        except Exception as e:
            logger.error(f"Exception while deleting user: {e}")
            return False




    @classmethod
    def find_user_by_id(cls, id_str: str) -> Optional[UserModel]: 
        obj_id = cls._to_objectid(id_str)

        if not obj_id:
            return None
        try:
            user_data = db.users.find_one({"_id": obj_id})
            if not user_data:
                logger.warning(f"User not found with ID: {id_str}")
                return None  

            return cls._to_user(user_data)
        except Exception as e:
            logger.error(f"Error fetching user by ID: {e}")
            return None


    @classmethod
    def find_user_by_role(cls, role: str) -> List[UserModel]:
        try:
            users_cursor = db.users.find({"role": role})
            raw_users = list(users_cursor)
            return cls._to_users(raw_users)
        except Exception as e:
            logger.error(f"Failed to find users by role {role}: {e}")
        return []
    @classmethod
    def find_user_by_email(cls, email: str) -> Optional[UserModel]:
        try:
            user_data = db.users.find_one({"email": email})
            if user_data:
                return cls._to_user(user_data)
            return None
        except Exception as e:
            logger.error(f"Failed to find user by email {email}: {e}")
        return None
    
    
    @classmethod
    def find_user_by_username(cls, username: str) -> Optional[Dict]:
        try:
            user_data = db.users.find_one({"username": username})
            if user_data:
                print(user_data)
                return cls._to_user(user_data) 
            else:
                logger.warning(f"User not found with username: {username}")
            return None
        except Exception as e:
            logger.error(f"Failed to find user by username {username}: {e}")
            return None
        
        
    @classmethod
    def find_all_users(cls):
        try:
            users_cursor = db.users.find()
            users_list = list(users_cursor)
            return cls._to_users(users_list)
        except Exception as e:
            logger.error(f"Failed to fetch all users: {e}")
            return []