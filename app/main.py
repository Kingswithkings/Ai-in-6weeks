from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="AI in 6 Weeks API")
app.include_router(router)

@app.get("/")
def root():
    return {"message": "AI system is running"}