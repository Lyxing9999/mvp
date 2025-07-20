from flask import jsonify
from enum import Enum
from typing import Optional, Union, Dict, Any
from flask.wrappers import Response as FlaskResponse






class Response:
    @staticmethod
    def success_response(
        data: Optional[Any] = None,
        message: str = "",
        status_code: int = 200,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FlaskResponse:
        """
        Return a successful JSON response.
        :param data: Payload data (any JSON-serializable)
        :param message: Optional message string
        :param status_code: HTTP status code (default 200)
        :param metadata: Optional additional metadata (e.g., pagination)
        :return: Flask JSON Response
        """
        response = {
            "success": True,
            "message": message,
            "data": data,
        }
        if metadata:
            response["metadata"] = metadata
        resp = jsonify(response)
        resp.status_code = status_code
        return resp

    @staticmethod
    def error_response(
        message: str = "An error occurred",
        status_code: int = 400,
        errors: Optional[Union[str, Dict[str, Any]]] = None
    ) -> FlaskResponse:
        """
        Return a generic error JSON response.
        :param message: Error message string
        :param status_code: HTTP status code (default 400)
        :param errors: Optional detailed error info (string or dict)
        :return: Flask JSON Response
        """
        response = {
            "success": False,
            "message": message,
        }
        if errors:
            response["errors"] = errors
        resp = jsonify(response)
        resp.status_code = status_code
        return resp

    @staticmethod
    def validation_error_response(
        errors: Union[str, Dict[str, Any]],
        message: str = "Validation error"
    ) -> FlaskResponse:
        """
        Return a validation error JSON response (HTTP 422).
        :param errors: Detailed validation errors
        :param message: Optional message (default "Validation error")
        :return: Flask JSON Response
        """
        return Response.error_response(message=message, status_code=422, errors=errors)

    @staticmethod
    def not_found_response(
        message: str = "Resource not found"
    ) -> FlaskResponse:
        """
        Return a 404 Not Found JSON response.
        """
        return Response.error_response(message=message, status_code=404)

    @staticmethod
    def unauthorized_response(
        message: str = "Unauthorized"
    ) -> FlaskResponse:
        """
        Return a 401 Unauthorized JSON response.
        """
        return Response.error_response(message=message, status_code=401)

    @staticmethod
    def forbidden_response(
        message: str = "Forbidden"
    ) -> FlaskResponse:
        """
        Return a 403 Forbidden JSON response.
        """
        return Response.error_response(message=message, status_code=403)
