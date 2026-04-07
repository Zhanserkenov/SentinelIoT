import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from analyzer.app.ml.rabbitmq_worker import consume_analysis_tasks

worker_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global worker_task
    worker_task = asyncio.create_task(consume_analysis_tasks())
    try:
        yield
    finally:
        if worker_task:
            worker_task.cancel()
            with suppress(asyncio.CancelledError):
                await worker_task


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}