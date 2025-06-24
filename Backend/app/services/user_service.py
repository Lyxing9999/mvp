from app.models.user import UserModel
from app.db import get_db
from app.enums.roles import Role
from app.utils.objectid import ObjectId # type: ignore
from typing import List, Optional, Dict, Any, Union
from werkzeug.security import generate_password_hash  # type: ignore
from app.models.student import StudentModel
import logging
from pydantic import ValidationError # type: ignore
from app.models.teacher import TeacherModel
from datetime import datetime, timedelta, timezone
from app.utils.console import console

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
    def _to_users(data_list: List[dict]) -> List[UserModel]:
        return [UserModel.model_validate(data) for data in data_list if data]

    @staticmethod
    def _to_objectid(id_val: str | ObjectId) -> Optional[ObjectId]:
        if isinstance(id_val, ObjectId):
            return id_val
        try:
            return ObjectId(id_val)
        except Exception as e:
            logger.error(f"Invalid ObjectId: {e}")
            return None

    @classmethod
    def ensure_date(cls, value: Any) -> Any:
        try:
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    return None
            if isinstance(value, datetime):
                return value.isoformat()
            if isinstance(value, ObjectId):
                return str(value)
            return None
        except Exception as e:
            logger.error(f"Error ensuring date: {e}")
            return None

    @classmethod
    def flatten_dict(cls, d: dict, parent_key: str = '', sep: str = '.') -> dict:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict) and v is not None:
                items.extend(cls.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

        
    @classmethod
    def _find_user_by_id_and_role(cls, id_str: str | ObjectId, role: str) -> Optional[UserModel]:
        
        obj_id = cls._to_objectid(id_str) if isinstance(id_str, str) else id_str
        if not obj_id:
            logger.warning(f"Invalid ObjectId: {id_str}")
            return None
        try:
            user_data = db.users.find_one({"_id": obj_id, "role": role})
            return cls._to_user(user_data) if user_data else None
        except Exception as e:
            logger.error(f"Failed to fetch {role} by ID: {e}")
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
            role_data["user_id"] = user_id
            
            if role == Role.STUDENT.value:
                new_student = StudentModel.create_minimal(user_id=user_id)
                doc = new_student.model_dump(by_alias=True)
                doc["_id"] = doc.pop("id", None) or user_id
                if "user_id" in doc and isinstance(doc["user_id"], str):
                    doc["user_id"] = ObjectId(doc["user_id"])
                console.print(f"Creating student info for user_id: {user_id}, doc: {doc}")
                console.print(type(doc["user_id"]))
                db.student_info.insert_one(doc)
                
            elif role == Role.TEACHER.value:

                new_teacher = TeacherModel.create_minimal(user_id=user_id)
                doc = new_teacher.model_dump(by_alias=True)
                doc["_id"] = doc.pop("id", None) or user_id
                if "user_id" in doc and isinstance(doc["user_id"], str):
                    doc["user_id"] = ObjectId(doc["user_id"])
                db.teacher_info.insert_one(doc)
            elif role == Role.ADMIN.value:
                db.admin_info.insert_one(role_data)
            user.id = str(user_id)
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
        
        
        
    @classmethod
    def find_teacher_by_id(cls, teacher_id: Union[str, ObjectId]) -> Optional[UserModel]:
        return cls._find_user_by_id_and_role(teacher_id, Role.TEACHER.value)
        
        

        
    @classmethod
    def find_student_by_id(cls, student_id: Union[str, ObjectId]) -> Optional[UserModel]:
        return cls._find_user_by_id_and_role(student_id, Role.STUDENT.value)

    @classmethod
    def find_admin_by_id(cls, admin_id: Union[str, ObjectId]) -> Optional[UserModel]:
        return cls._find_user_by_id_and_role(admin_id, Role.ADMIN.value)

    @classmethod
    def count_users_by_role(cls) -> dict:
        try:
            pipeline = [
                {"$group": {"_id": "$role", "count": {"$sum": 1}}}
            ]
            result = db.users.aggregate(pipeline)
            
            # Initialize counts for all roles with 0
            counts = {role.value: 0 for role in Role}
            
            # Update counts with actual values
            for r in result:
                if r["_id"] in counts:
                    counts[r["_id"]] = r["count"]      
            return counts
        except Exception as e:
            logger.error(f"Failed to count users by roles: {e}")
            return {}
    
    
    @classmethod
    def find_user_growth_stats(cls, start_date: str, end_date: str) -> List[Dict[str, Any]]:

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

            result = list(db.users.aggregate(pipeline))
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
            
    @classmethod
    def find_users_growth_stats_by_role(cls, start_date: str, end_date: str) -> List[Dict[str, Any]]:

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

            result = list(db.users.aggregate(pipeline))
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

    @classmethod
    def find_users_growth_stats_by_role_with_comparison( cls, current_start_date: str, current_end_date: str, previous_start_date: str,previous_end_date: str) -> List[Dict[str, Any]]:
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
            results = list(db.users.aggregate(pipeline))
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
        
        
    @classmethod    
    def find_users_detail(cls, user_id: Union[str, ObjectId]) -> Optional[dict]:
        obj_id = cls._to_objectid(user_id)
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
            data = list(db.users.aggregate(pipeline))
        except Exception as e:
            print(f"Aggregation failed: {str(e)}")
            return None

        user_doc = data[0]

        # Parse base user info
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




  
    @classmethod
    def edit_user_detail(cls, user_id: Union[str, ObjectId], user_update_data: dict) -> Optional[dict]:
        obj_id = cls._to_objectid(user_id)
        if not obj_id:
            logger.error(f"Invalid ObjectId: {user_id}")
            return None
        try:
            # STEP 1: Find full user with embedded info (admin/teacher/student)
            full_user = cls.find_users_detail(obj_id)
            if not full_user:
                logger.error(f"User not found with _id: {obj_id}")
                return None

            base_user = full_user["profile"]
            role = base_user.get("role")
            logger.info(f"User found with role: {role}")

            # STEP 2: Identify role and collection to update
            if role == Role.TEACHER.value:
                collection = db.teacher_info
            elif role == Role.STUDENT.value:
                collection = db.student_info
            elif role == Role.ADMIN.value:
                collection = db.admin_info
            else:
                logger.warning(f"Unknown role: {role}")
                return None

            # STEP 3: Prepare safe update (don’t allow _id or role)

            safe_update = dict(user_update_data)
            safe_update.pop("_id", None)
            safe_update.pop("role", None)
          
            if not safe_update:
                logger.warning("No valid fields to update.")
                return None
            if role == Role.TEACHER.value:
                teacher_info = safe_update.get("teacher_info", {})
                teacher_info["updated_at"] = datetime.now(timezone.utc)
                
                safe_update["teacher_info"] = teacher_info
                safe_update["phone_number"] = user_update_data.get("phone_number")

            elif role == Role.STUDENT.value:
                student_info = safe_update.get("student_info", {})
                student_info["updated_at"] = datetime.now(timezone.utc)

                
                student_info["birth_date"] = cls.ensure_date(student_info.get("birth_date"))

                safe_update["student_info"] = student_info

            elif role == Role.ADMIN.value:
                admin_info = safe_update.get("admin_info", {})
                admin_info["updated_at"] = datetime.now(timezone.utc)
                safe_update["admin_info"] = admin_info
            safe_update = cls.flatten_dict(safe_update)
            # STEP 4: Patch the correct role-specific collection
            update_result = collection.update_one(
                {"user_id": obj_id},
                {"$set": safe_update}
            )


            if update_result.modified_count > 0:
                return {"status": True, "msg": "User info updated successfully"}
            else:
                return {"status": True, "msg": "No changes detected"}

        except Exception as e:
            logger.exception(f"Exception in edit_user_detail: {e}")
            return None