from fastapi.encoders import jsonable_encoder
from typing import TypeVar, List
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)


def print_model(text: str = "", model: List[ModelType] = []):
    """
    It prints sqlmodel responses for complex relationship models.
    """
    return print(text, jsonable_encoder(model))
