from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.ml.router import router as ml_router
from app.suspicious.router import router as suspicious_router
from app.users.router import router as users_router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

app.include_router(ml_router)
app.include_router(suspicious_router)
app.include_router(users_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}