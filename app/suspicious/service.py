from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from sqlalchemy import select, delete
from fastapi import HTTPException, status
import pandas as pd
from datetime import datetime
import io
import asyncio
import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from app.suspicious.model import SuspiciousPacket
from app.suspicious.verdicts import PacketLabel

load_dotenv()

GDRIVE_SERVICE_ACCOUNT_FILE = os.getenv("GDRIVE_SERVICE_ACCOUNT_FILE")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")


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


def upload_to_gdrive_sync(filename: str, csv_bytes: io.BytesIO) -> str:
    if not GDRIVE_SERVICE_ACCOUNT_FILE:
        raise ValueError("GDRIVE_SERVICE_ACCOUNT_FILE not configured in .env")
    if not GDRIVE_FOLDER_ID:
        raise ValueError("GDRIVE_FOLDER_ID not configured in .env")

    credentials = service_account.Credentials.from_service_account_file(
        GDRIVE_SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/drive.file']
    )

    service = build('drive', 'v3', credentials=credentials)

    csv_bytes.seek(0)
    media = MediaIoBaseUpload(
        csv_bytes,
        mimetype='text/csv',
        resumable=True
    )

    file_metadata = {
        'name': filename,
        'parents': [GDRIVE_FOLDER_ID]
    }

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,webViewLink'
    ).execute()
    
    return file.get('webViewLink', '')


async def export_and_delete_labeled_packets(db: AsyncSession) -> str:
    stmt = select(SuspiciousPacket).where(
        SuspiciousPacket.label.in_([PacketLabel.BENIGN, PacketLabel.ATTACK])
    )
    result = await db.execute(stmt)
    packets = list(result.scalars().all())
    
    if not packets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No packets with BENIGN or ATTACK labels found"
        )

    packets_data = []
    packet_ids = []
    for packet in packets:
        packet_dict = {
            'id': packet.id,
            'probability': packet.probability,
            'ack_flag_number': packet.ack_flag_number,
            'https': packet.https,
            'rate': packet.rate,
            'header_length': packet.header_length,
            'variance': packet.variance,
            'max': packet.max,
            'tot_sum': packet.tot_sum,
            'time_to_live': packet.time_to_live,
            'std': packet.std,
            'psh_flag_number': packet.psh_flag_number,
            'min': packet.min,
            'dns': packet.dns,
            'label': packet.label.value
        }
        packets_data.append(packet_dict)
        packet_ids.append(packet.id)

    df = pd.DataFrame(packets_data)
    csv_bytes = io.BytesIO()
    df.to_csv(csv_bytes, index=False)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"labeled_packets_{timestamp}.csv"
    
    try:
        download_url = await asyncio.to_thread(
            upload_to_gdrive_sync,
            filename,
            csv_bytes
        )

        delete_stmt = delete(SuspiciousPacket).where(SuspiciousPacket.id.in_(packet_ids))
        await db.execute(delete_stmt)
        await db.commit()
        
        return download_url
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file to Google Drive: {str(e)}"
        )