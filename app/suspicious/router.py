from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.suspicious.service import get_suspicious_packets, update_packet_label, export_and_delete_labeled_packets
from app.suspicious.schemas import SuspiciousPacketResponse, PacketLabelUpdateRequest
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


@router.patch("/packets/{packet_id}/label", response_model=SuspiciousPacketResponse)
async def update_packet_label_api(
        packet_id: int,
        request: PacketLabelUpdateRequest,
        current_user: User = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db)
):
    updated_packet = await update_packet_label(
        db=db,
        packet_id=packet_id,
        new_label=request.label
    )

    return updated_packet


@router.post("/packets/export-and-delete")
async def export_and_delete_labeled_packets_api(current_user: User = Depends(get_current_admin),db: AsyncSession = Depends(get_db)):
    download_url = await export_and_delete_labeled_packets(db)
    return {
        "status": "success",
        "download_url": download_url
    }