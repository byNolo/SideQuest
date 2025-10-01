"""
Quest and related models for daily quests.
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, JSON, Float, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database import Base


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
    
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_user_date"),)