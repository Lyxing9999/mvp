from typing import Optional, List, Type, TypeVar, Union, Dict, Any, Set, AbstractSet
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from app.utils.convert import convert_objectid_to_str
from app.utils.objectid import ObjectId  # type: ignore
from pydantic import BaseModel, ValidationError  # type: ignore
import logging

from app.error.exceptions import (
    AppBaseException,
    ValidationError as AppValidationError,
    AppTypeError,
    InternalServerError,
    BadRequestError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class ConversionStrategy(Enum):
    SKIP_INVALID = "skip_invalid"
    RAISE_ON_INVALID = "raise_on_invalid"
    LOG_AND_SKIP = "log_and_skip"


@dataclass(frozen=True)
class ModelUtilsConfig:
    DEFAULT_PROTECTED_FIELDS = frozenset({"id", "_id", "role", "created_at", "updated_at"})
    protected_fields: AbstractSet[str] = DEFAULT_PROTECTED_FIELDS
    conversion_strategy: ConversionStrategy = ConversionStrategy.RAISE_ON_INVALID
    log_conversion_failures: bool = True



#* Abstract classes for model utils
class ModelConverter(ABC):
    @abstractmethod
    def convert(self, data: Dict[str, Any], model_class: Type[T]) -> Optional[T]:
        pass

class ModelInsertMany(ABC):
    @abstractmethod
    def insert_many(self, docs: List[Dict[str, Any]]) -> List[ObjectId]:
        pass

class ModelInsertOne(ABC):
    @abstractmethod
    def insert_one(self, doc: Dict[str, Any]) -> ObjectId:
        pass

class ModelUpdateOne(ABC):
    @abstractmethod
    def update_one(self, _id: ObjectId, update_data: Dict[str, Any]) -> Optional[T]:
        pass
    
class ModelUpdateMany(ABC):
    @abstractmethod
    def update_many(self, filter: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        pass
    
class ModelDeleteOne(ABC):
    @abstractmethod
    def delete_one(self, _id: ObjectId) -> bool:
        pass
#for future use after impletment MVP 
#* Abstract classes for model utils



class ModelConverterImp(ModelConverter):
    def __init__(self, config: ModelUtilsConfig):
        self.config = config

    def convert(self, data: Dict[str, Any], model_class: Type[T]) -> Optional[T]:
        logger.debug("Attempting conversion", extra={"data": data, "model_class": model_class.__name__})
        strategy = self.config.conversion_strategy
        try:
            model = model_class(**data)
            logger.debug("Conversion successful", extra={"model": model.dict()})
            return model
        except ValidationError as e:
            app_exc = AppValidationError(
                message=f"Pydantic validation failed for {model_class.__name__}",
                field_errors={str(err['loc'][0]): err['msg'] for err in e.errors()},
                cause=e,
                details={"raw_errors": e.errors(), "data": data}
            )
            if strategy == ConversionStrategy.RAISE_ON_INVALID:
                raise app_exc
            elif strategy == ConversionStrategy.LOG_AND_SKIP:
                logger.warning(str(app_exc), extra=app_exc.to_dict())
                return None
        except Exception as e:
            app_exc = InternalServerError(
                message=f"Unexpected error converting to {model_class.__name__}",
                cause=e,
                details={"data": data}
            )
            if strategy == ConversionStrategy.RAISE_ON_INVALID:
                raise app_exc
            elif strategy == ConversionStrategy.LOG_AND_SKIP:
                logger.error(str(app_exc), extra=app_exc.to_dict())
                return None
        return None



class ObjectIdValidator:
    def __init__(self, config: Optional[ModelUtilsConfig] = None):
        self.config = config or ModelUtilsConfig()

    @staticmethod
    def validate(id_val: Union[str, ObjectId, None]) -> ObjectId:
        if id_val is None:
            raise BadRequestError(
                message="ObjectId cannot be None",
                details={"received_value": None}
            )
        if isinstance(id_val, ObjectId):
            return id_val
            
        if not isinstance(id_val, str):
            raise BadRequestError(
                message="ObjectId must be a string",
                details={
                    "received_value": str(id_val),
                    "actual_type": type(id_val).__name__,
                    "expected_type": "str"
                }
            )
            
        try:
            return ObjectId(id_val)
        except Exception as e:
            raise BadRequestError(
                message="Invalid ObjectId format",
                cause=e,
                details={"input_value": id_val}
            )
        
    def convert_to_response_model(self, data: Dict[str, Any], model_class: Type[T]) -> Optional[T]:
        strategy = self.config.conversion_strategy
        try:
            data_str = convert_objectid_to_str(data)
            return model_class(**data_str)
        except ValidationError as e:
            app_exc = AppValidationError(
                message=f"Validation failed while converting to {model_class.__name__}",
                field_errors={str(err['loc'][0]): err['msg'] for err in e.errors()},
                cause=e,
                details={"raw_errors": e.errors(), "data": data},
            )
            if strategy == ConversionStrategy.RAISE_ON_INVALID:
                raise app_exc
            elif strategy == ConversionStrategy.LOG_AND_SKIP:
                logger.warning(str(app_exc), extra=app_exc.to_dict())
                return None
        except Exception as e:
            app_exc = InternalServerError(
                message=f"Unexpected error during conversion to {model_class.__name__}",
                cause=e,
                details={"data": data},
            )
            if strategy == ConversionStrategy.RAISE_ON_INVALID:
                raise app_exc
            elif strategy == ConversionStrategy.LOG_AND_SKIP:
                logger.error(str(app_exc), extra=app_exc.to_dict())
                return None
        return None

    def convert_to_response_model_list(self, data_list: List[Dict[str, Any]], model_class: Type[T]) -> List[T]:
        return [self.convert_to_response_model(data, model_class) for data in data_list]

    @staticmethod
    def try_convert(id_val: Union[str, ObjectId, None]) -> Optional[ObjectId]:
        try:
            return ObjectIdValidator.validate(id_val)
        except BadRequestError:
            return None

class ModelUtils:

    def __init__(self, config: Optional[ModelUtilsConfig] = None):
        self.config = config or ModelUtilsConfig()
        self._converter = ModelConverterImp(self.config)
        self._objectid_validator = ObjectIdValidator(self.config)
    
    
    def to_model(self, data: Dict[str, Any], model_class: Type[T]) -> Optional[T]:
        if not self._is_valid_input_dict(data):
            strategy = self.config.conversion_strategy
            if strategy == ConversionStrategy.RAISE_ON_INVALID:
                raise AppValidationError(
                    message=f"Invalid input data for {model_class.__name__}",
                    details={"received_value": data, "expected_type": "dict"}
                )
            elif strategy == ConversionStrategy.LOG_AND_SKIP:
                logger.warning(
                    f"Invalid input for {model_class.__name__} | received: {type(data).__name__}, expected: dict"
                )
                return None
            elif strategy == ConversionStrategy.SKIP_INVALID:
                return None
        return self._converter.convert(data, model_class)

    
    def to_model_list(
        self, 
        data_list: Optional[List[Dict[str, Any]]], 
        model_class: Type[T]
    ) -> List[T]:
        if not isinstance(data_list, list):
            msg = f"Invalid input data for {model_class.__name__}: Expected list, got {type(data_list).__name__}"
            if self.config.conversion_strategy == ConversionStrategy.SKIP_INVALID:
                return [] 
            if self.config.conversion_strategy == ConversionStrategy.RAISE_ON_INVALID:
                raise AppValidationError(message=msg, details={"received_value": data_list})
            if self.config.conversion_strategy == ConversionStrategy.LOG_AND_SKIP:
                logger.warning(msg)
                return []

        if not data_list:
            return []

        result: List[T] = []
        for data in data_list:
            model = self.to_model(data, model_class)
            if model is not None:
                result.append(model)
        return result

    
    def validate_object_id(self, id_val: Union[str, ObjectId, None]) -> ObjectId:
        return self._objectid_validator.validate(id_val)
    
    def try_convert_object_id(self, id_val: Union[str, ObjectId, None]) -> Optional[ObjectId]:
        return self._objectid_validator.try_convert(id_val)
        
    def prepare_safe_update(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(update_data, dict):
            msg = f"Expected dict, got {type(update_data).__name__}"
            if self.config.conversion_strategy == ConversionStrategy.RAISE_ON_INVALID:
                raise AppTypeError(
                    message=msg,
                    details={"received_value": update_data, "expected_type": "dict"}
                )
            elif self.config.conversion_strategy == ConversionStrategy.LOG_AND_SKIP:
                logger.warning(msg)
                return {}
            elif self.config.conversion_strategy == ConversionStrategy.SKIP_INVALID:
                return {}
        return {
            key: value for key, value in update_data.items()
            if key not in self.config.protected_fields
        }




    def _is_valid_input_dict(self, data: Optional[Dict[str, Any]]) -> bool:
        return isinstance(data, dict)

    def convert_to_response_model(self, data: Dict[str, Any], model_class: Type[T]) -> Optional[T]:
        return self._objectid_validator.convert_to_response_model(data, model_class)

    def convert_to_response_model_list(self, data_list: List[Dict[str, Any]], model_class: Type[T]) -> List[T]:
        return self._objectid_validator.convert_to_response_model_list(data_list, model_class)

# Factory function for common usage patterns
def create_model_utils(
    protected_fields: Optional[Set[str]] = None,
    strategy: ConversionStrategy = ConversionStrategy.RAISE_ON_INVALID
) -> ModelUtils:
    config = ModelUtilsConfig(
        protected_fields=protected_fields or ModelUtilsConfig.DEFAULT_PROTECTED_FIELDS,
        conversion_strategy=strategy
    )
    return ModelUtils(config)


# Default instance for backward compatibility
default_model_utils = create_model_utils()
