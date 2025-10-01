"""
Submission and related models for quest submissions and voting.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON, Float, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database import Base


class Submission(Base):
    __tablename__ = "submissions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quest_id: Mapped[int] = mapped_column(ForeignKey("quests.id"), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    caption: Mapped[str | None] = mapped_column(Text)
    media: Mapped[list] = mapped_column(JSON, default=list)
    exif_meta: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending | visible | flagged | removed
    score_cache: Mapped[float | None] = mapped_column(Float)
    ratings_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Vote(Base):
    __tablename__ = "votes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"))
    voter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    criteria: Mapped[dict] = mapped_column(JSON)  # {effort, creativity, execution}
    comment: Mapped[str | None] = mapped_column(Text)
    total: Mapped[float | None] = mapped_column(Float)  # computed/generated column
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint("submission_id", "voter_id", name="uq_vote_once"),)