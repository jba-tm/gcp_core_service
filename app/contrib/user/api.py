from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic_core import ErrorDetails

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.schema import IResponseBase, IPaginationDataBase, CommonsModel
from app.routers.dependency import get_async_db, get_commons
from .schema import (
    UserVisible, UserBase, UserCreate,
    GroupVisible, GroupBase, GroupCreate,
    UserToGroupCreate, UserToGroupVisible,
)
from .repository import user_repo, group_repo, user_to_group_repo

api = APIRouter()


@api.get('/user/', tags=["users"], name='user-list', response_model=IPaginationDataBase[UserVisible])
async def get_user_list(
        async_db: AsyncSession = Depends(get_async_db),
        commons: CommonsModel = Depends(get_commons),

) -> dict:
    obj_list = await user_repo.get_all(async_db=async_db, offset=commons.offset, limit=commons.limit)
    count = await user_repo.count(async_db=async_db)
    return {

        'page': commons.page,
        'limit': commons.limit,
        'rows': obj_list,
        'count': count,
    }


@api.post("/user/create/", tags=["users"], name='user-create', response_model=IResponseBase[UserVisible],
          status_code=201)
async def create_user(
        obj_in: UserCreate,
        async_db: AsyncSession = Depends(get_async_db),
) -> dict:
    is_exists = await user_repo.exists(async_db=async_db, params={'name': obj_in.name})

    if is_exists:
        raise RequestValidationError(
            [ErrorDetails(
                msg='User with this name already exists',
                loc=('body', "name"),
                type='value_error',
                input=obj_in.name
            )]
        )
    result = await user_repo.create(async_db=async_db, obj_in=obj_in.model_dump())
    return {
        "message": "User created",
        "data": result
    }


@api.get("/user/{obj_id}/detail/", tags=["users"], name='user-detail', response_model=UserVisible)
async def get_single_user(
        obj_id: int,
        async_db: AsyncSession = Depends(get_async_db),

):
    return await user_repo.get(async_db=async_db, obj_id=obj_id)


@api.patch("/user/{obj_id}/update/", tags=["users"], name='user-update', response_model=IResponseBase[UserVisible])
async def update_user(
        obj_id: int,
        obj_in: UserBase,
        async_db: AsyncSession = Depends(get_async_db)
):
    db_obj = await user_repo.get(async_db=async_db, obj_id=obj_id)
    if obj_in.name:
        model = user_repo.model
        expressions = (
            model.id != db_obj.id,
            model.name == obj_in.name
        )
        is_exists = await user_repo.exists(async_db=async_db, expressions=expressions)

        if is_exists:
            raise RequestValidationError(
                [ErrorDetails(
                    msg='User with this name already exists',
                    loc=('body', "name"),
                    type='value_error',
                    input=obj_in.name
                )]
            )

    result = await user_repo.update(
        async_db=async_db,
        db_obj=db_obj,
        obj_in=obj_in.model_dump(exclude_unset=True)
    )
    return {
        'message': "User updated",
        'data': result
    }


@api.get('/user/{obj_id}/delete/', tags=["users"], name='user-delete', response_model=IResponseBase[UserVisible])
async def delete_user(

        obj_id: int,
        async_db: AsyncSession = Depends(get_async_db)
):
    db_obj = await user_repo.get(async_db=async_db, obj_id=obj_id)

    try:

        await user_repo.delete(async_db=async_db, db_obj=db_obj)
    except IntegrityError:
        await async_db.rollback()
        raise HTTPException(status_code=400, detail="Can't delete user")

    return {"message": "User deleted", "data": db_obj}


@api.get('/group/', name='group-list', tags=["groups"], response_model=IPaginationDataBase[GroupVisible])
async def group_list(
        async_db: AsyncSession = Depends(get_async_db),
        commons: CommonsModel = Depends(get_commons),

) -> dict:
    obj_list = await group_repo.get_all(async_db=async_db, offset=commons.offset, limit=commons.limit)
    count = await group_repo.count(async_db=async_db)
    return {
        'page': commons.page,
        'limit': commons.limit,
        'rows': obj_list,
        'count': count,
    }


@api.post('/group/create/', name='group-create', tags=['groups'], response_model=IResponseBase[GroupVisible],
          status_code=201)
async def group_create(
        obj_in: GroupCreate,
        async_db: AsyncSession = Depends(get_async_db),
) -> dict:
    is_exists = await group_repo.exists(async_db=async_db, params={'name': obj_in.name})

    if is_exists:
        raise RequestValidationError(
            [ErrorDetails(
                msg='Group with this name already exists',
                loc=('body', "name"),
                type='value_error',
                input=obj_in.name
            )]
        )
    result = await group_repo.create(async_db=async_db, obj_in=obj_in.model_dump())

    return {
        'message': "Group created",
        'data': result
    }


@api.get("/group/{obj_id}/detail/", tags=["groups"], name='group-detail', response_model=GroupVisible)
async def get_single_group(
        obj_id: int,
        async_db: AsyncSession = Depends(get_async_db),

):
    return await group_repo.get(async_db=async_db, obj_id=obj_id)


@api.patch(
    "/group/{obj_id}/update/", tags=["groups"], name='group-update',
    response_model=IResponseBase[GroupVisible]
)
async def update_group(
        obj_id: int,
        obj_in: GroupBase,
        async_db: AsyncSession = Depends(get_async_db)
):
    db_obj = await group_repo.get(async_db=async_db, obj_id=obj_id)
    if obj_in.name:
        model = group_repo.model
        expressions = (
            model.id != db_obj.id,
            model.name == obj_in.name
        )
        is_exists = await group_repo.exists(async_db=async_db, expressions=expressions)

        if is_exists:
            raise RequestValidationError(
                [ErrorDetails(
                    msg='Group with this name already exists',
                    loc=('body', "name"),
                    type='value_error',
                    input=obj_in.name
                )]
            )

    result = await group_repo.update(
        async_db=async_db,
        db_obj=db_obj,
        obj_in=obj_in.model_dump(exclude_unset=True)
    )
    return {
        'message': "Group updated",
        'data': result
    }


@api.get('/group/{obj_id}/delete/', tags=["groups"], name='group-delete', response_model=IResponseBase[GroupVisible])
async def delete_user(
        obj_id: int,
        async_db: AsyncSession = Depends(get_async_db)
):
    db_obj = await group_repo.get(async_db=async_db, obj_id=obj_id)

    try:

        await group_repo.delete(async_db=async_db, db_obj=db_obj)
    except IntegrityError:
        await async_db.rollback()
        raise HTTPException(status_code=400, detail="Can't delete group")

    return {"message": "Group deleted", "data": db_obj}


@api.get('/user-to-group/', tags=['users', 'groups'], name='user-to-group-list',
         response_model=IPaginationDataBase[UserToGroupVisible])
async def user_to_group_list(

        async_db: AsyncSession = Depends(get_async_db),
        commons: CommonsModel = Depends(get_commons),
) -> dict:
    obj_list = await user_to_group_repo.get_all(async_db=async_db, offset=commons.offset, limit=commons.limit)
    count = await user_to_group_repo.count(async_db=async_db)
    return {

        'page': commons.page,
        'limit': commons.limit,
        'rows': obj_list,
        'count': count,
    }


@api.post("/user-to-group/create/", tags=['users', 'groups'], name='user-to-group-create',
          response_model=IResponseBase[UserToGroupVisible], status_code=201)
async def create_user_to_group(
        obj_in: UserToGroupCreate,
        async_db: AsyncSession = Depends(get_async_db),

) -> dict:
    is_exists = await user_to_group_repo.exists(
        async_db=async_db,
        params={'user_id': obj_in.user_id, "group_id": obj_in.group_id}
    )

    if is_exists:
        raise RequestValidationError(
            [ErrorDetails(
                msg='User to group relation already exists',
                loc=('body', "user_id"),
                type='value_error',
                input=obj_in.user_id
            )]
        )
    result = await user_to_group_repo.create(async_db=async_db, obj_in=obj_in.model_dump())
    return {
        "message": "User to group relation created",
        "data": result
    }


@api.get("/user-to-group/{obj_id}/detail/", tags=['users', 'groups'], name='user-to-group-detail',
         response_model=UserToGroupVisible)
async def get_single_user_to_group(
        obj_id: int,
        async_db: AsyncSession = Depends(get_async_db),

):
    return await user_to_group_repo.get(async_db=async_db, obj_id=obj_id)


@api.get('/user-to-group/{obj_id}/delete/', tags=["users", "groups"], name='user-to-group-delete',
         response_model=IResponseBase[UserToGroupVisible])
async def delete_user_to_group(

        obj_id: int,
        async_db: AsyncSession = Depends(get_async_db)
):
    db_obj = await user_to_group_repo.get(async_db=async_db, obj_id=obj_id)
    try:

        await user_to_group_repo.delete(async_db=async_db, db_obj=db_obj)
    except IntegrityError:
        await async_db.rollback()
        raise HTTPException(status_code=400, detail="Can't delete user to group relation")

    return {"message": "User to group relation deleted", "data": db_obj}
