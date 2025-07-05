from app.models.user import UserModel, Role
from app.models.student import StudentModel
from app.models.teacher import TeacherModel
from app.db import get_db
from app.utils.objectid import ObjectId # type: ignore
from typing import Optional, List, Dict, Any, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pydantic import ValidationError # type: ignore
from datetime import datetime, timedelta
from loguru import logger # type: ignore
import pymongo # type: ignore
from bson.errors import InvalidId # type: ignore

class UserRepository:
    def __init__(self):
        self.db = get_db()

    def _to_user(self, data: dict) -> Optional[UserModel]:
        if not data:
            return None
        try:
            return UserModel.model_validate(data)
        except Exception as e:
            logger.error(f"Error parsing user data: {e}")
            return None
    def _to_users(self, data_list: List[dict]) -> List[UserModel]:
        return [UserModel(**data) for data in data_list]

    def _to_objectid(self, id_val: Union[str, ObjectId]) -> Optional[ObjectId]:
        if isinstance(id_val, str):
            try:
                return ObjectId(id_val)
            except InvalidId:
                return None
        return id_val

    def find_all_users(self) -> List[UserModel]:
        try:
            users_cursor = self.db.users.find()
            users_list = list(users_cursor)
            return self._to_users(users_list)
        except Exception as e:
            logger.error(f"Failed to fetch all users: {e}")
            return []
        
        
    def find_users_growth_stats_by_role(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(milliseconds=1)

        try:
            pipeline = [
                {
                    "$match": {
                        "created_at": {
                            "$gte": start_dt,
                            "$lte": end_dt
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$role",
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$sort": {"count": -1}
                }
            ]

            result = list(self.db.users.aggregate(pipeline))
            if not result:
                return []

            total = sum(role["count"] for role in result)
            for role in result:
                role["role"] = role.pop("_id")
                role["percentage"] = round((role["count"] / total * 100) if total > 0 else 0, 2)

            return result

        except Exception as e:
            logger.error(f"Failed to fetch user growth stats by role: {e}")
            return []
    def search_user(self, query: str, page: int, page_size: int) -> List[UserModel]:
        try:
            regex = {"$regex": query, "$options": "i"}
            skip = (page - 1) * page_size
            pipeline = [
                {"$match": {"$or": [{"username": regex}, {"email": regex}]}},
                {"$skip": skip},
                {"$limit": page_size},
                {"$lookup": {"from": "admin_info", "localField": "_id", "foreignField": "user_id", "as": "admin_info"}},
                {"$unwind": {"path": "$admin_info", "preserveNullAndEmptyArrays": True}},
                {"$lookup": {"from": "teacher_info", "localField": "_id", "foreignField": "user_id", "as": "teacher_info"}},
                {"$unwind": {"path": "$teacher_info", "preserveNullAndEmptyArrays": True}},
                {"$lookup": {"from": "student_info", "localField": "_id", "foreignField": "user_id", "as": "student_info"}},
                {"$unwind": {"path": "$student_info", "preserveNullAndEmptyArrays": True}}
            ]
            users_cursor = self.db.users.aggregate(pipeline)
            users_list = list(users_cursor)
            return self._to_users(users_list)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return []
        except TypeError as e:
            logger.error(f"Type error: {e}")
            return []
        except pymongo.errors.PyMongoError as e:
            logger.error(f"MongoDB error: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to search users: {e}")
            return []

    def find_users_detail(self, user_id: Union[str, ObjectId]) -> Optional[dict]:
        obj_id = self._to_objectid(user_id)
        if not obj_id:
            logger.error(f"Invalid ObjectId: {user_id}")
            return None

        pipeline = [
            {"$match": {"_id": ObjectId(obj_id)}},

            {"$lookup": {
                "from": "admin_info",
                "localField": "_id",
                "foreignField": "user_id",
                "as": "admin_info"
            }},
            {"$unwind": {"path": "$admin_info", "preserveNullAndEmptyArrays": True}},

            {"$lookup": {
                "from": "teacher_info",
                "localField": "_id",
                "foreignField": "user_id",
                "as": "teacher_info"
            }},
            {"$unwind": {"path": "$teacher_info", "preserveNullAndEmptyArrays": True}},

            {"$lookup": {
                "from": "student_info",
                "localField": "_id",
                "foreignField": "user_id",
                "as": "student_info"
            }},
            {"$unwind": {"path": "$student_info", "preserveNullAndEmptyArrays": True}},
        ]


        
        try:
            data = list(self.db.users.aggregate(pipeline))
        except Exception as e:
            print(f"Aggregation failed: {str(e)}")
            return None

        user_doc = data[0]

        user = UserModel(**user_doc)
        result = {
            "profile": user.dict(exclude={"password"})
        }

        if user.role == "teacher" and user_doc.get("teacher_info"):
            result["teacher_info"] = TeacherModel(**user_doc["teacher_info"]).dict()
        elif user.role == "student" and user_doc.get("student_info"):
            result["student_info"] = StudentModel(**user_doc["student_info"]).dict()
        elif user.role == "admin" and user_doc.get("admin_info"):
            result["admin_info"] = UserModel(**user_doc["admin_info"]).dict()

        return result



    def find_user_growth_stats(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(milliseconds=1)
        try:
            pipeline = [
                {
                    "$match": {
                        "created_at": {
                            "$gte": start_dt,
                            "$lte": end_dt
                        }
                    }
                },
                {
                    "$facet": {
                        "dailyCounts": [
                            {
                                "$group": {
                                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                                    "count": {"$sum": 1}
                                }
                            },
                            {
                                "$sort": {"_id": 1}
                            }
                        ],
                        "totalCount": [
                            {
                                "$count": "total"
                            }
                        ]
                    }
                }
            ]

            result = list(self.db.users.aggregate(pipeline))
            if not result:
                return []

            daily_counts = result[0]["dailyCounts"]
            total_count = result[0]["totalCount"][0]["total"] if result[0]["totalCount"] else 0
            print(f"Total user count in date range: {total_count}, Daily counts: {daily_counts}")
            stats = []
            for entry in daily_counts:
                percent = (entry["count"] / total_count * 100) if total_count > 0 else 0
                stats.append({
                    "date": entry["_id"],
                    "count": entry["count"],
                    "percentage": round(percent, 2)  # round to 2 decimals
                })

            return stats

        except Exception as e:
            logger.error(f"Failed to fetch user growth stats: {e}")
            return []
            

    def find_users_growth_stats_by_role_with_comparison(self, current_start_date: str, current_end_date: str, previous_start_date: str,previous_end_date: str) -> List[Dict[str, Any]]:
        def parse_date_range(start, end):
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1) - timedelta(milliseconds=1)
            return start_dt, end_dt

        def get_role_counts(start_dt, end_dt):
            pipeline = [
                {
                    "$match": {
                        "created_at": {
                            "$gte": start_dt,
                            "$lte": end_dt
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$role",
                        "count": {"$sum": 1}
                    }
                }
            ]
            results = list(self.db.users.aggregate(pipeline))
            return {entry["_id"]: entry["count"] for entry in results}

        try:
            current_start, current_end = parse_date_range(current_start_date, current_end_date)
            prev_start, prev_end = parse_date_range(previous_start_date, previous_end_date)

            current_counts = get_role_counts(current_start, current_end)
            prev_counts = get_role_counts(prev_start, prev_end)

            all_roles = set(current_counts.keys()) | set(prev_counts.keys())
            growth_stats = []

            for role in all_roles:
                current = current_counts.get(role, 0)
                prev = prev_counts.get(role, 0)

                if prev == 0:
                    growth = 100.0 * current if current > 0 else 0.0
                else:
                    growth = ((current - prev) / prev) * 100

                growth_stats.append({
                    "role": role,
                    "previous": prev,
                    "current": current,
                    "growth_percentage": round(growth, 2)
                })

            return growth_stats
        except Exception as e:
            logger.error(f"Failed to fetch user growth comparison stats: {e}")
            return []
        
        
    def count_users_by_role(self) -> dict:
        try:
            pipeline = [
                {"$group": {"_id": "$role", "count": {"$sum": 1}}}
            ]
            result = self.db.users.aggregate(pipeline)
            
            counts = {role.value: 0 for role in Role}
            
            for r in result:
                if r["_id"] in counts:
                    counts[r["_id"]] = r["count"]      
            return counts
        except Exception as e:
            logger.error(f"Failed to count users by roles: {e}")
            return {}
    
    def find_teacher_by_id(self, teacher_id: Union[str, ObjectId]) -> Optional[UserModel]:
        obj_id = self._to_objectid(teacher_id)
        if not obj_id:
            logger.error(f"Invalid ObjectId: {teacher_id}")
            return None
        return self.db.users.find_one({"_id": obj_id, "role": Role.TEACHER.value})
        

    def find_student_by_id(self, student_id: Union[str, ObjectId]) -> Optional[UserModel]:
        obj_id = self._to_objectid(student_id)
        if not obj_id:
            logger.error(f"Invalid ObjectId: {student_id}")
            return None
        return self.db.users.find_one({"_id": obj_id, "role": Role.STUDENT.value})

    def find_admin_by_id(self, admin_id: Union[str, ObjectId]) -> Optional[UserModel]:
        obj_id = self._to_objectid(admin_id)
        if not obj_id:
            logger.error(f"Invalid ObjectId: {admin_id}")
            return None
        return self.db.users.find_one({"_id": obj_id, "role": Role.ADMIN.value})

    def find_user_by_id(self, id_str: str) -> Optional[UserModel]: 
        obj_id = self._to_objectid(id_str)

        if not obj_id:
            return None
        try:
            user_data = self.db.users.find_one({"_id": obj_id})
            if not user_data:
                logger.warning(f"User not found with ID: {id_str}")
                return None  

            return self._to_user(user_data)
        except Exception as e:
            logger.error(f"Error fetching user by ID: {e}")
            return None



    def find_user_by_role(self, role: str) -> List[UserModel]:
        
        try:
            users_cursor = self.db.users.find({"role": role})
            raw_users = list(users_cursor)
            return self._to_users(raw_users)
        except Exception as e:
            logger.error(f"Failed to find users by role {role}: {e}")
        return []

    def find_user_by_email(self, email: str) -> Optional[UserModel]:
        try:
            user_data = self.db.users.find_one({"email": email})
            if user_data:
                return self._to_user(user_data)
            return None
        except Exception as e:
            logger.error(f"Failed to find user by email {email}: {e}")
        return None
    

    def find_user_by_username(self, username: str) -> Optional[Dict]:
        try:
            user_data = self.db.users.find_one({"username": username})
            if user_data:
                return self._to_user(user_data) 
            else:
                logger.warning(f"User not found with username: {username}")
            return None
        except Exception as e:
            logger.error(f"Failed to find user by username {username}: {e}")
            return None
        
