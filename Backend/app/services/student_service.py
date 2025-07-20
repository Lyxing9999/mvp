from app.models.student import StudentModel # type: ignore
from typing import Optional, List, Dict, Any, Union
from app.utils.objectid import ObjectId # type: ignore
from pymongo.database import Database # type: ignore
from app.models.user import UserModel # type: ignore
from abc import ABC, abstractmethod
from app.error.exceptions import ExceptionFactory, AppBaseException, InternalServerError    
from app.utils.model_utils import default_model_utils
from app.utils.convert import convert_objectid_to_str

class StudentService(ABC):
    pass


class MongoStudentService(StudentService):
    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db.student
        self.model_utils = default_model_utils
        self._user_service = None
        self._classes_service = None

    @property
    def user_service(self):
        if self._user_service is None:
            from app.services.user_service import get_user_service
            self._user_service = get_user_service(self.db)
        return self._user_service
    @property
    def classes_service(self):
        if self._classes_service is None:
            from app.services.classes_service import get_classes_service
            self._classes_service = get_classes_service(self.db)
        return self._classes_service
    
    def _to_student(self, data: Dict[str, Any]) -> Optional[StudentModel]:
        return self.model_utils.to_model(data, StudentModel)
    
    def _to_student_list(self, data_list: List[Dict[str, Any]]) -> List[UserModel]:
        return self.model_utils.to_model_list(data_list, UserModel)
    
    def _to_objectid(self, id_val: Union[str, ObjectId]) -> Optional[ObjectId]:
        return self.model_utils.validate_object_id(id_val)

    def _prepare_safe_update(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.model_utils.prepare_safe_update(update_data)

    def _convert_objectid_dict(self, data: Dict[str, Any]) -> StudentModel:
        data = convert_objectid_to_str(data)
        return StudentModel(**data) 

    def create_student(self, data: Dict[str, Any]) -> Optional[UserModel]:
        return self.user_service.create_user(data)

        






def get_student_service(db: Database) -> MongoStudentService:
    return MongoStudentService(db)