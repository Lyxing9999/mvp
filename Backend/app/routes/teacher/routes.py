from . import teacher_bp
from flask import request, jsonify  # type: ignore - Flask does not provide type hints for this import
from app.models.teacher_model import Teacher
from app.models.user_model import User

@teacher_bp.route('/create', methods=['POST'])
def create_teacher():
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Invalid or missing JSON",
            "data": None
        }), 400
    data = request.json
    try:
        result = Teacher.create_user(data)
        if result:
            return jsonify({
                "success": True,
                "data": result.to_dict(),
                "message": "Teacher created successfully"
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": "Failed to create teacher",
                "data": None
            }), 400
    except Exception as e:
        print("Error:", str(e))
        return jsonify({
            "success": False,
            "error": str(e),
            "data": None
        }), 500
    
    


@teacher_bp.route('/', methods=['GET'])
def get_teacher():
    try:
        result = Teacher.find_user_by_role("teacher")
        teachers = [teacher.to_dict() for teacher in result]
        if teachers:
            return jsonify({
                "message": "Teachers retrieved successfully",
                "success": True,
                "data": teachers
            }), 200
        else:
            return jsonify({
                "message": "No teachers found",
                "success": False,
                "data": []
            }), 404

    except Exception as e:
        return jsonify({
            "message": "An unexpected error occurred!",
            "error": str(e),
            "success": False
        }), 500
    