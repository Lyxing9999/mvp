# app/utils/exceptions.py

class AppBaseException(Exception):
    """Base exception for custom app-level errors."""
    pass

class NotFoundError(AppBaseException):
    pass

class ValidationError(AppBaseException):
    pass

class DatabaseError(AppBaseException):
    pass

class AuthenticationError(AppBaseException):
    pass

class BadRequestError(AppBaseException):
    pass

class InternalServerError(AppBaseException):
    pass

class UnauthorizedError(AppBaseException):
    pass

class ForbiddenError(AppBaseException):
    pass