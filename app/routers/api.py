from fastapi import APIRouter

from app.contrib.user.api import api as user_api
from app.contrib.school.api import api as school_api

api = APIRouter()

api.include_router(user_api)
api.include_router(school_api, tags=['schools'], prefix="/school")
