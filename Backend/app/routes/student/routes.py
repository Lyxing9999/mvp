from flask import request, jsonify  # type: ignore
from . import student_bp
from app.models.student_model import Student
from bson.objectid import ObjectId # type: ignore
from app.utils.convert import convert_objectid_to_str
import json

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
    
    
        
@student_bp.route('/<user_id>', methods=['GET'])
def get_student_by_user_id(user_id):
    try:
        student_info = Student.find_student_info_by_id(user_id)
        
        
        if student_info:
            clean_result = convert_objectid_to_str(student_info)
            return jsonify({
                "message": "Student found",
                "data": clean_result,
                "success": True
            }), 200

        return jsonify({
            "message": "Student not found",
            "success": False
        }), 404

    except Exception as e:
        print(f"Error: {e}")
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
    
    
        
