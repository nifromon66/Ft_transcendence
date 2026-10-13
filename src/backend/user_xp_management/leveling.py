"""Levels derived from cumulative XP, without a separate database column."""


def get_xp_progress(xp: int | None) -> dict[str, int]:
    """Thresholds: 0, 30, 100, 200, 350, 550, 800, ... XP.

    After level 3, each level costs 50 XP more than the previous.
    NULL or negative XP is treated as zero.
    """
    total = max(0, xp or 0)
    level, start, end = 1, 0, 30
    while total >= end:
        level += 1
        start = end
        end += 70 if level == 2 else 50 * (level - 1)
    return {
        "total": total,
        "level": level,
        "current": total - start,
        "required": end - start,
        "next_level_xp": end,
    }
