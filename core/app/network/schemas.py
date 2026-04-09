from typing import Annotated
from pydantic import BaseModel, Field


class ConnectedDeviceIn(BaseModel):
    ip: str
    mac: str


class DevicesSnapshotIn(BaseModel):
    devices: Annotated[list[ConnectedDeviceIn], Field(default_factory=list)]


class ConnectedDeviceOut(BaseModel):
    ip: str
    mac: str
