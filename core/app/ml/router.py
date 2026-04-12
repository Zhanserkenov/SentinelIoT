import json
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.app.ml.rabbitmq_client import publish_analysis_task
from core.app.ml.schemas import FlowFeatures, WindowAnalysisResponse
from core.app.core.database import get_db
from core.app.core.redis import get_redis
from core.app.core.security import get_current_user
from core.app.users.model import User
from core.app.users.service import get_user_by_orange_pi_id

router = APIRouter(prefix="/flows", tags=["Flows"])

@router.post("/analyze-window", status_code=202)
async def analyze_window_api(
    flows: List[FlowFeatures],
    x_orange_pi_id: str | None = Header(default=None, alias="X-Orange-Pi-Id"),
    db: AsyncSession = Depends(get_db),
):
    if not x_orange_pi_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-Orange-Pi-Id")
    user = await get_user_by_orange_pi_id(db, x_orange_pi_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Orange Pi identifier")

    flows_dict = [f.model_dump() for f in flows]
    task_id = await publish_analysis_task(user.id, flows_dict)
    return {"status": "queued", "task_id": task_id, "message": "Traffic window sent for analysis"}


@router.get("/results", response_model=WindowAnalysisResponse)
async def get_results_api(current_user: User = Depends(get_current_user)):
    redis = get_redis()
    raw = await redis.get(f"analysis_result:{current_user.id}")
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis results yet",
        )
    return WindowAnalysisResponse(**json.loads(raw))