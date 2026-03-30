from pydantic import BaseModel
from typing import Optional
from app.suspicious.verdicts import PacketLabel


class PacketLabelUpdateRequest(BaseModel):
    label: PacketLabel


class SuspiciousPacketResponse(BaseModel):
    id: int
    user_id: Optional[int]

    src_ip: str
    src_mac: str
    dst_mac: str

    probability: float
    ack_flag_number: float
    https: float
    rate: float
    header_length: float
    variance: float
    max: float
    tot_sum: float
    time_to_live: float
    std: float
    psh_flag_number: float
    min: float
    dns: float

    label: PacketLabel

    class Config:
        from_attributes = True
