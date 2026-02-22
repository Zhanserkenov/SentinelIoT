from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from fastapi import HTTPException, status

from app.suspicious.model import SuspiciousPacket
from app.suspicious.verdicts import PacketLabel


async def save_suspicious_packets(db: AsyncSession, suspicious_packets: List[Dict[str, Any]], user_id: int) -> None:
    if not suspicious_packets:
        return

    packet_objects = []
    for packet in suspicious_packets:
        packet_obj = SuspiciousPacket(
            user_id=user_id,

            src_ip=packet.get("src_ip", ""),
            src_mac=packet.get("src_mac", ""),
            dst_mac=packet.get("dst_mac", ""),

            probability=packet.get("probability", 0.0),
            ack_flag_number=packet.get("ack_flag_number", 0.0),
            https=packet.get("https", 0.0),
            rate=packet.get("rate", 0.0),
            header_length=packet.get("header_length", 0.0),
            variance=packet.get("variance", 0.0),
            max=packet.get("max", 0.0),
            tot_sum=packet.get("tot_sum", 0.0),
            time_to_live=packet.get("time_to_live", 0.0),
            std=packet.get("std", 0.0),
            psh_flag_number=packet.get("psh_flag_number", 0.0),
            min=packet.get("min", 0.0),
            dns=packet.get("dns", 0.0)
        )
        packet_objects.append(packet_obj)

    db.add_all(packet_objects)
    await db.commit()


async def get_suspicious_packets(
        db: AsyncSession,
        user_id: Optional[int] = None,
        src_ip: Optional[str] = None,
        src_mac: Optional[str] = None,
        dst_mac: Optional[str] = None,
        label: Optional[PacketLabel] = None,
        offset: int = 0
) -> List[SuspiciousPacket]:

    stmt = select(SuspiciousPacket)
    limit = 30

    if user_id is not None:
        stmt = stmt.where(SuspiciousPacket.user_id == user_id)

    if src_ip is not None:
        stmt = stmt.where(SuspiciousPacket.src_ip == src_ip)

    if src_mac is not None:
        stmt = stmt.where(SuspiciousPacket.src_mac == src_mac)

    if dst_mac is not None:
        stmt = stmt.where(SuspiciousPacket.dst_mac == dst_mac)

    if label is not None:
        stmt = stmt.where(SuspiciousPacket.label == label)

    stmt = stmt.order_by(SuspiciousPacket.id.desc()).limit(limit).offset(offset)

    result = await db.execute(stmt)

    return list(result.scalars().all())


async def update_packet_label(db: AsyncSession, packet_id: int, new_label: PacketLabel) -> SuspiciousPacket:
    stmt = select(SuspiciousPacket).where(SuspiciousPacket.id == packet_id)
    result = await db.execute(stmt)
    packet = result.scalar_one_or_none()

    if packet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Packet with id {packet_id} not found"
        )

    packet.label = new_label
    await db.commit()
    await db.refresh(packet)

    return packet
