
from flask import jsonify # type: ignore

class Response:
    @staticmethod
    def success_response(data=None, message="Success", status_code=200):

        response = {
            "success": True,
            "message": message,
            "data": data
        }
        return jsonify(response), status_code
    @staticmethod
    def error_response(message="An error occurred", status_code=400, errors=None):
        response = {
            "success": False,
            "message": message,
            "errors": errors
        }
        return jsonify(response), status_code

    @staticmethod
    def not_found_response(message="Resource not found"):
        return Response.error_response(message=message, status_code=404)

    @staticmethod
    def unauthorized_response(message="Unauthorized"):
        return Response.error_response(message=message, status_code=401)

    @staticmethod
    def forbidden_response(message="Forbidden"):
        return Response.error_response(message=message, status_code=403)
