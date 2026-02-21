from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    encrypted_face_embedding = Column(String, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)

    votes = relationship("Vote", back_populates="voter")


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint("voter_id", name="uq_vote_voter_id"),)

    id = Column(Integer, primary_key=True, index=True)
    voter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    receipt_hash = Column(String(64), nullable=False, index=True)

    voter = relationship("User", back_populates="votes")
    candidate = relationship("Candidate", back_populates="votes")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


class OTPSession(Base):
    __tablename__ = "otp_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    otp = Column(String(255), nullable=False)
    generation_time = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    party_symbol = Column(String(512), nullable=False)

    votes = relationship("Vote", back_populates="candidate")


class ElectionConfig(Base):
    __tablename__ = "election_config"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=False)
