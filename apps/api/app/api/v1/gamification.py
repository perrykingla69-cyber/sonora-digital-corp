from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..schemas.gamification import UserStats, Achievement, AchievementType, BadgeLevel, GamificationResponse
from ...db.session import get_db
from ...security import get_current_user

router = APIRouter(prefix="/gamification", tags=["gamification"])

@router.get("/stats")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> GamificationResponse:
    """Get user gamification stats: level, XP, badges, achievements"""

    # Mock implementation (real version queries DB)
    user_stats = UserStats(
        tenant_id=current_user.tenant_id,
        total_xp=2450,
        level=5,
        badges_earned=3,
        achievements=[
            Achievement(
                id="first_login",
                achievement_type=AchievementType.FIRST_LOGIN,
                title="Bienvenido",
                description="Primer acceso a HERMES",
                badge_level=BadgeLevel.BRONZE,
                xp_reward=50,
                icon_emoji="🎯"
            ),
            Achievement(
                id="compliance_100",
                achievement_type=AchievementType.COMPLIANCE_100,
                title="Cumplido 100 Días",
                description="100 días sin obligaciones vencidas",
                badge_level=BadgeLevel.SILVER,
                xp_reward=500,
                icon_emoji="✅",
                unlocked_at=datetime.utcnow() - timedelta(days=30)
            )
        ],
        streaks_active=7,
        referrals=2,
        compliance_score=0.98,
        last_action=datetime.utcnow(),
        rank_percentile=0.78
    )

    return GamificationResponse(
        user_stats=user_stats,
        next_milestone="Level 6 (500 XP remaining)",
        daily_bonus_available=True,
        reward_preview={"xp": 100, "bonus": "2x XP this weekend"}
    )

@router.post("/claim-daily-bonus")
async def claim_daily_bonus(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Claim daily login bonus"""
    return {
        "success": True,
        "xp_gained": 100,
        "bonus_message": "¡Excelente! +100 XP por acceso diario. Racha: 7 días 🔥"
    }

@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get top users by level and XP"""
    # Mock leaderboard
    return {
        "period": "this_month",
        "leaderboard": [
            {"rank": 1, "usuario": "contador_pro", "level": 12, "xp": 8900, "badges": 8},
            {"rank": 2, "usuario": "contador_gold", "level": 10, "xp": 7200, "badges": 6},
            {"rank": 3, "usuario": "contador_silver", "level": 9, "xp": 6100, "badges": 5}
        ]
    }

@router.get("/badges")
async def get_all_badges():
    """Get available badges (public)"""
    return {
        "badges": [
            {
                "id": "first_login",
                "name": "Bienvenida",
                "emoji": "🎯",
                "requirement": "Primer acceso",
                "xp": 50
            },
            {
                "id": "tax_master",
                "name": "Maestro Fiscal",
                "emoji": "👑",
                "requirement": "100 cálculos de impuestos",
                "xp": 1000,
                "rarity": "epic"
            },
            {
                "id": "referral_5",
                "name": "Embajador",
                "emoji": "🤝",
                "requirement": "Referir 5 clientes",
                "xp": 2000,
                "rarity": "legendary"
            }
        ]
    }
