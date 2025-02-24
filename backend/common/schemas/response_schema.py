from math import ceil
from typing import Any, Generic, TypeVar, Dict
from collections.abc import Sequence
from fastapi_pagination import Params, Page
from fastapi_pagination.bases import AbstractPage, AbstractParams
from pydantic import Field
from pydantic import BaseModel

DataType = TypeVar("DataType")
T = TypeVar("T")


class PageBase(Page[T], Generic[T]):
    previous_page: int | None = Field(
        default=None, description="Page number of the previous page"
    )
    next_page: int | None = Field(
        default=None, description="Page number of the next page"
    )


class IResponseBase(BaseModel, Generic[T]):
    message: str = ""
    meta: dict | Any | None = {}
    data: T | None = None


class IGetResponsePaginated(AbstractPage[T], Generic[T]):
    message: str | None = ""
    meta: dict = {}
    data: PageBase[T]

    __params_type__ = Params  # Set params related to Page

    @classmethod
    def create( # type: ignore
        cls,
        items: Sequence[T],
        total: int,
        params: AbstractParams,
    ) -> "IGetResponsePaginated" | None:
        if hasattr(params, "size") and  params.size is not None and total is not None and params.size != 0:
            pages = ceil(total / params.size)
        else:
            pages = 0

        return cls(
            data=PageBase[T](
                items=items,
                page=params.page if hasattr(params, "page") else 1,
                size=params.size if hasattr(params, "size") else 0,
                total=total,
                pages=pages,
                next_page=params.page + 1 if hasattr(params, "page") and params.page < pages else None,
                previous_page=params.page - 1 if hasattr(params, "page") and params.page > 1 else None,
            )
        )


class IGetResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str = "Data got correctly"


class IPostResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str = "Data created correctly"


class IPutResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str = "Data updated correctly"


class IDeleteResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str = "Data deleted correctly"


def create_response(
    data: DataType,
    message: str | None = None,
    meta: Dict[Any, Any] = {},
) -> (
    IResponseBase[DataType]
    | IGetResponsePaginated[DataType]
    | IGetResponseBase[DataType]
    | IPutResponseBase[DataType]
    | IDeleteResponseBase[DataType]
    | IPostResponseBase[DataType]
    | Dict[str, Any]
):
    if isinstance(data, IGetResponsePaginated):
        data.message = "Data paginated correctly" if message is None else message
        data.meta = meta
        return data
    if message is None:
        return {"data": data, "meta": meta}
    return {"data": data, "message": message, "meta": meta}
