from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.users.service import update_telegram_user_id
from app.users.schemas import TelegramUserIdUpdateRequest
from app.users.model import User
from app.core.security import get_current_user
from app.core.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.patch("/me/telegram-id")
async def update_telegram_user_id_api(
        request: TelegramUserIdUpdateRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    updated_user = await update_telegram_user_id(
        db=db,
        user_id=current_user.id,
        telegram_user_id=request.telegram_user_id
    )

    return {
        "message": "Telegram user ID updated successfully",
        "telegram_user_id": updated_user.telegram_user_id
    }

