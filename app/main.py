import uvicorn

from typing import Optional
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRoute

from sqlalchemy.exc import NoResultFound

from app.conf.config import settings
from app.core.handlers import request_document_raw_not_found_exception
from app.routers.urls import router
from app.routers.api import api


def custom_generate_unique_id(route: APIRoute):
    return route.name


def get_application(
        app_router: APIRouter,
        app_api: APIRouter,
        root_path: Optional[str] = None,
        root_path_in_servers: Optional[bool] = False,
        openapi_url: Optional[str] = "/openapi.json",
        api_prefix: Optional[str] = ''
) -> FastAPI:
    application = FastAPI(
        default_response_class=ORJSONResponse,
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        version=settings.VERSION,
        openapi_url=openapi_url,
        root_path=root_path,
        root_path_in_servers=root_path_in_servers,
        generate_unique_id_function=custom_generate_unique_id,
        exception_handlers={
            NoResultFound: request_document_raw_not_found_exception,
        },
    )
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    application.include_router(app_api, prefix=api_prefix)
    application.include_router(app_router)

    return application


app = get_application(
    root_path=settings.ROOT_PATH,
    root_path_in_servers=settings.ROOT_PATH_IN_SERVERS,
    openapi_url=settings.OPENAPI_URL,
    app_router=router,
    app_api=api,
    api_prefix=settings.API_V1_STR,
)

if __name__ == "__main__":
    # noinspection PyTypeChecker
    uvicorn.run(
        get_application(
            root_path=settings.ROOT_PATH,
            root_path_in_servers=settings.ROOT_PATH_IN_SERVERS,
            openapi_url=settings.OPENAPI_URL,
            app_router=router,
            app_api=api,
        ),
        host="0.0.0.0", port=8000
    )
