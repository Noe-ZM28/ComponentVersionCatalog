from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import (
    changes_router,
    components_router,
    files_router,
    general_router,
    projects_router,
    tickets_router,
)
from app.api.general import REPOSITORY_ROOT
from app.config import settings


app = FastAPI(
    title=settings.app_name,
    description="API para administrar proyectos, componentes e historial de cambios.",
    version="0.1.0",
)

app.mount(
    "/css",
    StaticFiles(directory=REPOSITORY_ROOT / "css"),
    name="frontend-css",
)
app.mount(
    "/js",
    StaticFiles(directory=REPOSITORY_ROOT / "js"),
    name="frontend-js",
)

for router in (
    general_router,
    projects_router,
    components_router,
    tickets_router,
    changes_router,
    files_router,
    ):
    app.include_router(router)
