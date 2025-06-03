from flask import request, jsonify, url_for  # type: ignore
from werkzeug.security import check_password_hash  # type: ignore
from datetime import timedelta

from . import auth_bp
from app import oauth
from app.services.user_service import UserService
from app.auth.jwt_utils import create_access_token


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
        return response("Google login failed, no email found", 400)

    user = UserService.find_user_by_email(email)

    if user:
        if user.role != "student":
            return response("Google login is only allowed for student accounts", 403)
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
            return response("User registration failed", 500)
        user = result.get("user")

    access_token = create_access_token(
        data={"role": user.role, "id": str(user.id)},
        expire_delta=timedelta(hours=1)
    )

    return jsonify({"access_token": access_token}), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user and return JWT."""
    data = request.get_json()
    if not data:
        return response("Invalid JSON body", 400)

    result = UserService.create_user(data)
    if not result.get("status"):
        return response(result.get("msg", "User registration failed"), 400)

    user = result.get("user")
    access_token = create_access_token(
        data={"role": user.role, "id": str(user.id)},
        expire_delta=timedelta(hours=1)
    )

    return jsonify({"access_token": access_token}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return response("Username and password are required", 400)

    user = UserService.find_user_by_username(username)
    if not user or not check_password_hash(user.password, password):
        return response("Invalid username or password", 401)

    access_token = create_access_token(
        data={"role": user.role, "id": str(user.id)},
        expire_delta=timedelta(hours=1)
    )

    return jsonify({
        "access_token": access_token,
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": getattr(user, 'email', None),
            "role": user.role,
        }
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user (no server state for JWT)."""
    return response("Successfully logged out")
