from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.app.core.database import get_db
from core.app.core.security import get_current_user
from core.app.stats.schemas import StatsGroupBy, TrafficTimeseriesPoint
from core.app.stats.service import get_traffic_timeseries, resolve_query_range
from core.app.users.model import User

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/traffic/timeseries", response_model=List[TrafficTimeseriesPoint])
async def traffic_timeseries(
    group_by: StatsGroupBy = Query(StatsGroupBy.day),
    from_ts: Optional[datetime] = Query(None, alias="from"),
    to_ts: Optional[datetime] = Query(None, alias="to"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start, end = resolve_query_range(group_by, from_ts, to_ts)
    if end <= start:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'to' must be after 'from'")

    points = await get_traffic_timeseries(db, current_user.id, group_by, start, end)
    return [TrafficTimeseriesPoint(**p) for p in points]
