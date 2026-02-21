from sqlalchemy.orm import Session

from app.models.models import AuditLog


def log_event(db: Session, user_id: int | None, action: str, ip_address: str) -> None:
    db.add(AuditLog(user_id=user_id, action=action, ip_address=ip_address))
    db.commit()
