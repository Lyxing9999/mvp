from flask import request  # type: ignore
from . import admin_bp
from app.auth.jwt_utils import role_required
from app.services.user_service import UserService
from app.enums.roles import Role
from app.utils.response_utils import Response  # type: ignore 




@admin_bp.route('/', methods=['GET'])
@role_required([Role.ADMIN.value])
def get_all_users():
    """Fetch all users (Admin only)."""
    try:

        users = UserService.find_all_users()
        if not users:
            return Response.success_response(data=[], message="No users found")

        user_data = [user.model_dump(exclude={"password"},by_alias=True) for user in users]
        return Response.success_response(user_data, message="Users fetched successfully")

    except Exception as e:
        return Response.error_response(message=f"Error fetching users: {str(e)}", status_code=500)


@admin_bp.route('/users', methods=['POST'])
@role_required([Role.ADMIN.value])
def create_user():
    """Create a new user (Admin only)."""
    try:
        data = request.get_json()
        if not data:
            return Response.error_response(message="Invalid JSON", status_code=400)

        result = UserService.create_user(data)
        if not result.get("status"):
            return Response.error_response(message=result.get("msg", "Unknown error"), status_code=400)

        user = result.get("user")
        return Response.success_response(user.model_dump(exclude={"password"}), message="Successfully created user", status_code=201)

    except Exception as e:
        return Response.error_response(message=f"Error creating user: {str(e)}", status_code=500)


@admin_bp.route('/users', methods=['PUT'])
@role_required([Role.ADMIN.value])
def edit_user():
    """Edit an existing user (Admin only)."""
    try:
        user_update = request.get_json()
        if not user_update:
            return Response.error_response(message="Invalid JSON", status_code=400)

        user_id = user_update.get('_id') or user_update.get('id')
        if not user_id:
            return Response.error_response(message="User ID is required", status_code=400)

        updated_user = UserService.edit_user(user_id, user_update)
        if not updated_user:
            return Response.not_found_response("User not found or update failed")

        return Response.success_response(updated_user.model_dump(mode="json", by_alias=True), message="User updated successfully")

    except Exception as e:
        return Response.error_response(message=f"Error updating user: {str(e)}", status_code=500)


@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@role_required([Role.ADMIN.value])
def delete_user(user_id):
    """Delete a user by ID (Admin only)."""
    try:
        result = UserService.delete_user(user_id)
        if not result:
            return Response.not_found_response("User not found or delete failed")

        return Response.success_response(message="User deleted successfully")

    except Exception as e:
        return Response.error_response(message=f"Error deleting user: {str(e)}", status_code=500)


@admin_bp.route('/users/search-user', methods=['POST'])
@role_required([Role.ADMIN.value])
def search_user():
    """Search for a user by ID, username, or email (Admin only)."""
    try:
        data = request.get_json()
        if not data:
            return Response.error_response(message="Invalid JSON", status_code=400)

        user = None
        user_id = data.get('id') or data.get('_id')
        if user_id:
            user = UserService.find_user_by_id(str(user_id))
        elif 'username' in data:
            user = UserService.find_user_by_username(data['username'])
        elif 'email' in data:
            user = UserService.find_user_by_email(data['email'])
        else:
            return Response.error_response(message="Please provide 'id', 'username', or 'email'", status_code=400)

        if not user:
            return Response.not_found_response("User not found")

        user_data = user.model_dump(mode="json", by_alias=True, exclude_none=True)
        return Response.success_response(user_data, message="User fetched successfully")

    except Exception as e:
        return Response.error_response(message=f"Error fetching user: {str(e)}", status_code=500)


@admin_bp.route('/users/count-by-role', methods=['GET'])
@role_required([Role.ADMIN.value])
def count_users_by_role():
    """Count users by role (Admin only)."""
    try:
        counts = UserService.count_users_by_role()
        return Response.success_response(counts, message="User counts by role fetched successfully")

    except Exception as e:
        return Response.error_response(message=f"Error counting users by role: {str(e)}", status_code=500)




@admin_bp.route('/users/growth-stats', methods=['GET'])
@role_required([Role.ADMIN.value])
def get_user_growth_stats():
    """Get user growth statistics (Admin only)."""
    try:
        # Get query params from URL like ?start_date=2025-01-01&end_date=2025-06-10
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        # Optional: validate dates here or set defaults if missing
        if not start_date or not end_date:
            return Response.error_response(message="Missing start_date or end_date query parameters", status_code=400)

        stats = UserService.find_user_growth_stats(start_date=start_date, end_date=end_date)
        print(f"User growth stats from {start_date} to {end_date}: {stats}")
        return Response.success_response(stats, message="User growth statistics fetched successfully")

    except Exception as e:
        return Response.error_response(message=f"Error fetching user growth stats: {str(e)}", status_code=500)



@admin_bp.route('/users/growth-stats-by-role', methods=['GET'])
@role_required([Role.ADMIN.value])
def get_user_growth_stats_by_role():  # Changed function name to match route
    """Get user growth statistics by role (Admin only)."""
    try:
        # Get query params from URL like ?start_date=2025-01-01&end_date=2025-06-10
        current_start_date = request.args.get('current_start_date')
        current_end_date = request.args.get('current_end_date')
        previous_start_date = request.args.get('previous_start_date')
        previous_end_date = request.args.get('previous_end_date')
        if not current_start_date or not current_end_date:
            return Response.error_response(message="Missing current_start_date or current_end_date query parameters", status_code=400)
        if not previous_start_date or not previous_end_date:
            return Response.error_response(message="Missing previous_start_date or previous_end_date query parameters", status_code=400)
        
        # Optional: validate dates here or set defaults if missing
    
        stats = UserService.find_users_growth_stats_by_role_with_comparison(current_start_date=current_start_date, current_end_date=current_end_date,  previous_start_date=previous_start_date, previous_end_date=previous_end_date)
        print(f"User growth stats by role from {current_start_date} to {current_end_date} and {previous_start_date} to {previous_end_date}: {stats}")
        return Response.success_response(stats, message="User growth statistics fetched successfully")

    except Exception as e:
        return Response.error_response(message=f"Error fetching user growth stats: {str(e)}", status_code=500)






@admin_bp.route('/users/detail/<user_id>', methods=['GET'])
@role_required([Role.ADMIN.value])
def get_user_detail(user_id):
    """Get detailed information about a user by ID (Admin only)."""
    try:


        user = UserService.find_users_detail(user_id)
        print(f"User details for ID {user_id}: {user}")
        if not user:
            return Response.not_found_response("User not found")

        user.pop("password", None)  # optional: remove password if exists
        return Response.success_response(user, message="User details fetched successfully")

    except Exception as e:
        return Response.error_response(message=f"Error fetching user details: {str(e)}", status_code=500)



# @admin_bp.route('/teacher/<teacher_id>', methods=['GET'])
# @role_required([Role.ADMIN.value])
# def 