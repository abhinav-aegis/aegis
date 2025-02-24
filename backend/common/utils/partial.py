from copy import deepcopy
from typing import Any, Callable, Optional, Type, TypeVar
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

ModelType = TypeVar("ModelType", bound=BaseModel)  # ✅ Fix TypeVar binding

def optional(without_fields: list[str] | None = None) -> Callable[[Type[ModelType]], Type[ModelType]]:
    """
    A decorator that creates a partial model.

    Args:
        without_fields (list[str] | None): Fields to exclude from the model.

    Returns:
        Callable[[Type[BaseModel]], Type[BaseModel]]: A modified model class.
    """
    if without_fields is None:
        without_fields = []

    def wrapper(model: Type[ModelType]) -> Type[ModelType]:
        base_model: Type[BaseModel] = model  # ✅ Use BaseModel as the base

        def make_field_optional(field: Any, default: Any = None) -> tuple[Any, FieldInfo]:
            new = deepcopy(field)
            new.default = default
            new.annotation = Optional[field]  # ✅ Fix annotation
            return new.annotation, new

        if without_fields:
            base_model = BaseModel

        return create_model( # type: ignore
            model.__name__,
            __base__=base_model,
            __module__=model.__module__,
            **{
                field_name: make_field_optional(field_info)
                for field_name, field_info in model.__annotations__.items()  # ✅ Fix model_fields access
                if field_name not in without_fields
            },
        )

    return wrapper
