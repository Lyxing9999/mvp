from flask import Blueprint, request  # type: ignore
from app.services.teacher_service import MongoTeacherService
from app.auth.jwt_utils import role_required
from app.enums.roles import Role
from app.utils.response_utils import Response  # type: ignore
from app.utils.objectid import ObjectId # type: ignore
from app.utils.console import console
from flask import jsonify , g # type: ignore
from app.database.db import get_db # type: ignore
from app.models.classes  import ClassesModel  
import logging
from app.schemas.teacher_schema import TeacherCreateSchema
from app.utils.exceptions import NotFoundError, ValidationError, DatabaseError
logger = logging.getLogger(__name__)
from functools import wraps


teacher_bp = Blueprint('teacher', __name__)



def with_teacher_service(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        g.teacher_service = MongoTeacherService(get_db())
        return func(*args, **kwargs)
    return wrapper


@teacher_bp.route('/profile', methods=['GET'])
@role_required([Role.TEACHER.value])
@with_teacher_service
def get_teacher_profile():
    """Get teacher profile (Teacher only)."""
    try:
        user = getattr(g, 'user', None)
        user_id = user.get("id") if user else None

        if not user_id:
            return Response.error_response(
                message="Missing user ID",
                status_code=401
            )

        teacher_info = g.teacher_service.get_teacher_by_id(user_id)
        if not teacher_info:
            return Response.not_found_response("Teacher info not found")
        return Response.success_response(
            data=teacher_info.model_dump(mode="json", by_alias=True,  exclude_none=True),
            message="Teacher profile fetched"
        )
    except Exception as e:
        return Response.error_response(
            message=f"Error fetching teacher info: {str(e)}",
            status_code=500
        )

@teacher_bp.route('/create', methods=['POST'])
@role_required([Role.TEACHER.value])
@with_teacher_service
def create_teacher_profile():
    """Create teacher profile (Teacher only)."""
    try:
        user = getattr(g, 'user', None)
        user_id = user.get("id") if user else None
        if not user_id:
            return jsonify({"error": "Missing user ID"}), 401
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        user_data = {
            "username": data.get("username"),
            "email": data.get("email"),
            "password": data.get("password"),
            "role": Role.TEACHER.value
        }
        user_data = TeacherCreateSchema(**user_data).model_dump(by_alias=True)
        teacher_service = g.teacher_service
        result = teacher_service.create_teacher(user_data)

        return Response.success_response(
            data=result.model_dump(mode="json", by_alias=True, exclude_none=True),
            message="Teacher profile created"
        )
    except Exception as e:
        return Response.error_response(
            message=f"Error creating teacher profile: {str(e)}",
            status_code=500
        )

@teacher_bp.route('/profile', methods=['PATCH'])
@role_required([Role.TEACHER.value])
@with_teacher_service
def patch_teacher_profile():
    """Update teacher profile (Teacher only)."""
    try:
        user = getattr(g, 'user', None)
        user_id = user.get("id") if user else None
        if not user_id:
            return jsonify({"error": "Missing user ID"}), 401
        
        update_data = request.get_json()
        if not update_data:
            return jsonify({"error": "No data provided"}), 400
        
        updated_teacher = g.teacher_service.patch_teacher(user_id, update_data)
        
        if not updated_teacher:
            return Response.not_found_response("Teacher info not found or update failed")
        
        return Response.success_response(
            data=updated_teacher.model_dump(mode="json", by_alias=True, exclude_none=True),
            message="Teacher profile updated"
        )
    except Exception as e:
        return Response.error_response(
            message=f"Error updating teacher info: {str(e)}",
            status_code=500
        )




@teacher_bp.route('/classes', methods=['GET'])
@role_required([Role.TEACHER.value])
@with_teacher_service
def get_teacher_classes():
    """
    Get all classes assigned to the currently authenticated teacher.
    Returns:
        JSON response containing list of teacher's classes
    Raises:
        401: User not authenticated
        404: No classes found for teacher
        500: Internal server error
    """
    try:
        user = getattr(g, 'user', None)
        user_id = user.get("id") if user else None
        

        if not user_id:
            logger.warning("Missing user ID in JWT context")
            return Response.error_response(
                message="Invalid authentication context",
                status_code=401
            )
        
        logger.info(f"Fetching classes for teacher ID: {user_id}")
        
        classes = g.teacher_service.get_classes_by_teacher_id(user_id)
        
        if not classes:
            logger.info(f"No classes found for teacher ID: {user_id}")
            return Response.error_response(
                message="No classes found for this teacher",
                status_code=404
            )
        
        serialized_classes = [
            ClassesModel.model_validate(cls).model_dump(
                mode="json",
                by_alias=True
            )
            for cls in classes
        ]
        
        logger.info(f"Successfully retrieved {len(classes)} classes for teacher {user_id}")
        return Response.success_response(
            data=serialized_classes,
            message=f"Retrieved {len(classes)} classes successfully"
        )
        
    except NotFoundError as e:
        logger.warning(f"Teacher not found: {user_id} - {str(e)}")
        return Response.error_response(
            message="Teacher not found",
            status_code=404
        )
    except ValidationError as e:
        logger.error(f"Validation error for teacher {user_id}: {str(e)}")
        return Response.error_response(
            message="Data validation failed",
            status_code=422
        )
    except DatabaseError as e:
        logger.error(f"Database error for teacher {user_id}: {str(e)}")
        return Response.error_response(
            message="Database operation failed",
            status_code=500
        )
    except Exception as e:
        logger.error(f"Unexpected error for teacher {user_id}: {str(e)}", exc_info=True)
        return Response.error_response(
            message="An unexpected error occurred",
            status_code=500
        )


        
@teacher_bp.route('/classes/<class_id>', methods=['GET'])
@role_required([Role.TEACHER.value])
@with_teacher_service
def get_class(class_id):
    """Get detailed info for a specific class
    @param class_id: str
    @return: ClassResponseSchema
    @throws: Exception
    """
    pass




@teacher_bp.route('/classes/<class_id>/students', methods=['GET'])
@role_required([Role.TEACHER.value])
@with_teacher_service
def get_class_students(class_id):
    """List students enrolled in a class

    @param class_id: str
    @return: List[StudentResponseSchema]
    @throws: Exception
    """
    pass


@teacher_bp.route('/attendance', methods=['POST'])
@role_required([Role.TEACHER.value])
def mark_attendance():
    """Mark attendance for students (bulk for a class & date)
    @param class_id: str
    @return: AttendanceResponseSchema
    @throws: Exception
    """
    pass

@teacher_bp.route('/attendance/<attendance_id>', methods=['GET'])
@role_required([Role.TEACHER.value])
def get_attendance_by_id(attendance_id):
    """Get attendance for a class by id
    @param attendance_id: str
    @return: AttendanceResponseSchema
    @throws: Exception
    """
    pass


@teacher_bp.route('/attendance/<attendance_id>', methods=['PATCH'])
@role_required([Role.TEACHER.value])
def patch_attendance(attendance_id):
    """Patch a specific attendance record

    @param attendance_id: str
    @return: AttendanceResponseSchema
    @throws: Exception
    """
    pass

@teacher_bp.route('/grades', methods=['POST'])
@role_required([Role.TEACHER.value])
def submit_grades():
    """Submit grades/comments for students


    @param class_id: str
    @return: List[GradeResponseSchema]
    @throws: Exception
    """
    pass


@teacher_bp.route('/grades/<grade_id>', methods=['GET'])
@role_required([Role.TEACHER.value])
def get_grade(grade_id):
    """View a specific grade record

    @param grade_id: str
    @return: GradeResponseSchema
    @throws: Exception
    """
    pass


@teacher_bp.route('/notifications', methods=['GET'])
@role_required([Role.TEACHER.value])
def get_notifications():
    """Fetch notifications relevant to the teacher

    @return: List[NotificationResponseSchema]
    @throws: Exception
    """
    pass


@teacher_bp.route('/notifications/<notif_id>', methods=['GET'])
@role_required([Role.TEACHER.value])
def get_notification(notif_id):
    """View a specific notification (read/unread status)
    @param notif_id: str
    @return: NotificationResponseSchema
    @throws: Exception
    """
    pass

@teacher_bp.route('/feedback', methods=['POST'])
@role_required([Role.TEACHER.value])
def submit_feedback():
    """Send feedback  or comments

    @return: FeedbackResponseSchema
    @throws: Exception
    """
    pass



@teacher_bp.route('/feedback/<feedback_id>', methods=['GET'])
@role_required([Role.TEACHER.value])
def get_feedback(feedback_id):
    """View a specific feedback record

    @param feedback_id: str
    @return: FeedbackResponseSchema
    @throws: Exception
    """
    pass