import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from aerial_photography.config import settings
from aerial_photography.api.v1.api import api_router
from aerial_photography.database.base_class import Base
from aerial_photography.database.session import engine, SessionLocal
from aerial_photography.vectorizer.vectorizer import device
import logging


# ======== Sync ============
Base.metadata.create_all(bind=engine)


logger = logging.getLogger("uvicorn.error")
app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # create_db_and_tables()
    yield
# @app.on_event("startup")
# def initial_db():
#     # pass
#     session = SessionLocal()
#     create_db_and_tables()


logger.info(f"Device: {device}")
if __name__ == "__main__":
    uvicorn.run("aerial_photography.app:app", port=8000, log_level="info", reload=True)
