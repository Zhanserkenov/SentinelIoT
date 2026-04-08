from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.app.core.database import get_db
from core.app.core.redis import get_redis
from core.app.core.security import get_current_admin
from core.app.network.schemas import ConnectedDeviceOut, DevicesSnapshotIn
from core.app.network.service import get_online_devices, upsert_devices_snapshot
from core.app.users.service import get_user_by_orange_pi_id
from core.app.users.model import User

router = APIRouter(prefix="/network", tags=["Network"])

@router.post("/devices", status_code=status.HTTP_202_ACCEPTED)
async def ingest_connected_devices(
    payload: DevicesSnapshotIn,
    x_orange_pi_id: str | None = Header(default=None, alias="X-Orange-Pi-Id"),
    db: AsyncSession = Depends(get_db),
):
    if not x_orange_pi_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-Orange-Pi-Id")
    user = await get_user_by_orange_pi_id(db, x_orange_pi_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Orange Pi identifier")

    redis = get_redis()
    count = await upsert_devices_snapshot(redis, user.id, payload.devices, payload.ts)
    return {"status": "accepted", "devices_count": count}


@router.get("/devices", response_model=list[ConnectedDeviceOut])
async def get_online_connected_devices(current_user: User = Depends(get_current_admin)):
    redis = get_redis()
    return await get_online_devices(redis, current_user.id)
