import asyncio
import json
import logging
import os
from typing import Any, Dict, List

import aio_pika
from dotenv import load_dotenv

from analyzer.app.intelligence.service import process_ai_anomaly_report
from analyzer.app.ml.schemas import FlowFeatures
from analyzer.app.ml.service import analyze_window
from core.app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

load_dotenv()
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
ML_ANALYSIS_QUEUE = os.getenv("ML_ANALYSIS_QUEUE")
ML_RESULTS_QUEUE = os.getenv("ML_RESULTS_QUEUE")


async def _publish_result(channel: aio_pika.Channel, payload: Dict[str, Any]) -> None:
    queue = await channel.declare_queue(ML_RESULTS_QUEUE, durable=True)
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(payload).encode("utf-8"),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=queue.name,
    )


async def consume_analysis_tasks() -> None:
    while True:
        connection: aio_pika.RobustConnection | None = None
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=10)
            queue = await channel.declare_queue(ML_ANALYSIS_QUEUE, durable=True)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process(requeue=False):
                        try:
                            data = json.loads(message.body.decode("utf-8"))
                            user_id = int(data["user_id"])
                            flows_payload: List[Dict[str, Any]] = data.get("flows", [])
                            flows = [FlowFeatures(**item) for item in flows_payload]
                            result, suspicious_packets, alerts_to_dispatch = analyze_window(flows, user_id)

                            if alerts_to_dispatch:
                                async with AsyncSessionLocal() as db:
                                    await process_ai_anomaly_report(db, user_id, alerts_to_dispatch)

                            payload = {
                                "task_id": data.get("task_id"),
                                "user_id": user_id,
                                "result": result.model_dump(),
                                "suspicious_packets": suspicious_packets,
                            }
                            await _publish_result(channel, payload)
                        except Exception:
                            logger.exception("Failed to process ML analysis message")
        except asyncio.CancelledError:
            if connection:
                await connection.close()
            raise
        except Exception:
            logger.warning("ML worker lost RabbitMQ connection, retrying in 5 seconds")
            await asyncio.sleep(5)
