from flask import Blueprint, request  # type: ignore
from app.services.teacher_service import TeacherService
from app.auth.jwt_utils import role_required
from app.enums.roles import Role
from app.utils.response_utils import Response  # type: ignore
from app.utils.objectid import ObjectId
from app.utils.console import console
from flask import jsonify , g # type: ignore

teacher_bp = Blueprint('teacher', __name__)
def bson_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, dict):
        return {k: bson_to_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [bson_to_str(i) for i in obj]
    return obj


from app.utils.console import console


@teacher_bp.route('/profile', methods=['GET'])
@role_required([Role.TEACHER.value])
def get_teacher_profile():
    
    
    
    try:
        user = getattr(g, 'user', None)
        if not user or not user.get("id"):
            return jsonify({"error": "Missing user ID"}), 401
        console.print("Fetching teacher profile for user:", user)
        user_id = user.get("id") 

        console.print("User ID:", user_id)
        teacher_info = TeacherService.find_teacher_info_by_user_id(user_id)

        if not teacher_info:
            return Response.not_found_response("Teacher info not found")
        console.print(" teacher_info")

        return Response.success_response(
            data=teacher_info.model_dump(mode="json", by_alias=True,  exclude_none=True),
            message="Teacher profile fetched"
        )
    except Exception as e:
        return Response.error_response(
            message=f"Error fetching teacher info: {str(e)}",
            status_code=500
        )










@teacher_bp.route('/', methods=['patch'])
@role_required([Role.TEACHER.value])
def update_teacher():
    user = getattr(g, 'user', None)
    if not user or not user.get("id"):
        return jsonify({"error": "Missing user ID"}), 401

    user_id = user.get("id")
    update_data = request.get_json()
    
    if not update_data:
        return jsonify({"error": "Missing JSON body"}), 400

    try:
        updated_teacher = TeacherService.edit_teacher(user_id, update_data)
        if not updated_teacher:
            return Response.not_found_response("Teacher info not found")

        return Response.success_response(
            data=updated_teacher.model_dump(mode="json",by_alias=True, exclude_none=True),
            message="Teacher info updated successfully"
        )
    except Exception as e:
        
        return Response.error_response(
            message=f"Error updating teacher info: {str(e)}",
            status_code=500
        )


