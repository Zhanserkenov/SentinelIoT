from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.ml.schemas import FlowFeatures, WindowAnalysisResponse
from app.ml.service import analyze_window, get_user_analysis_result
from app.suspicious.service import save_suspicious_packets
from app.core.security import get_current_user
from app.users.model import User
from typing import List
from app.core.database import get_db

router = APIRouter(prefix="/flows", tags=["Flows"])

@router.post("/analyze-window", response_model=WindowAnalysisResponse)
async def analyze_window_api(flows: List[FlowFeatures], current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result, suspicious_packets = analyze_window(flows, current_user.id)

    if suspicious_packets:
        await save_suspicious_packets(db, suspicious_packets, current_user.id)

    return result

@router.get("/results", response_model=WindowAnalysisResponse)
def get_results_api(current_user: User = Depends(get_current_user)):
    return get_user_analysis_result(current_user.id)