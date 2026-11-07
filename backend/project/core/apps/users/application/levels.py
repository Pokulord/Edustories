from dataclasses import dataclass

XP_PER_LEVEL = 1000


@dataclass(frozen=True, slots=True)
class LevelInfo:
    """DTO для данных об уровне"""
    level: int
    xp_in_level: int
    xp_to_next_level: int
    progress_percent: int
    xp_in_next_level: int = XP_PER_LEVEL


def calculate_level_info(total_xp: int) -> LevelInfo:
    """Уровень, прогресс внутри него и остаток до следующего."""
    level = max(1, total_xp // XP_PER_LEVEL)
    xp_in_level = total_xp % XP_PER_LEVEL
    return LevelInfo(
        level=level,
        xp_in_level=xp_in_level,
        xp_to_next_level=XP_PER_LEVEL - xp_in_level,
        progress_percent=int(xp_in_level * 100 / XP_PER_LEVEL),
    )
