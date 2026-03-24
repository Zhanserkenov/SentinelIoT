from pydantic import BaseModel
from typing import Optional


class TelegramUserIdSchema(BaseModel):
    telegram_user_id: Optional[str]