from app.models.feedback import FeedbackModel
from app.db import get_db
from app.utils.exceptions import NotFoundError, ValidationError, DatabaseError
from app.utils.objectid import ObjectId # type: ignore
from typing import Optional, List, Dict, Any
from app.utils.dict_utils import flatten_dict
from datetime import datetime, timezone
from app.utils.console import console
from pymongo.database import Database # type: ignore

class FeedbackService:
    def __init__(self, db: Database):
        self.db = db

    def create_feedback(self, feedback: FeedbackModel) -> FeedbackModel:
        try:
            feedback = FeedbackModel(**feedback)
            doc = feedback.to_dict()
            result = self.db.feedback.insert_one(doc)
            return FeedbackModel(**result.inserted_id)
        except Exception as e:
            console.log(f"Failed to create feedback: {e}")
            raise DatabaseError("Error while creating feedback.")

    def get_feedback(self, feedback_id: str) -> FeedbackModel:
        try:
            feedback = self.db.feedback.find_one({"_id": ObjectId(feedback_id)})
            return FeedbackModel(**feedback)
        except Exception as e: