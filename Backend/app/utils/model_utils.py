from typing import Optional, List, Type, TypeVar, Union, Dict, Any # type: ignore
from app.utils.objectid import ObjectId # type: ignore
from pydantic import BaseModel # type: ignore
import logging
from app.utils.exceptions import BadRequestError # type: ignore
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def to_model(data: Optional[Dict[str, Any]], model_class: Type[T]) -> Optional[T]:
    if not isinstance(data, dict) or not data:
        return None
    try:
        return model_class(**data)
    except Exception as e:
        logger.warning(f"Failed to convert to {model_class.__name__}: {e}")
        return None


def to_model_list(data_list: List[Dict[str, Any]], model_class: Type[T]) -> List[T]:
    return [model for data in data_list if (model := to_model(data, model_class))]


def to_objectid(id_val: Union[str, ObjectId]) -> Optional[ObjectId]:
    if isinstance(id_val, ObjectId):
        return id_val
    try:
        return ObjectId(id_val)
    except Exception as e:
        logger.error(f"Invalid ObjectId: {e}")
        return None


def prepare_safe_update(update_data: dict) -> dict:
    safe_update = dict(update_data)
    safe_update.pop("id", None)
    safe_update.pop("_id", None)
    safe_update.pop("role", None)
    return safe_update  


def validate_object_id(_id: Union[str, ObjectId]) -> ObjectId:
    obj_id = to_objectid(_id)
    if not obj_id:
        raise BadRequestError(f"Invalid ObjectId (value: {_id}, type: {type(_id)})")
    return obj_id