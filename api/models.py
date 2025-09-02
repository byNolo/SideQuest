from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, JSON, Float, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    display_name: Mapped[str | None] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(255))
    privacy: Mapped[str] = mapped_column(String(16), default="public")
    prefs: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class QuestTemplate(Base):
    __tablename__ = "quest_templates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    body_template: Mapped[str] = mapped_column(String)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    constraints: Mapped[dict] = mapped_column(JSON, default=dict)
    rarity: Mapped[str] = mapped_column(String(16), default="common")

class Quest(Base):
    __tablename__ = "quests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[datetime] = mapped_column(Date)
    template_id: Mapped[int | None] = mapped_column(ForeignKey("quest_templates.id"))
    generated_context: Mapped[dict] = mapped_column(JSON, default=dict)
    weather_context: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(16), default="assigned")
    __table_args__ = (UniqueConstraint("user_id","date", name="uq_user_date"),)

class Submission(Base):
    __tablename__ = "submissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quest_id: Mapped[int] = mapped_column(ForeignKey("quests.id"), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    caption: Mapped[str | None] = mapped_column(String)
    media: Mapped[list] = mapped_column(JSON, default=list)
    exif_meta: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    score_cache: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Vote(Base):
    __tablename__ = "votes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"))
    voter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    criteria: Mapped[dict] = mapped_column(JSON)
    __table_args__ = (UniqueConstraint("submission_id","voter_id", name="uq_vote_once"),)
