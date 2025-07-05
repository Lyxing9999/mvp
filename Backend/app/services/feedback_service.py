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