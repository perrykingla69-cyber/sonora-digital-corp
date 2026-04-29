"""
UserJourneyTracker — tracks ABE Music user funnels and segment classification
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID
import redis

logger = logging.getLogger(__name__)

SEGMENTS = {
    "power_user": {"min_sessions": 10, "min_content_views": 50},
    "active": {"min_sessions": 3, "min_content_views": 10},
    "casual": {"min_sessions": 1, "min_content_views": 1},
    "churned": {"max_days_inactive": 30},
}

FUNNEL_STAGES = ["landing", "signup", "onboarding", "first_content", "engaged", "converted"]


class UserJourneyTracker:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.r = redis.from_url(redis_url, decode_responses=True)

    def track_event(self, tenant_id: str, user_id: str, event: str, metadata: Optional[Dict] = None):
        key = f"journey:{tenant_id}:{user_id}"
        entry = {"event": event, "ts": datetime.utcnow().isoformat(), "meta": metadata or {}}
        self.r.lpush(key, json.dumps(entry))
        self.r.ltrim(key, 0, 499)
        self.r.expire(key, 86400 * 90)

        stage_key = f"funnel:{tenant_id}:{user_id}"
        if event in FUNNEL_STAGES:
            idx = FUNNEL_STAGES.index(event)
            current = int(self.r.get(stage_key) or -1)
            if idx > current:
                self.r.set(stage_key, idx, ex=86400 * 90)

    def get_journey(self, tenant_id: str, user_id: str, limit: int = 50) -> List[Dict]:
        key = f"journey:{tenant_id}:{user_id}"
        raw = self.r.lrange(key, 0, limit - 1)
        return [json.loads(e) for e in raw]

    def classify_segment(self, tenant_id: str, user_id: str) -> str:
        events = self.get_journey(tenant_id, user_id, limit=200)
        if not events:
            return "new"

        sessions = len([e for e in events if e["event"] == "session_start"])
        content_views = len([e for e in events if e["event"] == "content_view"])
        last_ts = datetime.fromisoformat(events[0]["ts"])
        days_inactive = (datetime.utcnow() - last_ts).days

        if days_inactive > 30:
            return "churned"
        if sessions >= 10 and content_views >= 50:
            return "power_user"
        if sessions >= 3 and content_views >= 10:
            return "active"
        return "casual"

    def get_funnel_report(self, tenant_id: str, user_ids: List[str]) -> Dict:
        stage_counts = {s: 0 for s in FUNNEL_STAGES}
        for uid in user_ids:
            stage_key = f"funnel:{tenant_id}:{uid}"
            idx = int(self.r.get(stage_key) or -1)
            if idx >= 0:
                stage_counts[FUNNEL_STAGES[idx]] += 1

        total = len(user_ids)
        report = {}
        for i, stage in enumerate(FUNNEL_STAGES):
            count = stage_counts[stage]
            prev_count = stage_counts[FUNNEL_STAGES[i - 1]] if i > 0 else total
            conversion = round(count / prev_count * 100, 1) if prev_count > 0 else 0.0
            report[stage] = {"count": count, "conversion_pct": conversion}
        return {"funnel": report, "total_users": total}

    def get_segment_distribution(self, tenant_id: str, user_ids: List[str]) -> Dict:
        dist: Dict[str, int] = {}
        for uid in user_ids:
            seg = self.classify_segment(tenant_id, uid)
            dist[seg] = dist.get(seg, 0) + 1
        return dist
