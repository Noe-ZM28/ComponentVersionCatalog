from fastapi import FastAPI

from app.config import settings


app = FastAPI(
    title=settings.app_name,
    description="API para administrar proyectos, componentes e historial de cambios.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "application": settings.app_name,
    }

@app.get("/about")
def about():
    return {
        "project": "Component Version Catalog",
        "version": "0.1.0",
        "database": "SQLite",
    }
    
@app.get("/")
def root():
    return{
        "message": "Bienvenido a la API de Component Version Catalog",
    }