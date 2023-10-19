from typing import Optional
from datetime import datetime, date

from pydantic import Field, EmailStr

from app.core.schema import BaseModel, VisibleBase


class UserBase(BaseModel):
    name: str = Field(max_length=254)
    first_name: Optional[str] = Field(default="", max_length=254)
    medium_name: Optional[str] = Field(default="", max_length=254)
    last_name: Optional[str] = Field(default="", max_length=254)

    date_of_birth: Optional[date] = None
    date_of_join: Optional[date] = None
    date_of_left: Optional[date] = None

    business_email: Optional[EmailStr] = None
    personal_email: Optional[EmailStr] = None

    is_active: bool = Field(alias='is_active')


class UserCreate(UserBase):
    name: str = Field(..., max_length=254)
    is_active: bool = Field(True, alias='is_active')


class UserVisible(VisibleBase):
    name: str
    created_at: datetime
    modified_at: Optional[datetime] = None

    first_name: Optional[str] = None
    medium_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_join: Optional[date] = None
    date_of_left: Optional[date] = None
    business_email: Optional[EmailStr] = None
    personal_email: Optional[EmailStr] = None
    is_active: bool


class GroupBase(BaseModel):
    name: str = Field(max_length=254)


class GroupCreate(GroupBase):
    name: str = Field(..., max_length=254)


class GroupVisible(VisibleBase):
    name: str

    created_at: datetime
    modified_at: Optional[datetime] = None


class UserToGroupCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    group_id: int = Field(..., gt=0)


class UserToGroupVisible(VisibleBase):
    user_id: int
    group_id: int
