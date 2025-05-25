from flask import request, jsonify  # type: ignore
from . import student_bp
from app.models.student import Student
from app.models.user import User
from bson.objectid import ObjectId # type: ignore

@student_bp.route('/create', methods=['POST'])
def create_student():
    try:
        if not request.is_json:
            return jsonify({
                "message": "Invalid or missing JSON",
                "success": False
            }), 400

        data = request.get_json()
        student = Student.create_user(data)

        if student:
            return jsonify({
                "message": "Student created successfully",
                "success": True
            }), 201

        return jsonify({
            "message": "Failed to create student",
            "success": False
        }), 400

    except Exception as e:
        print(f"Error in create_student: {e}")
        return jsonify({
            "message": "An unexpected error occurred!",
            "error": str(e),
            "success": False
        }), 500
    
    
@student_bp.route('/', methods=['GET'])
def get_students():
    try:
        students = Student.find_all_user()
        students_dicts = [student.to_dict() for student in students]
        
        if students_dicts:
            return jsonify({
                "message": "Students retrieved successfully",
                "success": True,
                "data": students_dicts
            }), 200
        
        return jsonify({
            "message": "No students found",
            "success": False
        }), 404

    except Exception as e:
        print(f"Error in get_students: {e}")
        return jsonify({
            "message": "An unexpected error occurred!",
            "error": str(e),
            "success": False
        }), 500
        
        
@student_bp.route('/<student_id>', methods=['GET'])
def get_student_by_id(student_id):
    try:
        result = Student.find_user_by_id(student_id)

        if result:
            return jsonify({
                "message": "Student found",
                "data": result[0].to_dict(),
                "success": True
            }), 200

        return jsonify({
            "message": "Student not found",
            "success": False
        }), 404

    except Exception as e:
        print(f"Error in get_student_by_id: {e}")
        return jsonify({
            "message": "An unexpected error occurred!",
            "error": str(e),
            "success": False
        }), 500
    
    
    
    

@student_bp.route('/<student_id>', methods=["PUT"])
def update_student_by_id(student_id):
    try:
        student_obj_id = ObjectId(student_id)
        update_data = request.json
        if not update_data:
            return jsonify({"error": "No update data provided"}), 400

        result = Student.edit_user(student_obj_id, update_data)
        if result:
            return jsonify({
                "message": "Student updated successfully",
                "success": True
            }), 200
        
        return jsonify({
            "error": "Student not found",
            "success": False
        }), 404

    except Exception as e:
        print(f"Error in update_student_by_id: {e}")
        return jsonify({
            "error": str(e),
            "success": False
        }), 500
    
    
    
@student_bp.route('/delete<student_id>', methods=['DELETE'])
def delete_student_by_id(student_id):
    try:
        student_obj_id = ObjectId(student_id)
        result = Student.delete_user(student_obj_id)

        if result:
            return jsonify({
                "message": "Student deleted successfully",
                "success": True
            }), 200

        return jsonify({
            "message": "Failed to delete student",
            "success": False
        }), 400

    except Exception as e:
        print(f"Error in delete_student_by_id: {e}")
        return jsonify({
            "message": "An unexpected error occurred!",
            "error": str(e),
            "success": False
        }), 500
    
    
        
