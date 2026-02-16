from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.suspicious.model import SuspiciousPacket


async def save_suspicious_packets(db: AsyncSession, suspicious_packets: List[Dict[str, Any]], user_id: int) -> None:
    if not suspicious_packets:
        return

    packet_objects = []
    for packet in suspicious_packets:
        packet_obj = SuspiciousPacket(
            user_id=user_id,
            src_mac=packet.get("src_mac", ""),
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

