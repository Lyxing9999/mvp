from bson import ObjectId # type: ignore
from app.db import get_db
from typing import Optional , List
from app.enums.roles import Role
db = get_db()

class User:
    def __init__(self, data: dict):
        if not isinstance(data, dict): data = {} 
        self.id: Optional[str] = str(data.get("_id")) if data.get("_id") else None
        self.role: str = data.get("role", Role.STUDENT.value)
        self.username: str = data.get("username", "")
        self.email: str = data.get("email", "")




    def to_dict(self, ) -> dict:
        return {
            "role": self.role,
            "id": self.id,
            "username": self.username,
            "email": self.email
        }
    
    @classmethod
    def create_user(cls, user_data: dict) -> "User":
        role = user_data.get("role", Role.STUDENT.value)
        role_data = {}
        if role == Role.STUDENT.value and "student_info" in user_data:
            role_data = user_data.pop("student_info")
        elif role == Role.TEACHER.value and "teacher_info" in user_data:
            role_data = user_data.pop("teacher_info")
        result = db.users.insert_one(user_data)
        user_id = result.inserted_id
        if role == Role.STUDENT.value:
            role_data["user_id"] = user_id
            db.student_info.insert_one(role_data)
        elif role == Role.TEACHER.value:
            role_data["user_id"] = user_id
            db.teacher_info.insert_one(role_data)
        user_data["_id"] = user_id
        return cls(user_data)
        
    
    
    
    @classmethod
    def edit_user(cls, _id: ObjectId, update_data: dict) -> Optional["User"]:
        update_data = {k: v for k, v in update_data.items() if k != '_id'}
        result = db.users.update_one({"_id": _id}, {"$set": update_data})
        if result.modified_count > 0:
            update_user = db.users.find_one({"_id": _id})
            return cls(update_user)
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

        result = db.users.delete_one({"_id": _id})
        return result.deleted_count > 0
    
    @classmethod
    def find_user_by_id(cls, id: str) -> List["User"]:    

        try:
            user_cursor = db.users.find({"_id": ObjectId(id)})
            return [cls(user) for user in user_cursor]
        except Exception as e:
            print(f"Error fetching user data: {e}")
            return []
        
    @classmethod
    def find_all_user(cls) -> list["User"]:
        try:
            users_cursor = db.users.find()
            return [cls(user) for user in users_cursor]
        except Exception as e:
            print(f"Error fetching all users: {e}")
            return []
        
    @classmethod
    def find_user_by_role(cls, role: str) -> Optional["User"]:
        users_cursor = db.users.find({"role": role})
        return [cls(user_data) for user_data in users_cursor]
        
    @classmethod
    def find_by_email(cls, email: str) -> Optional["User"]:
        user_data = db.users.find_one({"email": email})
        return cls(user_data) if user_data else None



