"""Avatar rewards are available according to the user's current level."""
from .leveling import get_xp_progress

AVATAR_REWARDS = (
    {"id": "bronze", "name": "Bronze", "required_level": 3},
    {"id": "silver", "name": "Argent", "required_level": 5},
    {"id": "gold", "name": "Or", "required_level": 15},
)
FRAME_LEVELS = {reward["id"]: reward["required_level"] for reward in AVATAR_REWARDS}


def get_active_frame(user):
    preference = user.avatar_frame_preference
    frame = preference.frame if preference else None
    if frame in FRAME_LEVELS and get_xp_progress(user.xp)["level"] >= FRAME_LEVELS[frame]:
        return frame
    return None


def get_level_rewards(user):
    level = get_xp_progress(user.xp)["level"]
    return [{**reward, "unlocked": level >= reward["required_level"]} for reward in AVATAR_REWARDS]
