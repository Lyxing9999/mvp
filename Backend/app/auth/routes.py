from flask import request, jsonify, url_for # type: ignore
from werkzeug.security import check_password_hash # type: ignore
from app.services.user_service import UserService
from app.auth.jwt_utils import create_access_token
from datetime import timedelta
from config import Config
from authlib.integrations.flask_client import OAuth  # type: ignore
from . import auth_bp
from app import oauth 



@auth_bp.route('/google/login/callback')
def google_login_callback():
    token = oauth.google.authorize_access_token()
    nonce = token.get('nonce')
    user_info = oauth.google.parse_id_token(token, nonce=nonce)
    email = user_info.get('email')
    if not email:
        return jsonify({"msg": "Google login failed, no email found"}), 400
    
    user = UserService.find_user_by_email(email)
    if not user:
  
        user_data = {
            'username': user_info.get('name', email.split('@')[0]),
            'email': email,
            'role': 'student',
            'password': "",
            'google_id': user_info.get('sub')
        }
        user = UserService.create_user(user_data)  
        if not user:
            return jsonify({"msg": "User registration failed"}), 500
    access_token = create_access_token(
        data={"role": user.role, "id": user.id},
        expire_delta=timedelta(hours=1)
    )
    return jsonify({"access_token": access_token}), 200
    
    
@auth_bp.route('/google/login')
def google_login():
    redirect_uri = url_for('auth.google_login_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/register', methods=['POST'])
def register():
    
    data = request.json
    if not data.get('username') or not data.get('password'):
        return jsonify({"msg": "username and password are required"}), 400
    if not data.get('role') or data.get('role') not in ['student', 'teacher', 'admin']:
        return jsonify({"msg": "Role must be one of: student, teacher, admin"}), 400
    if len(data.get('password')) < 6:
        return jsonify({"msg": "Password must be at least 6 characters long"}), 400
    if UserService.find_user_by_username(data.get('username')):
        return jsonify({"msg": "User already exists"}), 400
    
     
    user_service = UserService()
    user = user_service.create_user(data)
    print(user)
    if user:
        access_token = create_access_token(
            data={"role": user.role, "id": user.id},
            expire_delta=timedelta(hours=1)
        )
        print(access_token)
        return jsonify({"access_token": access_token}), 201
    return jsonify({"msg": "User registration failed"}), 500



@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data.get('username') or not data.get('password'):
        return jsonify({"msg": "username and password are required"}), 400
    user = UserService.find_user_by_username(data.get('username'))
    if not user or not check_password_hash(user.password, data.get('password')):
        return jsonify({"msg": "Invalid email or password"}), 401
    access_token = create_access_token(
        data={"role": user.role, "id": user.id},
            expire_delta=timedelta(hours=1)
    )
    return jsonify({"access_token": access_token}), 200




@auth_bp.route('/logout')
def logout():
    return "Logout Page"

