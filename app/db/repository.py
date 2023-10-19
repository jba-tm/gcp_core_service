from typing import (
    Generic, Optional, Type, TypeVar, Union, Any, TYPE_CHECKING, Iterable,
    Dict
)
from uuid import UUID
from sqlalchemy import func, select, text, delete
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from app.core.enums import Choices

from .models import Base

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound=Base)
BaseSchemaType = TypeVar("BaseSchemaType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBaseSync(Generic[ModelType]):
    __slots__ = ('model', 'primary_field')

    def __init__(self, model: Type[ModelType], primary_field: Optional[str] = 'id'):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**


        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model
        self.primary_field = primary_field

    def first(
            self,
            db: "Session",
            params: Optional[dict] = None,
            options: Optional[Iterable] = None,
            order_by: Optional[Iterable] = None,
            expressions: Optional[Iterable] = None,
    ) -> Optional[ModelType]:
        """
        Soft retrieve obj
        :param db:
        :param params:
        :param options:
        :param order_by:
        :param expressions:
        :return:
        """

        stmt = select(self.model)
        if options:
            stmt = stmt.options(*options)
        if expressions:
            stmt = stmt.filter(*expressions)
        if params:
            stmt = stmt.filter_by(**params)
        if order_by:
            stmt = stmt.order_by(*order_by)
        return db.execute(stmt).scalars().first()

    def create(self, db: "Session", obj_in: dict) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in, custom_encoder={Choices: lambda x: x.value})
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def count(
            self, db: "Session", *,
            expressions: Optional[list] = None,
            params: Optional[dict] = None,
    ) -> int:
        """

        :param db:
        :param expressions:
        :param params:
        :return:
        """
        if params is None:
            params = {}

        stmt = select(func.count(self.model.id))
        if expressions:
            stmt = stmt.filter(*expressions)
        if params:
            stmt = stmt.filter_by(**params)
        return db.execute(stmt).scalar_one()

    def exists(
            self, db: "Session",
            expressions: Optional[Iterable] = None,
            params: Optional[dict] = None,
    ) -> Any:
        """
        Check the item exist
        :param db:
        :param expressions:
        :param params:
        :return:
        """
        stmt = select(self.model)
        if expressions:
            stmt = stmt.filter(*expressions)
        if params:
            stmt = stmt.filter_by(**params)
        return db.execute(select(stmt.exists())).scalar_one()

    def get_all(
            self,
            db: "Session",
            *,
            offset: int = 0,
            limit: int = 100,
            q: Optional[dict] = None,
            order_by: Optional[Iterable[str]] = None,
            options: Optional[Iterable] = None,
            expressions: Optional[Iterable] = None,
    ) -> Iterable:
        """

        :param db: sqlalchemy.orm.Session
        :param offset:
        :param limit:
        :param q:
        :param order_by:
        :param expressions:
        :param options:
        :return:
        """
        stmt = select(self.model)

        if options:
            stmt = stmt.options(*options)
        if expressions:
            stmt = stmt.filter(*expressions)
        if q:
            stmt = stmt.filter_by(**q)
        if not order_by:
            sort = (getattr(self.model, self.primary_field).desc(),)
        else:
            sort = tuple(text(f'{i[1:]} DESC') if i.startswith('-') else text(f'{i} ASC') for i in order_by)
        stmt = stmt.order_by(*sort).offset(offset=offset).limit(limit=limit)

        result = db.execute(stmt).scalars().fetchall()
        return result

    def get_by_params(
            self, db: "Session",

            options: Optional[Iterable] = (),
            expressions: Optional[Iterable] = (),
            params: Optional[dict] = None
    ) -> ModelType:
        """
        Retrieve items by params
        :param db:
        :param options:
        :param expressions:
        :param params:
        :return:
        """
        if params is None:
            params = {}
        result = db.execute(select(self.model).options(*options).filter(*expressions).filter_by(**params))

        return result.scalar_one()

    def get(
            self,
            db: "Session",
            obj_id: Union[int, UUID],
            options: Optional[Iterable] = ()
    ) -> ModelType:
        """
        Retrieve obj, if does not exist raise exception
        :param db:
        :param obj_id:
        :param options:
        :return:
        """
        result = db.execute(select(self.model).options(*options).where(self.model.id == obj_id))

        return result.scalar_one()

    @staticmethod
    def update(
            db: "Session",
            db_obj: ModelType,
            obj_in: Dict[str, Any]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj, custom_encoder={Choices: lambda x: x.value})
        obj_in = jsonable_encoder(obj_in, custom_encoder={Choices: lambda x: x.value})
        for field in obj_data:
            if field in obj_in:
                setattr(db_obj, field, obj_in[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(
            db: "Session",
            db_obj: ModelType
    ) -> ModelType:
        """
        Delete obj
        :param db_obj:
        :param db:
        :return:
        """
        db.delete(db_obj)
        db.commit()
        return db_obj

    def remove(self, db: "Session", expressions: list):
        statement = delete(self.model).where(*expressions)
        result = db.execute(statement)
        db.commit()
        return result


class CRUDBase(Generic[ModelType]):
    __slots__ = ('model', 'primary_field')

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**


        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def count(
            self, async_db: "AsyncSession", *,
            expressions: Optional[Iterable] = (),
            params: Optional[dict] = None,
    ) -> int:
        """

        :param async_db:
        :param expressions:
        :param params:
        :return:
        """
        if params is None:
            params = {}
        query = await async_db.execute(select(func.count(self.model.id)).filter(*expressions).filter_by(**params))
        return query.scalar_one()

    async def exists(
            self, async_db: "AsyncSession", *,
            expressions: Optional[Iterable] = (),
            params: Optional[dict] = None,
    ) -> Any:
        """
        Check the item exist
        :param async_db:
        :param expressions:
        :param params:
        :return:
        """
        if params is None:
            params = {}
        query = await async_db.execute(select(select(self.model).filter(*expressions).filter_by(**params).exists()))
        return query.scalar_one()

    async def get_by_params(
            self, async_db: "AsyncSession",
            expressions: Optional[Iterable] = (),
            options: Optional[Iterable] = (),
            params: Optional[dict] = None, ) -> ModelType:
        """
        Retrieve items by params
        :param async_db:
        :param expressions:
        :param options:
        :param params:
        :return:
        """
        if params is None:
            params = {}
        select_q = select(self.model).options(*options).filter(*expressions).filter_by(**params)
        result = await async_db.execute(select_q)

        return result.scalar_one()

    async def first(
            self,
            async_db: "AsyncSession",
            *,
            params: Optional[dict] = None,
            expressions: Optional[Iterable] = (),
            options: Optional[Iterable] = (),
    ) -> Optional[ModelType]:
        """
        Soft retrieve obj
        :param async_db:
        :param params:
        :param expressions:
        :param options:
        :return:
        """
        if params is None:
            params = {}
        select_q = select(self.model).options(*options).filter(*expressions).filter_by(**params)
        result = await async_db.execute(select_q)
        return result.scalars().first()

    async def get(
            self,
            async_db: "AsyncSession",
            obj_id: Union[int, UUID],
            options: Optional[Iterable] = (),
    ) -> ModelType:
        """
        Retrieve obj, if it does not exist raise exception
        :param async_db:
        :param options:
        :param obj_id:
        :return:
        """
        result = await async_db.execute(select(self.model).options(*options).where(self.model.id == obj_id))

        return result.scalar_one()

    async def get_all(
            self,
            async_db: "AsyncSession",
            *,
            offset: Optional[int] = 0,
            limit: Optional[int] = 100,
            q: Optional[dict] = None,
            order_by: Optional[Iterable] = (),
            options: Optional[Iterable] = (),
            expressions: Optional[Iterable] = (),
    ):
        """

        :param async_db:
        :param offset:
        :param limit:
        :param q:
        :param order_by:
        :param options:
        :param expressions:
        :return:
        """
        if q is None:
            q = {}
        result = await async_db.execute(
            select(self.model).options(*options).filter(*expressions).filter_by(**q).order_by(
                *order_by).offset(offset).limit(limit)
        )
        return result.scalars().fetchall()

    async def create(self, async_db: "AsyncSession", *, obj_in: Union[dict, CreateSchemaType]) -> ModelType:
        # obj_in_data = jsonable_encoder(obj_in, custom_encoder={Choices: lambda x: x.value})
        if isinstance(obj_in, dict):
            # obj_in_data = jsonable_encoder(obj_in, custom_encoder={Choices: lambda x: x.value})
            obj_in_data = obj_in
        else:
            obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)  # type: ignore
        async_db.add(db_obj)
        await async_db.commit()
        await async_db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update(
            async_db: "AsyncSession",
            *,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj, custom_encoder={Choices: lambda x: x.value})
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        async_db.add(db_obj)
        await async_db.commit()
        await async_db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def delete(
            async_db: "AsyncSession", *,
            db_obj: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Delete obj
        :param db_obj:
        :param async_db:
        :return:
        """
        await async_db.delete(db_obj)
        await async_db.commit()
        return db_obj
