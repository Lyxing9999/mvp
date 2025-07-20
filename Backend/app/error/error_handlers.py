from flask import jsonify
from werkzeug.exceptions import HTTPException
from app.utils.convert import convert_objectid_to_str
from app.error.exceptions import (
    AppBaseException,
    UnauthorizedError,
    ValidationError as CustomValidationError,
    ForbiddenError,
    NotFoundError,
    BadRequestError,
    InternalServerError,
    AuthenticationError,
    DatabaseError,
)


def register_error_handlers(app):

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        return jsonify({
            "error_code": "HTTP_ERROR",
            "message": error.description,
            "severity": "medium",
            "category": "system",
            "recoverable": False
        }), error.code or 500

    @app.errorhandler(CustomValidationError)
    def handle_custom_validation(error: CustomValidationError):
        return jsonify({
            "error_code": "VALIDATION_ERROR",
            "message": "Validation failed",
            "details": error.to_dict() if hasattr(error, "to_dict") else str(error),
            "severity": "low",
            "category": "validation",
            "recoverable": True
        }), error.status_code or 400

    @app.errorhandler(NotFoundError)
    def handle_not_found(error: NotFoundError):
        return jsonify({
            "error_code": "NOT_FOUND",
            "message": error.message,
            "details": convert_objectid_to_str(error.details or {}),
            "severity": "medium",
            "category": "client",
            "recoverable": False
        }), error.status_code or 404

    @app.errorhandler(DatabaseError)
    def handle_database_error(error: DatabaseError):
        return jsonify({
            "error_code": "DATABASE_ERROR",
            "message": error.message,
            "details": convert_objectid_to_str(error.details or {}),
            "severity": "high",
            "category": "system",
            "recoverable": False
        }), error.status_code or 500

    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(error: AuthenticationError):
        return jsonify({
            "error_code": "AUTHENTICATION_ERROR",
            "message": error.message,
            "details": convert_objectid_to_str(error.details or {}),
            "severity": "medium",
            "category": "auth",
            "recoverable": False
        }), error.status_code or 401

    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized(error: UnauthorizedError):
        return jsonify({
            "error_code": "UNAUTHORIZED",
            "message": error.message,
            "details": convert_objectid_to_str(error.details or {}),
            "severity": "medium",
            "category": "auth",
            "recoverable": False
        }), error.status_code or 401

    @app.errorhandler(ForbiddenError)
    def handle_forbidden(error: ForbiddenError):
        return jsonify({
            "error_code": "FORBIDDEN",
            "message": error.message,
            "details": convert_objectid_to_str(error.details or {}),
            "severity": "medium",
            "category": "auth",
            "recoverable": False
        }), error.status_code or 403

    @app.errorhandler(AppBaseException)
    def handle_app_base_exception(error: AppBaseException):
        return jsonify({
            "error_code": error.code or "APP_ERROR",
            "message": error.message,
            "details": convert_objectid_to_str(error.details or {}),
            "severity": error.severity or "medium",
            "category": error.category or "application",
            "recoverable": error.recoverable if hasattr(error, "recoverable") else False
        }), error.status_code or 400

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error: Exception):
        return jsonify({
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
            "details": {"exception": str(error)},
            "severity": "critical",
            "category": "system",
            "recoverable": False
        }), 500