from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic_core import ErrorDetails

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.schema import IResponseBase, IPaginationDataBase, CommonsModel
from app.routers.dependency import get_async_session, get_commons
from .schema import (
    SchoolBase, SchoolVisible, SchoolCreate,

    UserToSchoolBase, UserToSchoolCreate, UserToSchoolVisible
)
from .repository import school_repo, user_to_school_repo

api = APIRouter()


@api.get('/', name='school-list', response_model=IPaginationDataBase[SchoolVisible])
async def get_user_list(
        async_db: AsyncSession = Depends(get_async_session),
        commons: CommonsModel = Depends(get_commons),

) -> dict:
    obj_list = await school_repo.get_all(async_db=async_db, offset=commons.offset, limit=commons.limit)
    count = await school_repo.count(async_db=async_db)
    return {

        'page': commons.page,
        'limit': commons.limit,
        'rows': obj_list,
        'count': count,
    }


@api.post("/school/create/", tags=["schools"], name='school-create', response_model=IResponseBase[SchoolVisible])
async def create_school(
        obj_in: SchoolCreate,
        async_db: AsyncSession = Depends(get_async_session),

) -> dict:
    is_exists = await school_repo.exists(async_db=async_db, params={'name': obj_in.name})

    if is_exists:
        raise RequestValidationError(
            [ErrorDetails(
                msg='School with this name already exists',
                loc=('body', "name"),
                type='value_error',
                input=obj_in.name
            )]
        )
    result = await school_repo.create(async_db=async_db, obj_in=obj_in.model_dump())
    return {
        "message": "School created",
        "data": result
    }


@api.get("/school/{obj_id}/detail/", tags=["schools"], name='school-detail', response_model=SchoolVisible)
async def get_single_school(
        obj_id: int,
        async_db: AsyncSession = Depends(get_async_session),

):
    return await school_repo.get(async_db=async_db, obj_id=obj_id)


@api.patch("/school/{obj_id}/update/", tags=["schools"], name='school-update',
           response_model=IResponseBase[SchoolVisible])
async def update_school(
        obj_id: int,
        obj_in: SchoolBase,
        async_db: AsyncSession = Depends(get_async_session)
):
    db_obj = await school_repo.get(async_db=async_db, obj_id=obj_id)
    if obj_in.name:
        model = school_repo.model
        expressions = (
            model.id != db_obj.id,
            model.name == obj_in.name
        )
        is_exists = await school_repo.exists(async_db=async_db, expressions=expressions)

        if is_exists:
            raise RequestValidationError(
                [ErrorDetails(
                    msg='School with this name already exists',
                    loc=('body', "name"),
                    type='value_error',
                    input=obj_in.name
                )]
            )

    result = await school_repo.update(
        async_db=async_db,
        db_obj=db_obj,
        obj_in=obj_in.model_dump(exclude_unset=True)
    )
    return {
        'message': "School updated",
        'data': result
    }


@api.get('/school/{obj_id}/delete/', tags=["schools"], name='school-delete',
         response_model=IResponseBase[SchoolVisible])
async def delete_school(

        obj_id: int,
        async_db: AsyncSession = Depends(get_async_session)
):
    db_obj = await school_repo.get(async_db=async_db, obj_id=obj_id)

    try:

        await school_repo.delete(async_db=async_db, db_obj=db_obj)
    except IntegrityError:
        await async_db.rollback()
        raise HTTPException(status_code=400, detail="Can't delete school")

    return {"message": "School deleted", "data": db_obj}


@api.get('/user-to-school/', tags=['users', 'schools'], name='user-to-school-list',
         response_model=IPaginationDataBase[UserToSchoolVisible])
async def user_to_school_list(

        async_db: AsyncSession = Depends(get_async_session),
        commons: CommonsModel = Depends(get_commons),
) -> dict:
    obj_list = await user_to_school_repo.get_all(async_db=async_db, offset=commons.offset, limit=commons.limit)
    count = await user_to_school_repo.count(async_db=async_db)
    return {

        'page': commons.page,
        'limit': commons.limit,
        'rows': obj_list,
        'count': count,
    }


@api.post("/user-to-group/create/", tags=['users', 'schools'], name='user-to-school-create',
          response_model=IResponseBase[UserToSchoolVisible])
async def create_user_to_school(
        obj_in: UserToSchoolCreate,
        async_db: AsyncSession = Depends(get_async_session),

) -> dict:
    is_exists = await user_to_school_repo.exists(
        async_db=async_db,
        params={'user_id': obj_in.user_id, "school_id": obj_in.school_id}
    )

    if is_exists:
        raise RequestValidationError(
            [ErrorDetails(
                msg='User to school relation already exists',
                loc=('body', "user_id"),
                type='value_error',
                input=obj_in.user_id
            )]
        )
    result = await user_to_school_repo.create(async_db=async_db, obj_in=obj_in.model_dump())
    return {
        "message": "User to school relation created",
        "data": result
    }


@api.get("/user-to-school/{obj_id}/detail/", tags=['users', 'schools'], name='user-to-school-detail',
         response_model=UserToSchoolVisible)
async def get_single_user_to_school(
        obj_id: int,
        async_db: AsyncSession = Depends(get_async_session),

):
    return await user_to_school_repo.get(async_db=async_db, obj_id=obj_id)


@api.get("/user-to-school/{obj_id}/update/", tags=['users', 'schools'], name='user-to-school-update',
         response_model=UserToSchoolVisible)
async def update_user_to_school(
        obj_id: int,
        obj_in: UserToSchoolBase,
        async_db: AsyncSession = Depends(get_async_session),

):
    db_obj = await user_to_school_repo.get(async_db=async_db, obj_id=obj_id)
    result = await user_to_school_repo.update(async_db=async_db, db_obj=db_obj,
                                              obj_in=obj_in.model_dump(exclude_unset=True))

    return {
        "message": "User to school relation updated",
        "data": result
    }


@api.get('/user-to-school/{obj_id}/delete/', tags=["users", "schools"], name='user-to-school-delete',
         response_model=IResponseBase[UserToSchoolVisible])
async def delete_user_to_school(

        obj_id: int,
        async_db: AsyncSession = Depends(get_async_session)
):
    db_obj = await user_to_school_repo.get(async_db=async_db, obj_id=obj_id)
    try:

        await user_to_school_repo.delete(async_db=async_db, db_obj=db_obj)
    except IntegrityError:
        await async_db.rollback()
        raise HTTPException(status_code=400, detail="Can't delete user to school relation")

    return {"message": "User to school relation deleted", "data": db_obj}
