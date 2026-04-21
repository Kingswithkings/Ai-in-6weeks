from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.db.database import init_db
from app.services.rag_service import load_sample_data


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    load_sample_data()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router)
