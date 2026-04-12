from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.app.stats.model import TrafficStats
from core.app.stats.schemas import StatsGroupBy


def _utc_hour_start(when: datetime | None = None) -> datetime:
    dt = when or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.replace(minute=0, second=0, microsecond=0)


async def add_window_summary_to_hourly_stats(
    db: AsyncSession,
    user_id: int,
    summary: Dict[str, Any],
) -> None:
    period_start = _utc_hour_start()
    total_flows = int(summary.get("total_flows") or 0)
    anomalous = int(summary.get("anomalous_sources") or 0)
    suspicious = int(summary.get("suspicious_sources") or 0)

    if total_flows == 0 and anomalous == 0 and suspicious == 0:
        return

    tbl = TrafficStats.__table__
    stmt = insert(tbl).values(
        user_id=user_id,
        period_start=period_start,
        total_flows=total_flows,
        anomalous_sources=anomalous,
        suspicious_sources=suspicious,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[tbl.c.user_id, tbl.c.period_start],
        set_={
            "total_flows": tbl.c.total_flows + stmt.excluded.total_flows,
            "anomalous_sources": tbl.c.anomalous_sources + stmt.excluded.anomalous_sources,
            "suspicious_sources": tbl.c.suspicious_sources + stmt.excluded.suspicious_sources,
        },
    )
    await db.execute(stmt)
    await db.commit()


_PG_TRUNC = {
    StatsGroupBy.hour: "hour",
    StatsGroupBy.day: "day",
    StatsGroupBy.week: "week",
}


async def get_traffic_timeseries(
    db: AsyncSession,
    user_id: int,
    group_by: StatsGroupBy,
    start: datetime,
    end: datetime,
) -> List[Dict[str, Any]]:
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    else:
        start = start.astimezone(timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    else:
        end = end.astimezone(timezone.utc)

    trunc = _PG_TRUNC[group_by]
    bucket = func.date_trunc(trunc, TrafficStats.period_start).label("bucket")

    stmt = (
        select(
            bucket,
            func.coalesce(func.sum(TrafficStats.total_flows), 0).label("total_flows"),
            func.coalesce(func.sum(TrafficStats.anomalous_sources), 0).label("anomalous_sources"),
            func.coalesce(func.sum(TrafficStats.suspicious_sources), 0).label("suspicious_sources"),
        )
        .where(
            TrafficStats.user_id == user_id,
            TrafficStats.period_start >= start,
            TrafficStats.period_start < end,
        )
        .group_by(bucket)
        .order_by(bucket)
    )

    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "bucket_start": row.bucket,
            "total_flows": int(row.total_flows),
            "anomalous_sources": int(row.anomalous_sources),
            "suspicious_sources": int(row.suspicious_sources),
        }
        for row in rows
    ]


def _span_for_group_by(group_by: StatsGroupBy) -> timedelta:
    if group_by == StatsGroupBy.hour:
        return timedelta(hours=48)
    if group_by == StatsGroupBy.day:
        return timedelta(days=30)
    return timedelta(weeks=12)


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def resolve_query_range(
    group_by: StatsGroupBy,
    from_ts: datetime | None,
    to_ts: datetime | None,
) -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    span = _span_for_group_by(group_by)

    if from_ts is not None and to_ts is not None:
        start, end = _ensure_utc(from_ts), _ensure_utc(to_ts)
    elif from_ts is not None:
        start = _ensure_utc(from_ts)
        end = start + span
    elif to_ts is not None:
        end = _ensure_utc(to_ts)
        start = end - span
    else:
        start, end = now - span, now

    return start, end
