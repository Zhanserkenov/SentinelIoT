from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint

from core.app.core.database import Base


class TrafficStats(Base):
    __tablename__ = "traffic_stats"
    __table_args__ = (
        UniqueConstraint("user_id", "period_start", name="uq_traffic_stats_user_period"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)

    total_flows = Column(Integer, nullable=False, default=0)
    anomalous_sources = Column(Integer, nullable=False, default=0)
    suspicious_sources = Column(Integer, nullable=False, default=0)
