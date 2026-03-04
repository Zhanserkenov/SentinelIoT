from pydantic import BaseModel, field_validator
from typing import Optional


class TelegramUserIdSchema(BaseModel):
    telegram_user_id: Optional[str]




