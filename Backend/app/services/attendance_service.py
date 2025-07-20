from pymongo.database  import Database
from app.models import attendance
from app.models.classes import get_classes_service
from app.models.student import get_student_service 
from abc  import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.utils.pyobjectid import PyObjectId
from app.utils.model_utils import ModelUtils


class AttendanceService(ABC):
    def __init__(self, db: Database): 
        self.db = db
        self.collection = self.db["users"]