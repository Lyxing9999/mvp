from flask import jsonify, request  # type: ignore
from . import admin_bp
from app.auth.jwt_utils import role_required
from app.services.user_service import UserService

def response(data=None, status=True, msg="", code=200):
    return jsonify({
        "data": data,
        "status": status,
        "msg": msg
    }), code


@admin_bp.route('/', methods=['GET'])
@role_required(['admin'])
def get_all_users():
    """Fetch all users (Admin only)."""
    try:
        users = UserService.find_all_users()
        if not users:
            return response([], True, "No users found")

        user_data = [user.model_dump(by_alias=True) for user in users]
        return response(user_data, True, "Users fetched successfully")

    except Exception as e:
        return response(None, False, f"Error fetching users: {str(e)}", 500)


@admin_bp.route('/', methods=['POST'])
@role_required(['admin'])
def create_user():
    """Create a new user (Admin only)."""
    try:
        data = request.get_json()
        if not data:
            return response(None, False, "Invalid JSON", 400)

        result = UserService.create_user(data)

        if not result.get("status"):
            return response(None, False, result.get("msg", "Unknown error"), 400)

        user = result.get("user")
        return response(user.model_dump(exclude={"password"}), True, "Successfully created user", 201)

    except Exception as e:
        return response(None, False, f"Error creating user: {str(e)}", 500)


@admin_bp.route('/', methods=['PUT'])
@role_required(['admin'])
def edit_user():
    """Edit an existing user (Admin only)."""
    try:
        user_update = request.get_json()
        if not user_update:
            return response(None, False, "Invalid JSON", 400)

        user_id = user_update.get('_id') or user_update.get('id')
        if not user_id:
            return response(None, False, "User ID is required", 400)

        updated_user = UserService.edit_user(user_id, user_update)
        if not updated_user:
            return response(None, False, "User not found or update failed", 404)

        return response(updated_user.model_dump(mode="json", by_alias=True), True, "User updated successfully")

    except Exception as e:
        return response(None, False, f"Error updating user: {str(e)}", 500)


@admin_bp.route('/<user_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_user(user_id):
    """Delete a user by ID (Admin only)."""
    try:
        result = UserService.delete_user(user_id)
        if not result:
            return response(None, False, "User not found or delete failed", 404)

        return response(None, True, "User deleted successfully")

    except Exception as e:
        return response(None, False, f"Error deleting user: {str(e)}", 500)


@admin_bp.route('/search-user', methods=['POST'])
@role_required(['admin'])
def search_user():
    """Search for a user by ID, username, or email (Admin only)."""
    try:
        data = request.get_json()
        if not data:
            return response(None, False, "Invalid JSON", 400)

        user = None
        user_id = data.get('id') or data.get('_id')
        if user_id:
            user = UserService.find_user_by_id(str(user_id))
        elif 'username' in data:
            user = UserService.find_user_by_username(data['username'])
        elif 'email' in data:
            user = UserService.find_user_by_email(data['email'])
        else:
            return response(None, False, "Please provide 'id', 'username', or 'email'", 400)

        if not user:
            return response(None, False, "User not found", 404)

        user_data = user.model_dump(mode="json", by_alias=True, exclude_none=True)
        return response(user_data, True, "User fetched successfully")

    except Exception as e:
        return response(None, False, f"Error fetching user: {str(e)}", 500)
