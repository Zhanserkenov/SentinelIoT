from contextlib import asynccontextmanager, suppress
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.app.auth.router import router as auth_router
from core.app.core.redis import close_redis_connection
from core.app.ml.router import router as ml_router
from core.app.ml.results_consumer import consume_ml_results
from core.app.suspicious.router import router as suspicious_router
from core.app.suspicious.scheduler import register_suspicious_export_scheduler
from core.app.users.router import router as users_router

scheduler = AsyncIOScheduler()
ml_results_consumer_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global ml_results_consumer_task
    register_suspicious_export_scheduler(scheduler)
    scheduler.start()
    ml_results_consumer_task = asyncio.create_task(consume_ml_results())
    try:
        yield
    finally:
        if ml_results_consumer_task:
            ml_results_consumer_task.cancel()
            with suppress(asyncio.CancelledError):
                await ml_results_consumer_task
        scheduler.shutdown(wait=False)
        await close_redis_connection()


app = FastAPI(lifespan=lifespan)

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