from pydantic import BaseModel


class TelegramUserIdUpdateRequest(BaseModel):
    telegram_user_id: str

