from bson import ObjectId # type: ignore
from app.db import get_db
from typing import Optional 
from app.enums.roles import Role

db = get_db()

class User:
    def __init__(self, data: dict):
        if not isinstance(data, dict): data = {} 
        self.id: Optional[str] = str(data.get("_id")) if data.get("_id") else None
        self.role: str = data.get("role", Role.STUDENT.value)
        self.username: str = data.get("username", "")
        self.email: str = data.get("email", "")
        self.password:Optional[str] = data.get("password")

    def to_dict(self, include_password: bool = False) -> dict:
        user_dict  = {
            "role": self.role,
            "id": self.id,
            "username": self.username,
            "email": self.email
        }
        if include_password and self.password:
            user_dict["password"] = self.password
        return user_dict