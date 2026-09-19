from dataclasses import dataclass

def split_lore_into_pages(text: str) -> list[str]:
    """Делит единый текст лора узла на страницы"""
    if not text:
        return []
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return [page.strip() for page in text.split("\n\n") if page.strip()]


@dataclass(frozen=True)
class PassingPolicy:
    """Политика «пройдено» для узла.

    Узел пройден, только если все ответы правильные.
    """

    def is_passed(self, correct: int, total: int) -> bool:
        if total <= 0:
            return False
        return correct == total
