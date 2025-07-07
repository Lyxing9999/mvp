from flask import request, url_for  # type: ignore
from werkzeug.security import check_password_hash  # type: ignore
from datetime import timedelta
from app.enums.roles import Role 
from . import auth_bp
from app import oauth
from app.services.user_service import MongoUserService
from app.auth.jwt_utils import create_access_token
from app.repositories.user_repository import UserRepositoryImpl
from app.utils.response_utils import Response  # type: ignore
from app.database.db import get_db
import logging
logger = logging.getLogger(__name__)
db = get_db()


def build_jwt_payload(user: dict) -> dict:
    return {
        "id": str(user.get("id") or user.get("_id")),
        "role": user.get("role"),
        "username": user.get("username"),
        "email": user.get("email"),
    }

@auth_bp.route('/google/login')
def google_login():
    """Redirect to Google OAuth."""
    redirect_uri = url_for('auth.google_login_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/google/login/callback')
def google_login_callback():
    """Handle Google login callback."""
    token = oauth.google.authorize_access_token()
    nonce = token.get('nonce')
    user_info = oauth.google.parse_id_token(token, nonce=nonce)
    email = user_info.get('email')

    if not email:
        return Response.error_response("Google login failed, no email found", status_code=400)

    user_service = MongoUserService(db, UserRepositoryImpl(db))
    user = user_service.user_repo.find_user_by_email(email)

    if user:
        if user.role != Role.STUDENT.value:
            return Response.forbidden_response("Google login is only allowed for student accounts")
    else:
        user_data = {
            'username': user_info.get('name', email.split('@')[0]),
            'email': email,
            'role': Role.STUDENT.value,
            'password': "",
            'google_id': user_info.get('sub')
        }
        result = user_service.create_user(user_data)
        if not result:
            return Response.error_response("User registration failed", status_code=500)
        user = result.get("user")
        if not user:
            return Response.error_response("User registration failed", status_code=500)

    access_token = create_access_token(
        data=build_jwt_payload(user),
        expire_delta=timedelta(hours=1)
    )

    return Response.success_response({"access_token": access_token}, message="Login successful")


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user and return JWT."""
    data = request.get_json()
    if not data:
        return Response.error_response("Invalid JSON body", status_code=400)

    user_service = MongoUserService(db, UserRepositoryImpl(db))
    result = user_service.create_user(data)
    if not result:
        return Response.error_response("User registration failed", status_code=400)
    user = result.get("user")
    access_token = create_access_token(
        data=build_jwt_payload(user),
        expire_delta=timedelta(hours=1)
    )

    return Response.success_response({"access_token": access_token}, message="User registered successfully", status_code=201)



@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return Response.error_response("Username and password are required", status_code=400)

        user_service = MongoUserService(db, UserRepositoryImpl(db))
        user = user_service.user_repo.find_user_by_username(username)
        if not user:
            return Response.unauthorized_response("Invalid username or password")

        if not user.password:
            logger.warning(f"User {username} has no password set")
            return Response.unauthorized_response("Invalid username or password")

        if not check_password_hash(user.password, password):
            return Response.unauthorized_response("Invalid username or password")

        user_dict = user.model_dump(by_alias=True)

        access_token = create_access_token(
            data=build_jwt_payload(user_dict),
            expire_delta=timedelta(hours=1)
        )

        return Response.success_response({
            "access_token": access_token,
            "user": build_jwt_payload(user_dict)
        }, message="Login successful")

    except Exception as e:
        return Response.error_response(f"Error logging in: {str(e)}", status_code=500)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user (no server state for JWT)."""
    return Response.success_response(message="Successfully logged out")
