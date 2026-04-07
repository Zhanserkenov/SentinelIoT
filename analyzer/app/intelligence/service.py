import httpx
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Tuple, List
from analyzer.app.intelligence.core import ask_gemini
from core.app.users.model import User
from core.app.core.config import settings

cooldown_cache: dict[Tuple[int, str], float] = {}

async def send_telegram_msg(chat_id: str, text: str):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    async with httpx.AsyncClient(timeout=10) as http_client:
        await http_client.post(url, json=payload)

async def process_ai_anomaly_report(db: AsyncSession, user_id: int, alerts_to_dispatch: List[dict]):
    current_time = time.time()
    valid_alerts: List[dict] = []

    for alert in alerts_to_dispatch:
        cache_key = (user_id, alert["src_ip"])
        
        if cache_key in cooldown_cache:
            last_time = cooldown_cache[cache_key]
            if current_time - last_time < 3600:
                continue
        
        cooldown_cache[cache_key] = current_time
        valid_alerts.append(alert)

    if not valid_alerts:
        return

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.telegram_user_id:
        return

    alert_count = len(valid_alerts)
    prompt = f"""Analyze {alert_count} network anomalies detected simultaneously. This may be a coordinated attack.

"""
    
    for alert in valid_alerts:
        ip_type = alert.get("ip_type", "Unknown")
        src_ip = alert.get("src_ip", "Unknown")
        
        prompt += f"""Traffic source: {src_ip} ({ip_type} IP)
- Flow count: {alert.get('flow_count', 0)}
- Maximum attack probability: {alert.get('max_probability', 0.0):.2f}
- Average TTL (Time To Live): {alert.get('time_to_live', 0.0)}
- Average ACK flag: {alert.get('ack_flag_number', 0.0)}
- Average PSH flag: {alert.get('psh_flag_number', 0.0)}
- Average rate: {alert.get('rate', 0.0)}
- Variance: {alert.get('variance', 0.0)}

"""
    
    prompt += """Consider the IP address types:
- If IP is External: assess the risk of external scanning or coordinated attack from the internet
- If IP is Internal: assess the risk of device infection within the network or internal coordinated anomaly

Provide a brief professional assessment (3-4 sentences) about the nature of these anomalies, whether they indicate a coordinated attack, and recommended actions."""
    
    try:
        ai_response = await ask_gemini(prompt)

        if alert_count > 1:
            header = f"🚨 *Multiple Anomalies ({alert_count} IPs)*\n\n"
        else:
            header = "🚨 *Anomaly*\n\n"
        
        final_message = header + ai_response

        await send_telegram_msg(user.telegram_user_id, final_message)
    except Exception as e:
        print(f"Error processing AI anomaly report: {e}")
