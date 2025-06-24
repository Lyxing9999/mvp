from app.models.teacher import TeacherModel, TeacherInfoModel
from app.db import get_db
from typing import Optional, Dict, Any
from app.utils.objectid import ObjectId
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)
db = get_db()


class TeacherService:
    @staticmethod
    def _to_objectid(id_value: str | ObjectId) -> Optional[ObjectId]:
        try:
            if isinstance(id_value, ObjectId):
                return id_value
            if isinstance(id_value, str) and ObjectId.is_valid(id_value):
                return ObjectId(id_value)
        except Exception:
            pass
        return None


    @classmethod
    def find_teacher_info_by_user_id(cls, user_id: ObjectId) -> Optional[TeacherModel]:
        obj_user_id = cls._to_objectid(user_id)
        if not obj_user_id:
            return None
        try:
            user_id = db.teacher_info.distinct("user_id")
            print("All user_ids in user_id:", user_id)
            doc = db.teacher_info.find_one({"user_id": obj_user_id})

            if not doc:
                return None
            doc["teacher_info"] = TeacherInfoModel.model_validate(doc.get("teacher_info", {}))    
            print("Teacher info found for user_id:", user_id) 
            print("Teacher info document:", doc)       
            teacher_model = TeacherModel.model_validate(doc)
            return teacher_model
        except Exception as e:
            logger.error(f"Error finding teacher info by user_id: {e}")
            return None
        
        
        
        
        
        
    @classmethod
    def edit_teacher(cls, user_id: str | ObjectId, update_data: dict) -> Optional[TeacherModel]:
        obj_user_id = cls._to_objectid(user_id)
        if not obj_user_id:
            return None
        try:
            existing_doc = db.teacher_info.find_one({"user_id": obj_user_id})
            if not existing_doc:
                return None

            # Defensive copy
            update_data_copy = dict(update_data)
            if "user_id" in update_data_copy:
                update_data_copy.pop("user_id")
            teacher_info_dict = update_data_copy.get("teacher_info")
            if teacher_info_dict:
                teacher_info_dict["updated_at"] = datetime.now(timezone.utc)
                update_data_copy["teacher_info"] = TeacherInfoModel.model_validate(teacher_info_dict).model_dump()

            update_data_copy["updated_at"] = datetime.now(timezone.utc)

            db.teacher_info.update_one(
                {"user_id": obj_user_id},
                {"$set": update_data_copy}
            )
            new_doc = db.teacher_info.find_one({"user_id": obj_user_id})

            logger.info(f"Teacher info updated for user_id={user_id}: {new_doc}")
            return TeacherModel.model_validate(new_doc)

        except Exception as e:
            logger.error(f"Error updating TeacherModel: {e}")
            return None

        
    
    
    
    @classmethod
    def delete_teacher_info(cls, user_id: str | ObjectId) -> bool:
        obj_user_id = cls._to_objectid(user_id)
        if not obj_user_id:
            return False

        try:
            result = db.teacher_info.delete_one({"user_id": obj_user_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting teacher_info document: {e}")
            return False
