from pydantic import BaseModel, EmailStr

class AuthSchema(BaseModel):
    email: EmailStr
    password: str

class RegistrationCodeRequestSchema(BaseModel):
    email: EmailStr


class RegistrationCompleteSchema(BaseModel):
    email: EmailStr
    code: str
    password: str

class PasswordResetRequestSchema(BaseModel):
    email: EmailStr

class PasswordResetSchema(BaseModel):
    token: str
    new_password: str