from typing import Optional, List, Type, TypeVar, Union, Dict, Any
from app.utils.objectid import ObjectId  # type: ignore
from pydantic import BaseModel  # type: ignore
import logging
from app.utils.exceptions import BadRequestError

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

def to_model(data: Optional[Dict[str, Any]], model_class: Type[T]) -> Optional[T]:
    """
    Converts a dictionary to an instance of a Pydantic model.
    Returns None if input is not a valid dict or conversion fails.
    """
    if not isinstance(data, dict) or not data:
        return None
    try:
        return model_class(**data)
    except Exception as e:
        logger.warning(f"Failed to convert to {model_class.__name__}: {e}")
        return None

def _to_model_list(data_list: List[Dict[str, Any]], model_class: Type[T]) -> List[T]:
    """
    Internal helper to convert a list of dicts into a list of Pydantic models,
    skipping any dicts that fail validation/conversion.
    """
    return [model for data in data_list if (model := to_model(data, model_class))]

def to_model_list(data_list: List[Dict[str, Any]], model_class: Type[T]) -> List[T]:
    """
    Public function to convert a list of dicts into a list of Pydantic models.
    Validates input type and uses internal helper for conversion.
    """
    if not isinstance(data_list, list):
        logger.error(f"to_model_list expected a list but got {type(data_list)}")
        return []
    return _to_model_list(data_list, model_class)

def to_objectid(id_val: Union[str, ObjectId]) -> Optional[ObjectId]:
    """
    Attempts to convert input to ObjectId.
    Returns None if invalid.
    """
    if isinstance(id_val, ObjectId):
        return id_val
    try:
        return ObjectId(id_val)
    except Exception as e:
        logger.error(f"Invalid ObjectId: {e}")
        return None

def prepare_safe_update(update_data: dict) -> dict:
    """
    Returns a copy of update_data with protected keys removed,
    to prevent accidental overwriting of critical fields.
    """
    safe_update = dict(update_data)
    for key in ("id", "_id", "role"):
        safe_update.pop(key, None)
    return safe_update

def validate_object_id(_id: Union[str, ObjectId]) -> ObjectId:
    """
    Converts input to a valid ObjectId or raises BadRequestError if invalid.
    """
    obj_id = to_objectid(_id)
    if not obj_id:
        raise BadRequestError(f"Invalid ObjectId (value: {_id}, type: {type(_id)})")
    return obj_id
