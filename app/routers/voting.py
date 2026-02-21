import hashlib
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Candidate, ElectionConfig, User, Vote
from app.schemas.schemas import VoteCreate
from app.services.audit import log_event
from app.services.auth import client_ip, get_current_user

router = APIRouter(prefix="/api/voting", tags=["voting"])


@router.get("/candidates")
def list_candidates(db: Session = Depends(get_db)):
    return db.query(Candidate).all()


@router.post("/cast")
def cast_vote(
    payload: VoteCreate,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    config = db.query(ElectionConfig).first()
    if not config or not config.is_active:
        raise HTTPException(status_code=403, detail="Election inactive")
    now = datetime.utcnow()
    if now < config.start_time or now > config.end_time:
        raise HTTPException(status_code=403, detail="Voting outside allowed window")

    if db.query(Vote).filter(Vote.voter_id == user.id).first():
        raise HTTPException(status_code=400, detail="One voter one vote policy")

    candidate = db.query(Candidate).filter(Candidate.id == payload.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    receipt_hash = hashlib.sha256(f"{user.id}-{datetime.utcnow().isoformat()}".encode()).hexdigest()
    vote = Vote(voter_id=user.id, candidate_id=candidate.id, receipt_hash=receipt_hash)
    db.add(vote)
    db.commit()
    log_event(db, user.id, "vote_cast", client_ip(request))
    return {
        "message": "Vote recorded anonymously",
        "receipt_hash": receipt_hash,
        "recorded_at": vote.timestamp.isoformat(),
    }
