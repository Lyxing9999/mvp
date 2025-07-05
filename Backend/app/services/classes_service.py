from app.models.classes import ClassesModel
from app.db import get_db
from app.utils.exceptions import NotFoundError, ValidationError, DatabaseError
from app.utils.objectid import ObjectId # type: ignore
from typing import Optional, List, Dict, Any
from app.utils.dict_utils import flatten_dict
from datetime import datetime, timezone
from app.utils.console import console
from pymongo.database import Database # type: ignore


class ClassesService:
    def __init__(self, db: Database):
        self.db = db

    def _to_classes(self, data: Optional[Dict[str, Any]]) -> Optional[ClassesModel]:
        if not isinstance(data, dict) or not data:
            return None
        try:
            return ClassesModel(**data)
        except Exception as e:
            console.log(f"Failed to convert data to ClassesModel: {e}")
            return None
    
    def _to_classes_list(self, data_list: Optional[List[Dict[str, Any]]]) -> List[ClassesModel]:
        if not isinstance(data_list, list):
            return []
        result = []
        for item in data_list:
            model = self._to_classes(item)
            if model:
                result.append(model)
        return result



    def create_class(self, data_list: List[Dict[str, Any]]) -> List[ClassesModel]:
        if not isinstance(data_list, list) or not data_list:
            raise ValidationError("Input data must be a non-empty list.")

        now = datetime.now(timezone.utc)
        for item in data_list:
            item["created_at"] = now
            item["updated_at"] = now

        try:
            result = self.db.classes.insert_many(data_list)
            inserted_ids = result.inserted_ids
            inserted_docs = self.db.classes.find({"_id": {"$in": inserted_ids}})
            return self._to_classes_list(list(inserted_docs))
        except ValidationError as e:
            console.log(f"Failed to create classes: {e}")
            raise ValidationError("Invalid data format.")
        except Exception as e:
            console.log(f"Failed to create classes: {e}")
            raise DatabaseError("Error while creating classes.")





    def get_classes_service(self) -> List[ClassesModel]:
        """
        This function is used to get the classes service instance.
        It is used to get the classes service instance.
        Args:
            db: The database instance.
        Returns:
            ClassesService: The classes service instance.
        Raises:
            ValidationError: If the input data is invalid.
            DatabaseError: If the database operation fails.
        Example:
            >>> from app.services.classes_service import get_classes_service
            >>> from app.db import get_db
            >>> db = get_db()
        """
        try:
            classes = self.db.classes.find()
            return self._to_classes_list(list(classes))
        except Exception as e:
            console.log(f"Failed to get classes: {e}")
            raise DatabaseError("Error while getting classes.")







