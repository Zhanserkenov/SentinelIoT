import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from core.app.ml.rabbitmq_client import publish_analysis_task
from core.app.ml.schemas import FlowFeatures, WindowAnalysisResponse
from core.app.core.redis import get_redis
from core.app.core.security import get_current_user
from core.app.users.model import User

router = APIRouter(prefix="/flows", tags=["Flows"])

@router.post("/analyze-window", status_code=202)
async def analyze_window_api(flows: List[FlowFeatures], current_user: User = Depends(get_current_user)):
    flows_dict = [f.model_dump() for f in flows]
    task_id = await publish_analysis_task(current_user.id, flows_dict)
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