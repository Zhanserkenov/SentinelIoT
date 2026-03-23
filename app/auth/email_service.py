import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL")


def _send_email_sync(to_email: str, subject: str, body: str) -> None:
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")


async def send_email(to_email: str, subject: str, body: str) -> None:
    await asyncio.to_thread(_send_email_sync, to_email, subject, body)


async def send_registration_code(email: str, code: str) -> None:
    subject = "Your Registration Code"
    body = f"""
    <html>
        <body>
            <h2>Complete Your Registration</h2>
            <p>Use this code to finish creating your account:</p>
            <p><strong>{code}</strong></p>
            <p>This code will expire in 3 minutes.</p>
            <p>If you did not request registration, please ignore this email.</p>
        </body>
    </html>
    """
    await send_email(email, subject, body)


async def send_password_reset(email: str, token: str) -> None:
    reset_url = f"{FRONTEND_URL}/auth/reset-password?token={token}"
    subject = "Password Reset Request"
    body = f"""
    <html>
        <body>
            <h2>Password Reset</h2>
            <p>You have requested to reset your password. Click the link below to reset it:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>This link will expire in 5 minutes.</p>
            <p>If you did not request a password reset, please ignore this email.</p>
        </body>
    </html>
    """
    await send_email(email, subject, body)

