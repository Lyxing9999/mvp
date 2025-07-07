from app.models.feedback import FeedbackModel
from app.database.db import get_db
from app.utils.exceptions import NotFoundError, ValidationError, DatabaseError
from app.utils.objectid import ObjectId # type: ignore
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
from app.utils.console import console
from pymongo.database import Database # type: ignore

class FeedbackService:
    def __init__(self, db: Database):
        self.db = db
    def _to_objectid(self, id_val: Union[str, ObjectId]) -> Optional[ObjectId]:
        if isinstance(id_val, ObjectId):
            return id_val
        if isinstance(id_val, str) and ObjectId.is_valid(id_val):
            return ObjectId(id_val)
        return None
    def create_feedback(self, feedback: FeedbackModel) -> FeedbackModel:
        try:
            feedback = FeedbackModel(**feedback)
            doc = feedback.to_dict()
            result = self.db.feedback.insert_one(doc)
            return FeedbackModel(**result.inserted_id)
        except Exception as e:
            console.log(f"Failed to create feedback: {e}")
            raise DatabaseError("Error while creating feedback.")

    def get_feedback(self, _id: str) -> Optional[FeedbackModel]:
        """
        Get a feedback by its ID.

        Args:
            feedback_id (str): The ID of the feedback to retrieve.

        Returns:
            FeedbackModel: The feedback object if found, None otherwise.

        Raises:
            NotFoundError: If the feedback is not found.
            ValidationError: If the feedback ID is invalid.
            DatabaseError: If there is an error accessing the database.
        """
        try:
            feedback_id = self._to_objectid(_id)
            if not feedback_id:
                raise ValidationError("Invalid feedback ID format")
            result = self.db.feedback.find_one({"_id": feedback_id}) 
            return FeedbackModel(**result) if result else None
        except Exception as e:
            console.log(f"Error fetching feedback by ID {feedback_id}: {str(e)}")
            raise DatabaseError("Failed to fetch feedback")
        
