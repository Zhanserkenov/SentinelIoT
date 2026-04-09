import json

from redis.asyncio import Redis

from core.app.network.schemas import ConnectedDeviceIn, ConnectedDeviceOut

LATEST_SNAPSHOT_KEY = "network:user:{user_id}:latest_devices"


async def upsert_devices_snapshot(redis: Redis, user_id: int, devices: list[ConnectedDeviceIn]) -> int:
    unique = {}
    for dev in devices:
        mac = dev.mac.strip().lower()
        if mac:
            unique[mac] = dev

    snapshot = {
        "devices": [
            {"ip": dev.ip, "mac": mac}
            for mac, dev in unique.items()
        ],
    }
    await redis.set(LATEST_SNAPSHOT_KEY.format(user_id=user_id), json.dumps(snapshot))
    return len(unique)


async def get_online_devices(redis: Redis, user_id: int) -> list[ConnectedDeviceOut]:
    raw = await redis.get(LATEST_SNAPSHOT_KEY.format(user_id=user_id))
    if not raw:
        return []
    data = json.loads(raw)
    devices = data.get("devices", [])

    result = [
        ConnectedDeviceOut(
            ip=str(item.get("ip", "")),
            mac=str(item.get("mac", ""))
        )
        for item in devices
    ]
    return sorted(result, key=lambda d: d.mac)
