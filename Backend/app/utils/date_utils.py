from datetime import datetime # type: ignore
from typing import Any # type: ignore
import logging # type: ignore
from app.utils.exceptions import BadRequestError # type: ignore
from app.utils.objectid import ObjectId  # type: ignore

logger = logging.getLogger(__name__)

def ensure_date(value: Any) -> Any:
    """Ensure date is in correct format.

    - Converts ISO8601 strings to datetime
    - Converts datetime to ISO8601 string
    - Converts ObjectId to string
    Raises BadRequestError if invalid.
    """
    try:
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                raise BadRequestError(f"Invalid date format: {value}")
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, ObjectId):
            return str(value)
        raise BadRequestError(f"Invalid date format: {value}")
    except Exception as e:
        logger.error(f"Error ensuring date: {e}")
        raise