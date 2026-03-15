from pydantic import BaseModel, EmailStr

class AuthSchema(BaseModel):
    email: EmailStr
    password: str

class EmailConfirmationSchema(BaseModel):
    token: str

class PasswordResetRequestSchema(BaseModel):
    email: EmailStr

class PasswordResetSchema(BaseModel):
    token: str
    new_password: str