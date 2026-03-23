import secrets
from pydantic import EmailStr
from sqlalchemy import select
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.users.model import User
from app.core.security import create_access_token, get_user_from_token_payload
from app.auth.email_service import send_registration_code, send_password_reset
from app.core.redis import get_redis
from app.core.security import verify_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
REGISTRATION_CODE_TTL_SECONDS = 180

def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)

async def register_user(db: AsyncSession, email: EmailStr, code: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    code_key = _registration_code_key(str(email))
    redis = get_redis()
    stored_code = await redis.get(code_key)
    if stored_code is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code is invalid or expired"
        )

    if stored_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code is invalid or expired"
        )

    hashed_password = get_hashed_password(password)
    user = User(email=str(email), password=hashed_password)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    await redis.delete(code_key)

    return user


def _registration_code_key(email: str) -> str:
    return f"registration_code:{email.lower()}"


def _generate_registration_code() -> str:
    return f"{secrets.randbelow(1000000):06d}"


async def send_registration_email_code(db: AsyncSession, email: EmailStr) -> None:
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    code = _generate_registration_code()
    redis = get_redis()
    await redis.setex(_registration_code_key(str(email)), REGISTRATION_CODE_TTL_SECONDS, code)
    await send_registration_code(str(email), code)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

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

    user = await get_user_from_token_payload(db, payload, "password_reset")

    hashed_password = get_hashed_password(new_password)
    user.password = hashed_password
    await db.commit()
    await db.refresh(user)

    return user