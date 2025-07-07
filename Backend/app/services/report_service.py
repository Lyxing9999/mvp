from app.models.classes import ClassesModel
from app.models.student import StudentModel
from app.models.schedule import ScheduleItemModel
from app.utils.pyobjectid import PyObjectId

class ReportService:
    def __init__(self):
        self.classes = ClassesModel.get_all_classes()
        self.students = StudentModel.get_all_students()
        self.schedule_items = ScheduleItemModel.get_all_schedule_items()
        