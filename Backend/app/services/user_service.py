from app.models.user_model import User
from app.db import get_db
from app.enums.roles import Role
from bson import ObjectId # type: ignore
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from app.utils.convert import convert_objectid_to_str
from werkzeug.security import generate_password_hash  # type: ignore


import logging

logger = logging.getLogger(__name__)
db = get_db()
class UserService:
    @staticmethod
    def _to_user(data: Optional[dict]) -> Optional[User]:
        if not isinstance(data, dict):
            return None
        return User(data)
    @staticmethod
    def _to_users(data_list: List[dict]) -> List[User]:
        return [User(data) for data in data_list if isinstance(data, dict)]

    @classmethod
    def create_user(cls, user_data: dict) -> "User":
        
        role = user_data.get("role", Role.STUDENT.value)
        role_data = {}
        if "password" in user_data and user_data["password"]:
            user_data["password"] = generate_password_hash(user_data["password"])
            
        if role == Role.STUDENT.value and "student_info" in user_data:
            role_data = user_data.pop("student_info")
        elif role == Role.TEACHER.value and "teacher_info" in user_data:
            role_data = user_data.pop("teacher_info")
        elif role == Role.ADMIN.value and "admin_info" in user_data:
            role_data = user_data.pop("admin_info")
        user_data["created_at"] = datetime.now(timezone.utc)
        result = db.users.insert_one(user_data)
        user_id = result.inserted_id
        
        if role == Role.STUDENT.value:
            role_data["user_id"] = user_id
            db.student_info.insert_one(role_data)
        elif role == Role.TEACHER.value:
            role_data["user_id"] = user_id
            db.teacher_info.insert_one(role_data)
        elif role == Role.ADMIN.value:
            role_data["user_id"] = user_id
            db.admin.insert_one(role_data)
        user_data["_id"] = user_id
        return User(user_data)
        
    
    @classmethod
    def edit_user(cls, _id: ObjectId, update_data: Dict[str, Any]) -> Optional["User"]:
        if isinstance(_id, str):
            try:
                _id = ObjectId(_id)
            except Exception as e:
                logger.error(f"Invalid _id format: {e}")
                return None

        update_data = {k: v for k, v in update_data.items() if k != '_id'}
        result = db.users.update_one({"_id": _id}, {"$set": update_data})
        if result.modified_count > 0:
            update_user = db.users.find_one({"_id": _id})
            return cls._to_user(update_user)
        return None
    

    @classmethod
    def delete_user(cls, _id: ObjectId) -> bool:
        
        user = db.users.find_one({"_id": _id})
        if not user:
            return False
        role = user.get("role")
        
        if role == Role.STUDENT.value:
            db.student_info.delete_one({"user_id": _id})
        elif role == Role.TEACHER.value:
            db.teacher_info.delete_one({"user_id": _id})
        elif role == Role.ADMIN.value:
            db.admin.delete_one({"user_id": _id}) 
            
        result = db.users.delete_one({"_id": _id})
        return result.deleted_count > 0

    
    
    @classmethod
    def find_teacher_info(cls) -> List[dict]:
        try:
            teacher_cursor = db.teacher_info.find()
            return list(teacher_cursor)
        except Exception as e:
            logger.error(f"Error fetching users by teacher: {e}")
            return []
        
        
    @classmethod
    def find_student_info(cls) -> List[dict]:
        try:
            student_cursor = db.student_info.find()
            return list(student_cursor)
        except Exception as e:
            logger.error(f"Error fetching users by student: {e}")
            return []


    @classmethod
    def find_user_by_id(cls, id: str) -> Optional["User"]:    
        try:
            user_data = db.users.find_one({"_id": ObjectId(id)})
            if not user_data:
                logger.warning(f"User not found with ID: {id}")
            return cls._to_user(user_data)
        except Exception as e:
            logger.error(f"Error fetching users by user ID: {e}")
            return None


    @classmethod
    def find_student_info_by_id(cls, user_id: str) -> Optional[Dict]:
        try:
            obj_user_id = ObjectId(user_id)
            student_info = db.student_info.find_one({"user_id": obj_user_id})
            return student_info
        except Exception as e:
            logger.error(f"Error fetching users by student ID: {e}")
            return None
        
        
                  
    @classmethod
    def find_user_by_role(cls, role: str) -> List["User"]:
        users_cursor = db.users.find({"role": role})
        raw_users = list(users_cursor)
        return cls._to_users(raw_users)
        
    @classmethod
    def find_user_by_email(cls, email: str) -> Optional["User"]:
        user_data = db.users.find_one({"email": email})
        if user_data:
            return cls._to_user(user_data)
        return None
    
    
    @classmethod
    def find_user_by_username(cls, username: str) -> Optional["User"]:
            user_data = db.users.find_one({"username": username})
            if user_data:
                return cls._to_user(user_data)
            return None
        

