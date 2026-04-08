from typing import Annotated
from pydantic import BaseModel, Field


class ConnectedDeviceIn(BaseModel):
    ip: str
    mac: str
    iface: str = ""


class DevicesSnapshotIn(BaseModel):
    ts: float
    devices: Annotated[list[ConnectedDeviceIn], Field(default_factory=list)]


class ConnectedDeviceOut(BaseModel):
    ip: str
    mac: str
    iface: str
    last_seen_ts: float
