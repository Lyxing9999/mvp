from flask import request, jsonify, url_for  # type: ignore
from werkzeug.security import check_password_hash  # type: ignore
from datetime import timedelta

from . import auth_bp
from app import oauth
from app.services.user_service import UserService
from app.auth.jwt_utils import create_access_token
from app.utils.response_utils import Response  # type: ignore

# Unified JSON response helper
def response(msg, code=200, data=None): 
    body = {"msg": msg}
    if data is not None:
        body["data"] = data
    return jsonify(body), code


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

    user = UserService.find_user_by_email(email)

    if user:
        if user.role != "student":
            return Response.forbidden_response("Google login is only allowed for student accounts")
    else:
        user_data = {
            'username': user_info.get('name', email.split('@')[0]),
            'email': email,
            'role': 'student',
            'password': "",
            'google_id': user_info.get('sub')
        }
        result = UserService.create_user(user_data)
        if not result or not result.get("status"):
            return Response.error_response("User registration failed", status_code=500)
        user = result.get("user")

    access_token = create_access_token(
        data={"role": user.role, "id": str(user.id)},
        expire_delta=timedelta(hours=1)
    )

    return Response.success_response({"access_token": access_token}, message="Login successful")


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user and return JWT."""
    data = request.get_json()
    if not data:
        return Response.error_response("Invalid JSON body", status_code=400)

    result = UserService.create_user(data)
    if not result.get("status"):
         return Response.error_response(result.get("msg", "User registration failed"), status_code=400)

    user = result.get("user")
    access_token = create_access_token(
        data={"role": user.role, "id": str(user.id)},
        expire_delta=timedelta(hours=1)
    )

    return Response.success_response({"access_token": access_token}, message="User registered successfully", status_code=201)



@auth_bp.route('/login', methods=['POST'])
def login():
    try:

        """Login user and return JWT."""
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return Response.error_response("Username and password are required", status_code=400)

        user = UserService.find_user_by_username(username)
        if not user or not check_password_hash(user.password, password):
            return Response.unauthorized_response("Invalid username or password")
        
        access_token = create_access_token(
            data={"role": user.role, "id": str(user.id)},
            expire_delta=timedelta(hours=1)
        )

        return Response.success_response({
            "access_token": access_token,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": getattr(user, 'email', None),
                "role": user.role,
            }
        }, message="Login successful")
    except Exception as e:
        return Response.error_response(f"Error logging in: {str(e)}", status_code=500)


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user (no server state for JWT)."""
    return Response.success_response(message="Successfully logged out")
