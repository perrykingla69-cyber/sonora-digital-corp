from __future__ import annotations
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class AchievementType(str, Enum):
    FIRST_LOGIN = "first_login"
    FIRST_INVOICE = "first_invoice"
    COMPLIANCE_100 = "compliance_100_days"
    TAX_MASTER = "tax_master"
    REFERRAL_5 = "referral_5"
    STREAKER_7 = "streaker_7_days"
    POWER_USER = "power_user"

class BadgeLevel(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

class UserLevel(BaseModel):
    level: int = Field(1, ge=1, le=100)
    experience_points: int = Field(0, ge=0)
    next_level_xp: int = Field(100, ge=100)
    progress_percent: float = Field(0.0, ge=0, le=100)

class Achievement(BaseModel):
    id: str
    achievement_type: AchievementType
    title: str
    description: str
    badge_level: BadgeLevel
    xp_reward: int
    icon_emoji: str
    unlocked_at: Optional[datetime] = None
    rarity: str = Field("common")  # common, rare, epic, legendary

class UserStats(BaseModel):
    tenant_id: str
    total_xp: int = 0
    level: int = 1
    badges_earned: int = 0
    achievements: list[Achievement] = []
    streaks_active: int = 0
    referrals: int = 0
    compliance_score: float = 1.0
    last_action: Optional[datetime] = None
    rank_percentile: float = 0.0

class GamificationResponse(BaseModel):
    user_stats: UserStats
    next_milestone: Optional[str] = None
    daily_bonus_available: bool = False
    reward_preview: Optional[dict] = None
