from typing import Generic, Optional, TypeVar, List
from pydantic import BaseModel as PydanticBaseModel, ConfigDict

from app.conf.config import settings

DataType = TypeVar("DataType")


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)


class IResponseBase(PydanticBaseModel, Generic[DataType]):
    message: Optional[str] = None
    data: DataType

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class IPaginationDataBase(PydanticBaseModel, Generic[DataType]):
    count: int
    limit: int
    page: int
    rows: List[DataType]

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class CommonsModel(PydanticBaseModel):
    limit: Optional[int] = settings.PAGINATION_MAX_SIZE
    offset: Optional[int] = 0
    page: Optional[int] = 1


class VisibleBase(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
