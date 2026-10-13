"""Levels derived from cumulative XP, without a separate database column."""


def get_xp_progress(xp: int | None) -> dict[str, int]:
    """Thresholds: 0, 30, 65, 105, 150, 200, 255, 315, 380, 450, ... XP.

    Each level costs 5 XP more than the previous, starting at 30 XP.
    Level 10 requires 450 XP, equivalent to 15 recipes at 30 XP each.
    NULL or negative XP is treated as zero.
    """
    total = max(0, xp or 0)
    level, start, end = 1, 0, 30
    while total >= end:
        level += 1
        start = end
        end += 30 + 5 * (level - 1)
    return {
        "total": total,
        "level": level,
        "current": total - start,
        "required": end - start,
        "next_level_xp": end,
    }
