from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.ml.router import router as ml_router
from app.suspicious.router import router as suspicious_router

app = FastAPI()

app.include_router(auth_router)

app.include_router(ml_router)
app.include_router(suspicious_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
