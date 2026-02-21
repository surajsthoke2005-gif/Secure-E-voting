from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    face_embedding: list[float]


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    face_embedding: list[float]
    blink_detected: bool


class OTPVerify(BaseModel):
    email: EmailStr
    otp: str


class CandidateCreate(BaseModel):
    name: str
    party_symbol: str


class VoteCreate(BaseModel):
    candidate_id: int


class ElectionWindowUpdate(BaseModel):
    start_time: datetime
    end_time: datetime
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
