import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    scan_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # e.g., "email_breach", "footprint", "permissions", "full_scan"
    
    target: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )  # e.g., email address, domain, or username
    
    status: Mapped[str] = mapped_column(
        String(20),
        default="completed",
        nullable=False
    )  # "pending", "completed", "failed"
    
    risk_level: Mapped[str] = mapped_column(
        String(20),
        default="clean",
        nullable=False
    )  # "clean", "low", "medium", "high", "critical"
    
    score_impact: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )  # Points deducted from privacy score
    
    summary: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False
    )
    
    findings_data: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    user = relationship("User", back_populates="scans")
