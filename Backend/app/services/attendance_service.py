from app.models.classes import ClassesModel
from app.models.student import StudentModel
from app.models.schedule import ScheduleItemModel
from app.utils.pyobjectid import PyObjectId


class AttendanceService:
    def __init__(self):
        self.classes = ClassesModel.get_all_classes()
        self.students = StudentModel.get_all_students()
        self.schedule_items = ScheduleItemModel.get_all_schedule_items()

    def get_attendance_by_class_id(self, class_id: str):
        return self.classes.get(class_id)
    
    def get_attendance_by_student_id(self, student_id: str):
        return self.students.get(student_id)
    
    def get_attendance_by_schedule_item_id(self, schedule_item_id: str):
        for class_ in self.classes:
            for schedule_item in class_.schedule:
                if schedule_item.id == schedule_item_id:
                    return schedule_item
        return None
    
    def get_attendance_by_class_id_and_student_id(self, class_id: str, student_id: str):
        return self.classes.get(class_id).students.get(student_id)