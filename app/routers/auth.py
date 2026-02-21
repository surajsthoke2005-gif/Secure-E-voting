import hashlib
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import OTPSession, User
from app.schemas.schemas import OTPVerify, UserCreate, UserLogin
from app.services.audit import log_event
from app.services.auth import client_ip
from app.services.otp import generate_otp, otp_timestamp, send_otp_email
from app.services.security import (
    create_access_token,
    decrypt_embedding,
    encrypt_embedding,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


def _csrf_ok(request: Request) -> bool:
    cookie_token = request.cookies.get("csrf_token")
    header_token = request.headers.get("X-CSRF-Token")
    return bool(cookie_token and header_token and secrets.compare_digest(cookie_token, header_token))


@router.post("/csrf")
def issue_csrf(response: Response):
    token = secrets.token_urlsafe(32)
    response.set_cookie("csrf_token", token, httponly=False, secure=False, samesite="lax")
    return {"csrf_token": token}


@router.post("/register")
def register(payload: UserCreate, request: Request, db: Session = Depends(get_db)):
    if not _csrf_ok(request):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        encrypted_face_embedding=encrypt_embedding(payload.face_embedding),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    log_event(db, user.id, "register_success", client_ip(request))
    return {"message": "Registered successfully"}


@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, payload: UserLogin, db: Session = Depends(get_db)):
    if not _csrf_ok(request):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

    user = db.query(User).filter(User.email == payload.email).first()
    ip = client_ip(request)
    if not user or not verify_password(payload.password, user.password_hash):
        log_event(db, user.id if user else None, "login_failed_password", ip)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not payload.blink_detected:
        log_event(db, user.id, "login_failed_liveness", ip)
        raise HTTPException(status_code=401, detail="Blink liveness not detected")

    stored_embedding = decrypt_embedding(user.encrypted_face_embedding)
    distance = sum((a - b) ** 2 for a, b in zip(stored_embedding, payload.face_embedding)) ** 0.5
    if distance > 0.45:
        log_event(db, user.id, "login_failed_face", ip)
        raise HTTPException(status_code=401, detail="Face mismatch")

    otp = generate_otp()
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()
    otp_row = db.query(OTPSession).filter(OTPSession.user_id == user.id).first()
    if not otp_row:
        otp_row = OTPSession(user_id=user.id, otp=otp_hash, generation_time=otp_timestamp(), used=False)
        db.add(otp_row)
    else:
        otp_row.otp = otp_hash
        otp_row.generation_time = datetime.utcnow()
        otp_row.used = False
    db.commit()
    send_otp_email(user.email, otp)
    log_event(db, user.id, "login_password_face_passed", ip)
    return {"message": "OTP sent"}


@router.post("/verify-otp")
def verify_otp(payload: OTPVerify, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    otp_row = db.query(OTPSession).filter(OTPSession.user_id == user.id).first()
    if not otp_row:
        raise HTTPException(status_code=400, detail="OTP not generated")
    if otp_row.used:
        raise HTTPException(status_code=400, detail="OTP already used")
    if datetime.utcnow() > otp_row.generation_time + timedelta(minutes=2):
        raise HTTPException(status_code=400, detail="OTP expired")

    incoming = hashlib.sha256(payload.otp.encode()).hexdigest()
    if incoming != otp_row.otp:
        log_event(db, user.id, "otp_failed", client_ip(request))
        raise HTTPException(status_code=401, detail="Invalid OTP")

    otp_row.used = True
    db.commit()
    token = create_access_token(user.email)
    log_event(db, user.id, "login_success", client_ip(request))
    return {"access_token": token, "token_type": "bearer"}
