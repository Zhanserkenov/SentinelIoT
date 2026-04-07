import json
import uuid
from typing import Any, Dict, List

import aio_pika

from core.app.core.config import settings

async def publish_analysis_task(user_id: int, flows: List[Dict[str, Any]]) -> str:
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    task_id = str(uuid.uuid4())
    payload = {
        "task_id": task_id,
        "user_id": user_id,
        "flows": flows,
    }

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(settings.ML_ANALYSIS_QUEUE, durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(payload).encode("utf-8"),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=queue.name,
        )
    return task_id