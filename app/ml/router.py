from fastapi import APIRouter, Depends, Body
from app.ml.schemas import FlowFeatures, WindowAnalysisResponse
from app.ml.service import analyze_window, get_user_analysis_result
from app.core.security import get_current_user
from app.users.models import User
from typing import List

router = APIRouter(prefix="/flows", tags=["Flows"])

@router.post("/analyze-window", response_model=WindowAnalysisResponse)
def analyze_window_api(flows: List[FlowFeatures], current_user: User = Depends(get_current_user)):
    return analyze_window(flows, current_user.id)

@router.get("/results", response_model=WindowAnalysisResponse)
def get_results_api(current_user: User = Depends(get_current_user)):
    return get_user_analysis_result(current_user.id)