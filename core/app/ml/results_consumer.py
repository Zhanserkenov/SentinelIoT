import json
import logging
from typing import Any, Dict, List

import aio_pika

from core.app.core.config import settings
from core.app.core.database import AsyncSessionLocal
from core.app.core.redis import get_redis
from core.app.suspicious.service import save_suspicious_packets

logger = logging.getLogger(__name__)


async def _handle_result_message(payload: Dict[str, Any]) -> None:
    user_id = int(payload["user_id"])
    result = payload["result"]
    suspicious_packets = payload.get("suspicious_packets", [])

    redis = get_redis()
    await redis.set(f"analysis_result:{user_id}", json.dumps(result), ex=3600)

    async with AsyncSessionLocal() as db:
        if suspicious_packets:
            await save_suspicious_packets(db, suspicious_packets, user_id)


async def consume_ml_results() -> None:
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue(settings.ML_RESULTS_QUEUE, durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process(requeue=False):
                try:
                    payload = json.loads(message.body.decode("utf-8"))
                    await _handle_result_message(payload)
                except Exception:
                    logger.exception("Failed to process ML result message")
