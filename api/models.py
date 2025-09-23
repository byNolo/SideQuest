from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, JSON, Float, UniqueConstraint, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    display_name: Mapped[str | None] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(String(255))
    privacy: Mapped[str] = mapped_column(String(16), default="public")  # public | friends_only
    # Preferences: willing_to_spend, max_spend_daily, max_spend_weekly, max_time_minutes, travel_radius_km, default_location, delivery_windows
    prefs: Mapped[dict] = mapped_column(JSON, default=dict)
    webpush_endpoint: Mapped[str | None] = mapped_column(String(512))
    webpush_keys: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime)

class QuestTemplate(Base):
    __tablename__ = "quest_templates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    body_template: Mapped[str] = mapped_column(Text)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    constraints: Mapped[dict] = mapped_column(JSON, default=dict)
    requires_place: Mapped[bool] = mapped_column(Boolean, default=False)
    rarity: Mapped[str] = mapped_column(String(16), default="common")  # common | rare | legendary
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Quest(Base):
    __tablename__ = "quests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[datetime] = mapped_column(Date)
    template_id: Mapped[int | None] = mapped_column(ForeignKey("quest_templates.id"))
    seed: Mapped[str | None] = mapped_column(String(64))  # for reproducible mods
    generated_context: Mapped[dict] = mapped_column(JSON, default=dict)
    weather_context: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(16), default="assigned")  # assigned | submitted | missed
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime)
    __table_args__ = (UniqueConstraint("user_id","date", name="uq_user_date"),)

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
    __table_args__ = (UniqueConstraint("submission_id","voter_id", name="uq_vote_once"),)

class Friendship(Base):
    __tablename__ = "friendships"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    friend_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending | accepted | blocked
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Location(Base):
    __tablename__ = "locations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    precision_m: Mapped[float | None] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(16))  # browser | manual
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Streak(Base):
    __tablename__ = "streaks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_quest_date: Mapped[datetime | None] = mapped_column(Date)

class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(32))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False)
    channel: Mapped[str] = mapped_column(String(16))  # webpush | email | inapp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime)

class LeaderboardSnapshot(Base):
    __tablename__ = "leaderboard_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    period: Mapped[str] = mapped_column(String(16))  # lifetime | yearly | monthly
    year: Mapped[int | None] = mapped_column(Integer)
    month: Mapped[int | None] = mapped_column(Integer)
    scores: Mapped[dict] = mapped_column(JSON, default=dict)  # [{user_id, score, rank, submissions, avg_score, streak}]
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ModerationFlag(Base):
    __tablename__ = "moderation_flags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"))
    reporter_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(16), default="open")  # open | resolved
    signals: Mapped[dict | None] = mapped_column(JSON)  # heuristics snapshot
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)
