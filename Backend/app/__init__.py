from flask import Flask # type: ignore
from config import Config
from app.extensions import init_extensions, mongo_client
from authlib.integrations.flask_client import OAuth # type: ignore

oauth = OAuth()
oauth.register(
    name='google',
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)
def create_app():
    
    app = Flask(__name__)
    app.config.from_object(Config)
    init_extensions(app)
    oauth.init_app(app)
    from .auth.routes import auth_bp
    # from .admin.routes import admin_bp
    from .routes.teacher.routes import teacher_bp
    from .routes.student.routes import student_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    # app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(student_bp, url_prefix='/student')

    
    
    return app