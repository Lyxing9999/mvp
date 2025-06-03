from bson import ObjectId
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from typing import Any

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.union_schema([
                core_schema.str_schema(),
                core_schema.is_instance_schema(ObjectId),
            ])
        )

    @classmethod
    def validate(cls, v: Any) -> "PyObjectId":
        
        if isinstance(v, cls):
            return v
        if isinstance(v, ObjectId):
            return cls(str(v))
        if isinstance(v, str) and ObjectId.is_valid(v):
            return cls(v)
        raise ValueError("Invalid ObjectId")

