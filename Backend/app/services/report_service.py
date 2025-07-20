from app.models.report import ReportModel
from app.utils.model_utils import ModelUtils
from app.error.exceptions import AppBaseException, ExceptionFactory, InternalServerError, NotFoundError, ValidationError
from app.database.db import get_db
from app.services.user_service import MongoUserService
from app.services.teacher_service import MongoTeacherService
from app.utils.model_utils import ModelUtils
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from app.utils.objectid import ObjectId
from pymongo import Database # type: ignore

class ReportService(ABC):
    @abstractmethod
    def create_report(self, data: Dict[str, Any]) -> Optional[ReportModel]:
        pass

    @abstractmethod
    def get_report_by_id(self, _id: Union[str, ObjectId]) -> Optional[ReportModel]:
        pass



class MongoReportService(ReportService):
    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db.report_info
        self.model_utils = ModelUtils()

    def _to_report(self, data: Dict[str, Any]) -> Optional[ReportModel]:
        return self.model_utils.to_model(data, ReportModel)

    def _to_reports(self, data_list: List[Dict[str, Any]]) -> List[ReportModel]:
        return self.model_utils.to_model_list(data_list, ReportModel)


    def create_report(self, data: Dict[str, Any]) -> Optional[ReportModel]:
        try:
            report = self._to_report(data)
            if not report:
                raise ExceptionFactory.validation_failed(field="data", value=data, reason="Invalid report data")
            result = self.collection.insert_one(report.model_dump(by_alias=True))
            if not result.acknowledged:
                raise InternalServerError(message="Failed to create report in database", details={"data": data})
            _id = result.inserted_id
            return self._to_report(result.inserted_id)
        
        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while creating report", cause=e)

        