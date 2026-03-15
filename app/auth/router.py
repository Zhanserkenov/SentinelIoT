from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import (
    register_user, 
    login_user, 
    confirm_email, 
    request_password_reset, 
    reset_password
)
from app.auth.schemas import (
    AuthSchema, 
    EmailConfirmationSchema,
    PasswordResetRequestSchema, 
    PasswordResetSchema
)
from app.core.database import get_db
from app.core.security import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: AuthSchema, db: AsyncSession = Depends(get_db)):
    user = await register_user(db, user_data.email, user_data.password)

    return {
        "message": "User registered successfully. Please check your email to confirm your account.",
        "user_id": user.id
    }

@router.post("/login")
async def login(user_data: AuthSchema, db: AsyncSession = Depends(get_db)):
    user = await login_user(db, user_data.email, user_data.password)
    access_token = create_access_token({"sub": str(user.id), "role": user.role})

    return {
        "message": "User logged in",
        "access_token": access_token
    }

@router.post("/confirm-email")
async def confirm_email_endpoint(
    confirmation_data: EmailConfirmationSchema, 
    db: AsyncSession = Depends(get_db)
):
    user = await confirm_email(db, confirmation_data.token)
    return {
        "message": "Email confirmed successfully",
        "user_id": user.id
    }

@router.post("/request-password-reset")
async def request_password_reset_endpoint(
    request_data: PasswordResetRequestSchema, 
    db: AsyncSession = Depends(get_db)
):
    await request_password_reset(db, request_data.email)
    return {
        "message": "If the email exists, a password reset link has been sent."
    }

@router.post("/reset-password")
async def reset_password_endpoint(
    reset_data: PasswordResetSchema, 
    db: AsyncSession = Depends(get_db)
):
    user = await reset_password(db, reset_data.token, reset_data.new_password)
    return {
        "message": "Password reset successfully",
        "user_id": user.id
    }