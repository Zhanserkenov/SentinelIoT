from pydantic import EmailStr
from sqlalchemy import select
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.users.model import User
from app.core.security import create_access_token
from app.auth.email_service import send_email_confirmation, send_password_reset
from app.core.security import verify_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)

async def register_user(db: AsyncSession, email: EmailStr, password: str):
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    hashed_password = get_hashed_password(password)
    user = User(email = str(email), password = hashed_password, email_verified = False)

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Generate confirmation token (5 minutes)
    confirmation_token = create_access_token(
        {"sub": str(user.id), "type": "email_confirmation"},
        expires_delta=timedelta(minutes=5)
    )

    await send_email_confirmation(str(email), confirmation_token)

    return user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def _get_user_from_token(
    db: AsyncSession, 
    payload: dict, 
    expected_token_type: str
) -> User:
    token_type = payload.get("type")
    if token_type != expected_token_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type"
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

async def login_user(db: AsyncSession, email: EmailStr, password: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password"
        )

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password"
        )

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified. Please check your email for confirmation link."
        )

    return user

async def confirm_email(db: AsyncSession, token: str):
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    user = await _get_user_from_token(db, payload, "email_confirmation")

    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )

    user.email_verified = True
    await db.commit()
    await db.refresh(user)

    return user

async def request_password_reset(db: AsyncSession, email: EmailStr):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return

    reset_token = create_access_token(
        {"sub": str(user.id), "type": "password_reset"},
        expires_delta=timedelta(minutes=5)
    )

    await send_password_reset(str(email), reset_token)

async def reset_password(db: AsyncSession, token: str, new_password: str):
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    user = await _get_user_from_token(db, payload, "password_reset")

    hashed_password = get_hashed_password(new_password)
    user.password = hashed_password
    await db.commit()
    await db.refresh(user)

    return user