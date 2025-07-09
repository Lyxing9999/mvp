from app.models.user import UserModel, Role
from app.models.student import StudentModel
from app.models.teacher import TeacherModel
from app.utils.objectid import ObjectId # type: ignore
from typing import Optional, List, Dict, Any, Union, Tuple
from abc import ABC, abstractmethod
from pydantic import ValidationError # type: ignore
from datetime import datetime, timedelta
import logging
import pymongo # type: ignore
from app.utils.model_utils import to_model, to_model_list, to_objectid, prepare_safe_update, validate_object_id # type: ignore
from app.utils.exceptions import NotFoundError, ValidationError, BadRequestError, InternalServerError # type: ignore
from app.database.pipelines.user_pipeline import users_growth_by_role_pipeline, build_user_detail_pipeline, build_user_growth_stats_pipeline, build_search_user_pipeline, build_role_counts_pipeline
from pymongo.database import Database # type: ignore

logger = logging.getLogger(__name__)
class UserRepository(ABC):
    @abstractmethod
    def find_user_by_username(self, username: str) -> Optional[UserModel]:
        pass
    
    @abstractmethod
    def find_all_users(self) -> List[UserModel]:
        pass
    
    @abstractmethod
    def find_user_detail(self, _id: Union[str, ObjectId]) -> Optional[dict]:
        pass

    
class UserRepositoryImpl(UserRepository):
    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db["users"]

    @staticmethod
    def _to_user(data: dict) -> Optional[UserModel]:
        return to_model(data, UserModel)
    
    @staticmethod
    def _to_users(data_list: List[dict]) -> List[UserModel]:
        return to_model_list(data_list, UserModel)

    @staticmethod
    def _to_objectid(id_val: Union[str, ObjectId]) -> Optional[ObjectId]:
        return to_objectid(id_val)
    
    @staticmethod
    def _validate_object_id(_id: Union[str, ObjectId]) -> ObjectId:
        return validate_object_id(_id)


    def find_user_by_username(self, username: str) -> Optional[UserModel]:
        """Find a user by their username
        @param username: str
        @return: UserModel
        @throws: NotFoundError
        @throws: InternalServerError
        """
        try:
            user_data = self.collection.find_one({"username": username})
            if not user_data:
                logger.warning(f"User not found with username: {username}")
                raise NotFoundError(f"User not found with username: {username}")
            return self._to_user(user_data)
        except Exception as e:
            logger.error(f"Failed to find user by username '{username}': {e}")
            raise InternalServerError(f"Failed to find user by username '{username}': {e}")
            
    @staticmethod
    def parse_date_range( start: str, end: str) -> Tuple[datetime, datetime]:
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1) - timedelta(milliseconds=1)
            return start_dt, end_dt



    def find_user_by_id(self, id_str: str) -> Optional[UserModel]: 
        """Find a user by their ID
        @param id_str: str
        @return: UserModel
        @throws: NotFoundError
        @throws: InternalServerError
        """
        obj_id = self._to_objectid(id_str)
        if not obj_id:
            raise BadRequestError(f"Invalid ObjectId: {id_str}")
        try:
            user_data = self.collection.find_one({"_id": obj_id})
            if not user_data:
                logger.warning(f"User not found with ID: {id_str}")
                raise NotFoundError(f"User not found with ID: {id_str}")

            return self._to_user(user_data)
        except Exception as e:
            logger.error(f"Error fetching user by ID: {e}")
            raise InternalServerError(f"Error fetching user by ID: {e}")

            
    def find_all_users(self) -> List[UserModel]:
        """Find all users
        @return: List[UserModel]
        @throws: InternalServerError
        """
        try:
            users_cursor = self.collection.find()
            users_list = list(users_cursor)
            return self._to_users(users_list)
        except Exception as e:
            logger.error(f"Failed to fetch all users: {e}")
            raise InternalServerError(f"Failed to fetch all users: {e}")
        
        
    def search_user(self, query: str, page: int, page_size: int) -> List[UserModel]:
        """Search for users by username or email
        @param query: str
        @param page: int
        @param page_size: int
        @return: List[UserModel]
        @throws: InternalServerError
        """
        try:
            pipeline = build_search_user_pipeline(query, page, page_size)
            users_cursor = self.db.users.aggregate(pipeline)
            users_list = list(users_cursor)
            return self._to_users(users_list)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise InternalServerError(f"Validation error: {e}")
        except TypeError as e:
            logger.error(f"Type error: {e}")
            raise InternalServerError(f"Type error: {e}")
        except pymongo.errors.PyMongoError as e:
            logger.error(f"MongoDB error: {e}")
            raise InternalServerError(f"MongoDB error: {e}")
        except Exception as e:
            logger.error(f"Failed to search users: {e}")
            raise InternalServerError(f"Failed to search users: {e}")

    def find_user_by_email(self, email: str) -> Optional[UserModel]:
        """Find a user by their email
        @param email: str
        @return: UserModel
        @throws: NotFoundError
        @throws: InternalServerError
        """
        try:
            user_data = self.collection.find_one({"email": email})
            if user_data:
                return self._to_user(user_data)
            return None
        except Exception as e:
            logger.error(f"Failed to find user by email {email}: {e}")
            raise InternalServerError(f"Failed to find user by email {email}: {e}")
          
    
        

    def find_user_by_role(self, role: str) -> List[UserModel]:
        """Find users by their role
        @param role: str
        @return: List[UserModel]
        @throws: InternalServerError
        """
        try:
            users_cursor = self.db.users.find({"role": role})
            raw_users = list(users_cursor)
            return self._to_users(raw_users)
        except Exception as e:
            logger.error(f"Failed to find users by role {role}: {e}")
            raise InternalServerError(f"Failed to find users by role {role}: {e}")

        
        
        
    def find_user_detail(self, _id: Union[str, ObjectId]) -> Optional[dict]:
        """Find users detail
        @param _id: Union[str, ObjectId]
        @return: Optional[dict]
        @throws: BadRequestError
        @throws: InternalServerError
        """
        obj_id = self._to_objectid(_id)
        if not obj_id:
            logger.error(f"Invalid ObjectId: {_id}")
            raise BadRequestError(f"Invalid ObjectId: {_id}")
        pipeline = build_user_detail_pipeline(obj_id)
        try:
            data = list(self.collection.aggregate(pipeline))
        except Exception as e:
            print(f"Aggregation failed: {str(e)}")
            raise InternalServerError(f"Aggregation failed: {str(e)}")
            
        if not data:
            logger.warning(f"No user detail found for ID: {_id}")
            raise NotFoundError(f"User detail not found")

        user_doc = data[0]

        user = UserModel.model_validate(user_doc)
        result = {
            "profile": user.model_dump(by_alias=True, exclude={"password"})
        }
        role_model_map = {
            Role.TEACHER.value: (TeacherModel, "teacher"),
            Role.STUDENT.value: (StudentModel, "student"),
            Role.ADMIN.value: (UserModel, "admin"),
        }

        model_class, key = role_model_map.get(user.role, (None, None))
        if model_class and user_doc.get(key):
            result[key] = model_class(**user_doc[key]).model_dump(by_alias=True)

        return result

    def count_users_by_role(self) -> dict:
        try:
            pipeline = [
                {"$group": {"_id": "$role", "count": {"$sum": 1}}}
            ]
            result = self.collection.aggregate(pipeline)
            counts = {role.value: 0 for role in Role}
            for r in result:
                if r["_id"] in counts:
                    counts[r["_id"]] = r["count"]      
            return counts
        except Exception as e:
            logger.error(f"Failed to count users by roles: {e}")
            return {}
    


    def find_user_growth_stats(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        try:
            pipeline = build_user_growth_stats_pipeline(start_date, end_date)
            result = list(self.collection.aggregate(pipeline))

            if not result or ("dailyCounts" not in result[0] and "totalCount" not in result[0]):
                return []

            daily_counts = result[0].get("dailyCounts", [])
            total_count = result[0].get("totalCount", [{}])[0].get("total", 0)

            stats = []
            for entry in daily_counts:
                percent = (entry["count"] / total_count * 100) if total_count > 0 else 0
                stats.append({
                    "date": entry["_id"],
                    "count": entry["count"],
                    "percentage": round(percent, 2)
                })

            return stats
        except Exception:
            logger.exception("Unexpected error in find_user_growth_stats")
            raise InternalServerError("Something went wrong during aggregation")




    def find_users_growth_stats_by_role_with_comparison(
        self,
        current_start_date: str,
        current_end_date: str,
        previous_start_date: str,
        previous_end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Compare user counts by role between two date ranges, calculate growth %.
        """
        current_start_dt, current_end_dt = self.parse_date_range(current_start_date, current_end_date)
        previous_start_dt, previous_end_dt = self.parse_date_range(previous_start_date, previous_end_date)

        def get_role_counts(start_dt: datetime, end_dt: datetime) -> Dict[str, int]:
            pipeline = build_role_counts_pipeline(start_dt, end_dt)
            results = list(self.collection.aggregate(pipeline))
            return {entry["_id"]: entry["count"] for entry in results}

        current_counts = get_role_counts(current_start_dt, current_end_dt)
        previous_counts = get_role_counts(previous_start_dt, previous_end_dt)

        all_roles = set(current_counts.keys()) | set(previous_counts.keys())
        growth_stats = []

        for role in all_roles:
            current = current_counts.get(role, 0)
            previous = previous_counts.get(role, 0)

            if previous == 0:
                growth = 100.0 * current if current > 0 else 0.0
            else:
                growth = ((current - previous) / previous) * 100

            growth_stats.append({
                "role": role,
                "previous": previous,
                "current": current,
                "growth_percentage": round(growth, 2)
            })

        return growth_stats