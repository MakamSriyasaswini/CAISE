from fastapi import FastAPI

from gateway.routes.object_routes import router as object_router
from gateway.routes.health_routes import router as health_router
from gateway.routes.evaluation_routes import router as evaluation_router


app = FastAPI(
    title="CAISE",
    description="Cloud-Agnostic Intelligent Storage Engine",
    version="1.0.0"
)


app.include_router(
    health_router,
    prefix="/api"
)


app.include_router(
    object_router,
    prefix="/api"
)


app.include_router(
    evaluation_router,
    prefix="/api"
)


@app.get("/")
def root():

    return {
        "message": "Welcome to CAISE"
    } 