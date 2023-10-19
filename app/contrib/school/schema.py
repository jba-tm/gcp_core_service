from datetime import datetime
from typing import Optional, Annotated
from decimal import Decimal
from pydantic import Field

from app.core.schema import BaseModel, VisibleBase


class SchoolBase(BaseModel):
    name: str = Field(max_length=254)
    address_line_1: Optional[str] = Field(None, max_length=254)
    address_line_2: Optional[str] = Field(None, max_length=254)
    pin_code: Optional[int] = Field(None, gt=0)
    web_site: Optional[str] = Field(None, max_length=100)
    latitude: Annotated[Decimal, Field(decimal_places=18, max_digits=18, gt=0)] | None
    longitude: Annotated[Decimal, Field(decimal_places=18, max_digits=18, gt=0)] | None
    is_active: bool = Field(alias='is_active')


class SchoolCreate(SchoolBase):
    name: str = Field(..., max_length=254)
    is_active: bool = Field(True, alias='is_active')


class SchoolVisible(VisibleBase):
    id: int

    name: str
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    pin_code: Optional[int] = None
    web_site: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    created_at: datetime
    modified_at: Optional[datetime] = None
    is_active: bool


class UserToSchoolBase(BaseModel):
    is_active: bool = Field(alias='is_active')


class UserToSchoolCreate(UserToSchoolBase):
    user_id: int = Field(gt=0)
    school_id: int = Field(gt=0)
    is_active: bool = Field(True, alias='is_active')


class UserToSchoolVisible(VisibleBase):
    id: int

    user_id: int
    school_id: int
    is_active: bool
