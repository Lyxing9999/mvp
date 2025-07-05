from flask import request  # type: ignore
from . import admin_bp
from app.auth.jwt_utils import role_required
from app.services.user_service import UserService
from app.enums.roles import Role
from app.utils.response_utils import Response  # type: ignore 
from app.schemas.user_schema import UserCreateSchema, UserResponseSchema, UserUpdateSchema
from pydantic import ValidationError  # type: ignore 
import logging
from flask import send_from_directory # type: ignore
import os
logger = logging.getLogger(__name__)


@admin_bp.route('/', methods=['GET'])   
@role_required([Role.ADMIN.value])
def get_all_users():
    """Fetch all users (Admin only).
    @return: List[UserResponseSchema]
    @throws: Exception
    """
    try:
        users = UserService.find_all_users()

        if not users:
            return Response.success_response(data=[], message="No users found")

        user_data = [user.model_dump(exclude={"password"},by_alias=True) for user in users]
        return Response.success_response(user_data, message="Users fetched successfully")
 
    except Exception as e:
        return Response.error_response(message=f"Error fetching users: {str(e)}", status_code=500)


@admin_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user (Admin only).
    @param data: UserCreateSchema
    @return: UserResponseSchema
    @throws: ValidationError
    @throws: Exception
    """
    try:
        data = request.get_json()
        if not data:
            return Response.error_response(message="Invalid JSON", status_code=400)

        validated_data = UserCreateSchema.model_validate(data)
        result = UserService.create_user(validated_data.model_dump())
        if not result.get("status"):
            return Response.error_response(message=result.get("msg", "Unknown error"), status_code=400)

        user = result.get("user")
        user_response = UserResponseSchema.model_validate(user)
        return Response.success_response(user_response.model_dump(), message="Successfully created user", status_code=201)
    except ValidationError as ve:
      
        return Response.error_response(message=ve.errors(), status_code=400)
    except Exception as e:
        return Response.error_response(message=f"Error creating user: {str(e)}", status_code=500)


@admin_bp.route('/users/<_id>', methods=['PATCH'])
@role_required([Role.ADMIN.value])
def edit_user(_id):
    """Edit an existing user (Admin only).
    @param user_id: str
    @param user_update: UserUpdateSchema
    @return: UserResponseSchema
    @throws: ValidationError
    @throws: Exception
    """
    try:
        user_update = request.get_json()
        if not user_update:
            return Response.error_response(message="Invalid JSON", status_code=400)

     
        if not _id:
            return Response.error_response(message="User ID is required", status_code=400)

        updated_user = UserService.edit_user(_id, user_update)
        if not updated_user:
            return Response.not_found_response("User not found or update failed")

        return Response.success_response(updated_user.model_dump(mode="json", by_alias=True), message="User updated successfully")

    except Exception as e:
        return Response.error_response(message=f"Error updating user: {str(e)}", status_code=500)


@admin_bp.route('/users/<_id>', methods=['DELETE'])
@role_required([Role.ADMIN.value])
def delete_user(_id):
    """Delete a user by ID (Admin only).
    @param _id: str
    @return: UserResponseSchema
    @throws: Exception
    """
    try:
        result = UserService.delete_user(_id)
        if not result:
            return Response.not_found_response("User not found or delete failed")

        return Response.success_response(message="User deleted successfully")

    except Exception as e:
        return Response.error_response(message=f"Error deleting user: {str(e)}", status_code=500)


@admin_bp.route('/users/find-one-user', methods=['POST'])
@role_required([Role.ADMIN.value])
def find_one_user():
    """Find a user by ID, username, or email (Admin only).
    @param data: UserSearchSchema
    @return: UserResponseSchema
    @throws: ValidationError
    @throws: Exception
    """
    try:
        data = request.get_json()
        if not data:
            return Response.error_response(message="Invalid JSON", status_code=400)

        user = None
        _id = data.get('id') or data.get('_id')
        if _id:
            user = UserService.find_user_by_id(str(_id))
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
    """Count users by role (Admin only).
    @return: List[UserResponseSchema]
    @throws: Exception
    """
    try:
        counts = UserService.count_users_by_role()
        return Response.success_response(counts, message="User counts by role fetched successfully")

    except Exception as e:
        return Response.error_response(message=f"Error counting users by role: {str(e)}", status_code=500)






@admin_bp.route('/users/growth-stats', methods=['GET'])
@role_required([Role.ADMIN.value])
def get_user_growth_stats():
    """Get user growth statistics (Admin only).
    @return: List[UserResponseSchema]
    @throws: Exception
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
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
    """Get user growth statistics by role (Admin only).
    @return: List[UserResponseSchema]
    @throws: Exception
    """
    try:
        current_start_date = request.args.get('current_start_date')
        current_end_date = request.args.get('current_end_date')
        previous_start_date = request.args.get('previous_start_date')
        previous_end_date = request.args.get('previous_end_date')
        if not current_start_date or not current_end_date:
            return Response.error_response(message="Missing current_start_date or current_end_date query parameters", status_code=400)
        if not previous_start_date or not previous_end_date:
            return Response.error_response(message="Missing previous_start_date or previous_end_date query parameters", status_code=400)
        
            
        stats = UserService.find_users_growth_stats_by_role_with_comparison(current_start_date=current_start_date, current_end_date=current_end_date,  previous_start_date=previous_start_date, previous_end_date=previous_end_date)
        print(f"User growth stats by role from {current_start_date} to {current_end_date} and {previous_start_date} to {previous_end_date}: {stats}")
        return Response.success_response(stats, message="User growth statistics fetched successfully")

    except Exception as e:
        return Response.error_response(message=f"Error fetching user growth stats: {str(e)}", status_code=500)






@admin_bp.route('/users/detail/<_id>', methods=['GET'])
@role_required([Role.ADMIN.value])
def get_user_detail(_id):
    """Get detailed information about a user by ID (Admin only).
    @param user_id: str
    @return: UserResponseSchema
    @throws: Exception
    """
    try:

        if not _id:
            return Response.error_response(message="User ID is required", status_code=400)
        user = UserService.find_users_detail(_id)
        if not user:
            return Response.not_found_response("User not found")

        user.pop("password", None)  
        return Response.success_response(user, message="User details fetched successfully", status_code=200)

    except Exception as e:
        logger.exception(f"Error fetching user details for ID {_id}")  
        return Response.error_response(message=f"Error fetching user details: {str(e)}", status_code=500)


# @admin_bp.route('/teacher/<teacher_id>', methods=['GET'])
# @role_required([Role.ADMIN.value])
# def 

@admin_bp.route('/users/edit-user-detail/<_id>', methods=['PATCH'])
@role_required([Role.ADMIN.value])
def edit_user_detail(_id):
    """Edit user detail (Admin only).
    @param user_id: str
    @param data: UserUpdateSchema
    @return: UserResponseSchema
    @throws: ValidationError
    @throws: Exception
    """
    try:
        data = request.get_json()
        if not data:
            return Response.error_response(message="Invalid JSON", status_code=400)
        
        
        if not _id:
            return Response.error_response(message="User ID is required", status_code=400)
        
        updated_user = UserService.patch_user_detail(_id, data)
        if not updated_user:
            return Response.not_found_response("User not found or update failed")
        return Response.success_response(updated_user, message="User detail updated successfully")
    except Exception as e:
        return Response.error_response(message=f"Error updating user detail: {str(e)}", status_code=500)

@admin_bp.route('/users/search-user', methods=['POST'])
@role_required([Role.ADMIN.value])
def search_user():
    """Search for users by username or email (Admin only)."""
    try:
        data = request.get_json()
        if not data:
            return Response.error_response(message="Invalid JSON", status_code=400)

        query = data.get('query', '')
        page = data.get('page', 1)
        page_size = data.get('page_size', 10)

        users = UserService.search_user(query, page, page_size)
        users_serialized = [
            user.model_dump(mode="json", by_alias=True, exclude_none=True) for user in users
        ]
        return Response.success_response(users_serialized, message="Users fetched successfully")

    except Exception as e:
        return Response.error_response(message=f"Error searching users: {str(e)}", status_code=500)















@admin_bp.route('/openapi.yaml', methods=['GET'])
def get_openapi_yaml():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'openapi.yaml')
