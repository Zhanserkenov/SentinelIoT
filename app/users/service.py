from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.users.model import User


async def update_telegram_user_id(db: AsyncSession, user_id: int, telegram_user_id: str) -> User:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    if telegram_user_id:
        existing_user_stmt = select(User).where(
            User.telegram_user_id == telegram_user_id,
            User.id != user_id
        )
        existing_user_result = await db.execute(existing_user_stmt)
        existing_user = existing_user_result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This Telegram user ID is already associated with another account"
            )

    user.telegram_user_id = telegram_user_id
    await db.commit()
    await db.refresh(user)

    return user

