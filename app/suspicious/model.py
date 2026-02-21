from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum as SqlEnum

from app.core.database import Base
from app.suspicious.verdicts import PacketLabel


class SuspiciousPacket(Base):
    __tablename__ = 'suspicious_packets'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    src_ip = Column(String, nullable=False, index=True)
    src_mac = Column(String, nullable=False, index=True)
    dst_mac = Column(String, nullable=False, index=True)
    probability = Column(Float, nullable=False)
    
    ack_flag_number = Column(Float, nullable=False)
    https = Column(Float, nullable=False)
    rate = Column(Float, nullable=False)
    header_length = Column(Float, nullable=False)
    variance = Column(Float, nullable=False)
    max = Column(Float, nullable=False)
    tot_sum = Column(Float, nullable=False)
    time_to_live = Column(Float, nullable=False)
    std = Column(Float, nullable=False)
    psh_flag_number = Column(Float, nullable=False)
    min = Column(Float, nullable=False)
    dns = Column(Float, nullable=False)

    label = Column(SqlEnum(PacketLabel), default=PacketLabel.PENDING, nullable=False, index=True)
