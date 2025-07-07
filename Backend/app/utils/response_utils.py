from flask import jsonify  # type: ignore
from typing import Any, Dict, Optional, Union


class Response:
    @staticmethod
    def success_response(
        data: Optional[Union[Dict, list]] = None,
        message: str = "Success",
        status_code: int = 200,
        meta: Optional[Dict[str, Any]] = None,
    ):
        """
        Returns a standardized success response.
        """
        response = {
            "success": True,
            "message": message,
            "data": data if data is not None else {},
        }
        if meta:
            response["meta"] = meta  

        return jsonify(response), status_code

    @staticmethod
    def error_response(
        message: str = "An error occurred",
        status_code: int = 400,
        errors: Optional[Union[Dict, str]] = None,
    ):
        """
        Returns a standardized error response.
        """
        response = {
            "success": False,
            "message": message,
        }
        if errors:
            response["errors"] = errors

        return jsonify(response), status_code

    @staticmethod
    def not_found_response(message: str = "Resource not found"):
        return Response.error_response(message=message, status_code=404)

    @staticmethod
    def unauthorized_response(message: str = "Unauthorized"):
        return Response.error_response(message=message, status_code=401)

    @staticmethod
    def forbidden_response(message: str = "Forbidden"):
        return Response.error_response(message=message, status_code=403)

    @staticmethod
    def validation_error_response(errors: Union[Dict[str, Any], str], message: str = "Validation failed"):
        """
        Use when returning schema/field validation errors.
        """
        return Response.error_response(message=message, status_code=422, errors=errors)