from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from .location import Location


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(String(500))
    avatar_url: Mapped[str | None] = mapped_column(String(512))
    privacy: Mapped[str] = mapped_column(String(16), default="public", nullable=False)

    prefs: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    quest_preferences: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    default_lat: Mapped[float | None] = mapped_column(Float)
    default_lon: Mapped[float | None] = mapped_column(Float)
    default_location_name: Mapped[str | None] = mapped_column(String(255))
    location_radius_km: Mapped[float] = mapped_column(Float, default=2.0, nullable=False)

    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    onboarding_step: Mapped[str | None] = mapped_column(String(32))

    webpush_endpoint: Mapped[str | None] = mapped_column(String(512))
    webpush_keys: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime)

    locations: Mapped[list["Location"]] = relationship(
        "Location", back_populates="user", cascade="all, delete-orphan"
    )

    def mark_active(self) -> None:
        self.last_active_at = datetime.utcnow()
