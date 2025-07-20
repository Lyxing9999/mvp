from app.models.feedback import FeedbackModel
from app.database.db import get_db
from app.error.exceptions import NotFoundError, ValidationError, DatabaseError, ExceptionFactory, InternalServerError, AppBaseException, BadRequestError, ErrorCategory, ErrorSeverity , AppTypeError
from app.utils.convert import convert_objectid_to_str
from app.utils.objectid import ObjectId # type: ignore
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
from pymongo.database import Database # type: ignore
from app.utils.model_utils import default_model_utils
from abc import ABC, abstractmethod
from pymongo.database import Database
import logging
logger = logging.getLogger(__name__)

class FeedbackService(ABC):
    pass

class MongoFeedbackService(FeedbackService):
    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db.feedback
        self.model_utils = default_model_utils

    def _to_feedback(self, data: Dict[str, Any]) -> Optional[FeedbackModel]:
        return self.model_utils.to_model(data, FeedbackModel)
    
    def _to_feedback_list(self, data_list: List[Dict[str, Any]]) -> List[FeedbackModel]:
        return self.model_utils.to_model_list(data_list, FeedbackModel)
    
    def _to_objectid(self, id_val: Union[str, ObjectId]) -> Optional[ObjectId]:
        return self.model_utils.validate_object_id(id_val)
    
    def _prepare_safe_update(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.model_utils.prepare_safe_update(update_data)
    
    def _convert_objectid_dict(self, data: Dict[str, Any]) -> Optional[FeedbackModel]:
        data = convert_objectid_to_str(data)
        return FeedbackModel(**data)
    
    def _fetch_first_inserted(self, inserted_id: ObjectId) ->  Optional[FeedbackModel]:
        if not inserted_id:
            raise NotFoundError(
                message="No classes inserted",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
                status_code=404
            )
        raw_doc = self.collection.find_one({"_id": inserted_id})
        if not raw_doc:
            raise NotFoundError(message="No classes inserted", severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE, status_code=404)
        return self._convert_objectid_dict(raw_doc)
    
    def create_feedback(self,  data: Dict[str, Any]) -> Optional[FeedbackModel]:
        
        try:
            feedback = self._to_feedback(data)
            if not feedback:
                raise ExceptionFactory.validation_failed(field="data", value=data, reason="Invalid feedback data")
            result = self.collection.insert_one(feedback.model_dump(by_alias=True, exclude_none=True))
            if not result.acknowledged:
                raise InternalServerError(message="Failed to create feedback in database", details={"data": data})
            return self._fetch_first_inserted(result.inserted_id)
        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while creating feedback", cause=e)
