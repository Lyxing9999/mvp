from flask import Flask # type: ignore
from config import Config
from app.extensions import init_extensions, mongo_client




def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_extensions(app)
    from .auth.routes import auth_bp
    # from .admin.routes import admin_bp
    from .teacher.routes import teacher_bp
    from .student.routes import student_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    # app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(student_bp, url_prefix='/student')

    
    
    return app