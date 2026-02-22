from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.suspicious.service import get_suspicious_packets
from app.suspicious.schemas import SuspiciousPacketResponse
from app.core.security import get_current_admin
from app.suspicious.verdicts import PacketLabel
from app.users.model import User
from app.core.database import get_db
from typing import List, Optional

router = APIRouter(prefix="/suspicious", tags=["Suspicious"])


@router.get("/packets", response_model=List[SuspiciousPacketResponse])
async def get_suspicious_packets_api(
        current_user: User = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),

        user_id: Optional[int] = None,
        src_ip: Optional[str] = None,
        src_mac: Optional[str] = None,
        dst_mac: Optional[str] = None,
        label: Optional[PacketLabel] = None,
        offset: int = 0
):
    packets = await get_suspicious_packets(
        db=db,
        user_id=user_id,
        src_ip=src_ip,
        src_mac=src_mac,
        dst_mac=dst_mac,
        label=label,
        offset=offset
    )

    return packets