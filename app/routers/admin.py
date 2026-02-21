from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import AuditLog, Candidate, ElectionConfig, Vote
from app.schemas.schemas import CandidateCreate, ElectionWindowUpdate
from app.services.auth import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/candidates")
def add_candidate(payload: CandidateCreate, _: object = Depends(require_admin), db: Session = Depends(get_db)):
    candidate = Candidate(name=payload.name, party_symbol=payload.party_symbol)
    db.add(candidate)
    db.commit()
    return {"message": "Candidate added", "candidate_id": candidate.id}


@router.put("/election-window")
def update_window(payload: ElectionWindowUpdate, _: object = Depends(require_admin), db: Session = Depends(get_db)):
    if payload.end_time <= payload.start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")

    config = db.query(ElectionConfig).first()
    if not config:
        config = ElectionConfig(start_time=payload.start_time, end_time=payload.end_time, is_active=payload.is_active)
        db.add(config)
    else:
        config.start_time = payload.start_time
        config.end_time = payload.end_time
        config.is_active = payload.is_active
    db.commit()
    return {"message": "Election window updated"}


@router.get("/stats")
def voting_stats(_: object = Depends(require_admin), db: Session = Depends(get_db)):
    stats = (
        db.query(Candidate.name, func.count(Vote.id).label("votes"))
        .outerjoin(Vote, Vote.candidate_id == Candidate.id)
        .group_by(Candidate.id)
        .all()
    )
    total = db.query(func.count(Vote.id)).scalar() or 0
    return {"total_votes": total, "candidate_stats": [{"name": n, "votes": v} for n, v in stats]}


@router.get("/audit-logs")
def audit_logs(_: object = Depends(require_admin), db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(500).all()
    return [
        {
            "user_id": row.user_id,
            "action": row.action,
            "ip_address": row.ip_address,
            "timestamp": row.timestamp.isoformat(),
        }
        for row in logs
    ]
