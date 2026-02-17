from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.suspicious.service import get_suspicious_packets
from app.suspicious.schemas import SuspiciousPacketResponse
from app.core.security import get_current_admin
from app.users.model import User
from app.core.database import get_db
from typing import List

router = APIRouter(prefix="/suspicious", tags=["Suspicious"])

@router.get("/packets", response_model=List[SuspiciousPacketResponse])
async def get_suspicious_packets_api(current_user: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    return await get_suspicious_packets(db)