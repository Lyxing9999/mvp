from itertools import count
from flask import request  # type: ignore
from . import admin_bp
from app.auth.jwt_utils import role_required
from app.services.user_service import get_user_service
from app.enums.roles import Role
from app.utils.response_utils import Response  # type: ignore 
from app.schemas.user_schema import UserCreateSchema, UserResponseSchema, UserPatchSchema, UserPatchUserDetailSchema, UserDetailResponseSchema
from pydantic import ValidationError  # type: ignore 
from app.database.db import get_db
import logging
from flask import send_from_directory , g # type: ignore
from  functools import wraps
import os
logger = logging.getLogger(__name__)

def with_user_service(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        g.user_service = get_user_service()
        return func(*args, **kwargs)
    return wrapper


db = get_db()
@admin_bp.route('/', methods=['GET'])   
@with_user_service
@role_required([Role.ADMIN.value])
def get_all_users():
    """Fetch all users (Admin only).
    @return: List[UserResponseSchema]
    @throws: Exception
    """
    try:
        users = g.user_service.user_repo.find_all_users()

        if not users:
            return Response.success_response(data=[], message="No users found")

        user_data = [user.model_dump(exclude={"password"},by_alias=True) for user in users]
        return Response.success_response(user_data, message="Users fetched successfully")
 
    except Exception as e:
        return Response.error_response(message=f"Error fetching users: {str(e)}", status_code=500)

@admin_bp.route('/users', methods=['POST'])
@with_user_service
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

        # Now returns the created user directly
        user = g.user_service.create_user(validated_data.model_dump(by_alias=True))
        
        user_response = UserResponseSchema.model_validate(user)
        return Response.success_response(user_response.model_dump(by_alias=True), message="Successfully created user", status_code=201)
    
    except ValidationError as ve:
        return Response.error_response(message=ve.errors(), status_code=400)
    except Exception as e:
        logger.exception("Error creating user")
        return Response.error_response(message=f"Error creating user: {str(e)}", status_code=500)




@admin_bp.route('/users/<_id>', methods=['PATCH'])
@role_required([Role.ADMIN.value])
@with_user_service
def patch_user(_id):
    """Edit an existing user (Admin only).
    @param user_id: str
    @param user_update: UserPatchSchema
    @return: UserResponseSchema
    @throws: ValidationError
    @throws: Exception
    """
    try:
        data = request.get_json()
        if not data:
            return Response.error_response(message="Invalid JSON", status_code=400)
        try:
            user_update = UserPatchSchema.model_validate(data)
        except ValidationError as ve:
            return Response.error_response(message=f"Validation error: {ve}", status_code=422)        
        updated_user = g.user_service.patch_user(_id, user_update.model_dump(by_alias=True))
        if not updated_user:
            return Response.not_found_response("User not found or update failed")
        user_data = UserResponseSchema.model_validate(updated_user, by_alias=True, exclude_none=True, mode="json")
        return Response.success_response(
            user_data,
            message="User updated successfully"
        )

    except Exception as e:
        return Response.error_response(message=f"Error updating user: {str(e)}", status_code=500)

@admin_bp.route('/users/<_id>', methods=['DELETE'])
@role_required([Role.ADMIN.value])
@with_user_service
def delete_user(_id):
    """Delete a user by ID (Admin only).
    @param _id: str
    @return: boolean True if deleted successfully, False otherwise
    @throws: Exception
    """
    try:
        result = g.user_service.delete_user(_id)
        if not result:
            return Response.not_found_response("User not found or delete failed")

        return Response.success_response(message="User deleted successfully")

    except Exception as e:
        return Response.error_response(message=f"Error deleting user: {str(e)}", status_code=500)


@admin_bp.route('/users/find-one-user', methods=['POST'])
@role_required([Role.ADMIN.value])
@with_user_service
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
            user = g.user_service.user_repo.find_user_by_id(str(_id))
        elif 'username' in data:
            user = g.user_service.user_repo.find_user_by_username(data['username'])
        elif 'email' in data:
            user = g.user_service.user_repo.find_user_by_email(data['email'])
        else:
            return Response.error_response(message="Please provide 'id', 'username', or 'email'", status_code=400)

        if not user:
            return Response.not_found_response("User not found")
        user_data = UserDetailResponseSchema.model_validate(user, by_alias=True, exclude_none=True, mode="json")
        return Response.success_response(user_data, message="User fetched successfully")

    except Exception as e:
        return Response.error_response(message=f"Error fetching user: {str(e)}", status_code=500)


@admin_bp.route('/users/count-by-role', methods=['GET'])
@role_required([Role.ADMIN.value])
@with_user_service
def count_users_by_role():
    """Count users by role (Admin only).
    @throws: Exception
    """
    try:
        counts = g.user_service.user_repo.count_users_by_role()
        return Response.success_response(counts, message="User counts by role fetched successfully")

    except Exception as e:
        return Response.error_response(message=f"Error counting users by role: {str(e)}", status_code=500)






@admin_bp.route('/users/growth-stats', methods=['GET'])
@role_required([Role.ADMIN.value])
@with_user_service
def get_user_growth_stats():
    """Get user growth statistics (Admin only).
    @throws: Exception
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        if not start_date or not end_date:
            return Response.error_response(message="Missing start_date or end_date query parameters", status_code=400)

        stats = g.user_service.user_repo.find_user_growth_stats(start_date=start_date, end_date=end_date)
        return Response.success_response(stats, message="User growth statistics fetched successfully")

    except Exception as e:
        return Response.error_response(message=f"Error fetching user growth stats: {str(e)}", status_code=500)



@admin_bp.route('/users/growth-stats-by-role', methods=['GET'])
@role_required([Role.ADMIN.value])
@with_user_service
def get_user_growth_stats_by_role(): 
    """Get user growth statistics by role (Admin only).
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
            
        stats = g.user_service.user_repo.find_users_growth_stats_by_role_with_comparison(current_start_date=current_start_date, current_end_date=current_end_date, previous_start_date=previous_start_date, previous_end_date=previous_end_date)
        return Response.success_response(stats, message="User growth statistics fetched successfully")

    except Exception as e:
        return Response.error_response(message=f"Error fetching user growth stats: {str(e)}", status_code=500)





@admin_bp.route('/users/detail/<_id>', methods=['GET'])
@role_required([Role.ADMIN.value])
@with_user_service
def get_user_detail(_id):
    """Get detailed information about a user by ID (Admin only).
    @param user_id: str
    @return: UserResponseSchema
    @throws: Exception
    """
    try:

        if not _id:
            return Response.error_response(message="User ID is required", status_code=400)
        user = g.user_service.user_repo.find_user_detail(_id)
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
@with_user_service
def patch_user_detail(_id):
    """Edit user detail (Admin only).
    @param _id: str must provide id
    @param data: UserPatchUserDetailSchema
    @return: UserDetailResponseSchema
    @throws: ValidationError
    @throws: Exception
    """
    try:
        if not _id:
            return Response.error_response(message="User ID is required", status_code=400)
        data = request.get_json()
        if not data:
            return Response.error_response(message="Invalid JSON", status_code=400)
        try:
            user_update = UserPatchUserDetailSchema.model_validate(data)
        except ValidationError as ve:
            return Response.error_response(message=f"Validation error: {ve}", status_code=422)        
        updated_user = g.user_service.patch_user_detail(_id, user_update.model_dump(by_alias=True))

        if not updated_user:
            return Response.not_found_response("User not found or update failed")
        user_data = UserDetailResponseSchema.model_validate(updated_user, by_alias=True, exclude_none=True, mode="json")
        return Response.success_response(user_data, message="User detail updated successfully")
    except Exception as e:
        return Response.error_response(message=f"Error updating user detail: {str(e)}", status_code=500)


@admin_bp.route('/users/search-user', methods=['POST'])
@role_required([Role.ADMIN.value])
@with_user_service
def search_user():
    """Search for users by username or email (Admin only)."""
    try:
        data = request.get_json()
        if not data:
            return Response.error_response(message="Invalid JSON", status_code=400)

        query = data.get('query', '')
        page = data.get('page', 1)
        page_size = data.get('page_size', 10)

        users = g.user_service.user_repo.search_user(query, page, page_size)
        users_serialized = [
            user.model_dump(mode="json", by_alias=True, exclude_none=True) for user in users
        ]
        return Response.success_response(users_serialized, message="Users fetched successfully")

    except Exception as e:
        return Response.error_response(message=f"Error searching users: {str(e)}", status_code=500)








@admin_bp.route('/openapi.yaml', methods=['GET'])
def get_openapi_yaml():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'openapi.yaml')
