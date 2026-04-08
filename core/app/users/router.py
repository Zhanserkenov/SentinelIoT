from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.app.core.security import get_current_user
from core.app.users.service import update_telegram_user_id, delete_user_profile, update_orange_pi_id
from core.app.users.schemas import TelegramUserIdSchema, OrangePiIdSchema
from core.app.users.model import User
from core.app.core.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me/telegram-id", response_model=TelegramUserIdSchema)
async def get_telegram_user_id_api(current_user: User = Depends(get_current_user)):
    return {
        "telegram_user_id": current_user.telegram_user_id
    }


@router.patch("/me/telegram-id", response_model=TelegramUserIdSchema)
async def update_telegram_user_id_api(
        request: TelegramUserIdSchema,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if request.telegram_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="telegram_user_id cannot be None"
        )

    updated_user = await update_telegram_user_id(
        db=db,
        user_id=current_user.id,
        telegram_user_id=request.telegram_user_id
    )

    return {
        "telegram_user_id": updated_user.telegram_user_id
    }


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_profile_api(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    await delete_user_profile(db=db, user_id=current_user.id)


@router.get("/me/orange-pi-id", response_model=OrangePiIdSchema)
async def get_orange_pi_id_api(current_user: User = Depends(get_current_user)):
    return {"orange_pi_id": current_user.orange_pi_id}


@router.patch("/me/orange-pi-id", response_model=OrangePiIdSchema)
async def update_orange_pi_id_api(
        request: OrangePiIdSchema,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not request.orange_pi_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="orange_pi_id cannot be empty"
        )
    updated_user = await update_orange_pi_id(db=db, user_id=current_user.id, orange_pi_id=request.orange_pi_id)
    return {"orange_pi_id": updated_user.orange_pi_id}