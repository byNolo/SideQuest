from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import DateTime, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class QuestRarity(str, Enum):
    COMMON = "common"
    RARE = "rare"
    LEGENDARY = "legendary"


class QuestTemplate(Base):
    __tablename__ = "quest_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    rarity: Mapped[QuestRarity] = mapped_column(SQLEnum(QuestRarity), default=QuestRarity.COMMON, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Quest generation constraints and hints
    constraints: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    hints: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    
    # Weather and location requirements
    weather_conditions: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    location_types: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    
    # Time and difficulty estimates
    estimated_duration_minutes: Mapped[int | None] = mapped_column(Integer)
    difficulty_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1-5 scale
    
    # Template metadata
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    weight: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # Selection weight
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)