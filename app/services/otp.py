import random
import smtplib
from datetime import datetime
from email.message import EmailMessage

from app.core.config import settings


def generate_otp() -> str:
    return f"{random.randint(100000, 999999)}"


def send_otp_email(email: str, otp: str) -> None:
    if not settings.smtp_user or not settings.smtp_password:
        return
    msg = EmailMessage()
    msg["Subject"] = "Secure E-Voting OTP"
    msg["From"] = settings.smtp_sender
    msg["To"] = email
    msg.set_content(f"Your OTP is {otp}. It expires in 2 minutes.")

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)


def otp_timestamp() -> datetime:
    return datetime.utcnow()
