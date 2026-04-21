from fastapi import FastAPI
from app.api.routes import router
from app.db.database import init_db

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

app.include_router(router)

@app.get("/")
def root():
    return {"message": "AI system is running"}