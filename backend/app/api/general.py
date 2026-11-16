from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.services.catalog_seed import seed_catalog

router = APIRouter()

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "application": settings.app_name,
    }

@router.get("/about")
def about():
    return {
        "project": "Component Version Catalog",
        "version": "0.1.0",
        "database": "Microsoft SQL Server",
    }

@router.post("/catalog/seed-demo")
def seed_demo_catalog(db: Session = Depends(get_db)):
    created = seed_catalog(db)
    return {
        "message": "Catálogo de demostración cargado.",
        "created": created,
    }

@router.get("/")
def root():
    return FileResponse(REPOSITORY_ROOT / "index.html")

@router.get("/hello")
def hello():
    return{
        "message": "Hola Desarrollador",
        "application": settings.app_name,
    }
