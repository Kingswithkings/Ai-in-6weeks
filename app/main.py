from fastapi import FastAPI
from app.api.routes import router
from app.db.database import init_db
from app.services.rag_services import load_sample_data

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()
    load_sample_data()

app.include_router(router)
