from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="AI System",
    description="Clean AI system architecture with FastAPI",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "AI system is running"}