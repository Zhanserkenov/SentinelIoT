from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StatsGroupBy(str, Enum):
    hour = "hour"
    day = "day"
    week = "week"


class TrafficTimeseriesPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bucket_start: datetime = Field()
    total_flows: int
    anomalous_sources: int
    suspicious_sources: int
