# presentation/serializers/roadmap_serializers.py

from ..domain.entities import Node, Question, Roadmap


def roadmap_to_page_data(
    roadmap: Roadmap,
    progress_map: dict | None = None,
) -> dict:
    """
    Превращает доменную карту в структуру для JS-шаблона.

    Args:
        roadmap: доменная карта.
        progress_map: {node_id: UserNodeProgress} — прогресс пользователя.
    """
    progress_map = progress_map or {}

    nodes = []
    prev_passed = True  # первый узел всегда доступен

    for node in sorted(roadmap.points, key=lambda n: n.order):
        progress = progress_map.get(node.uid)
        nodes.append(node_to_js(node, progress, prev_passed))
        prev_passed = progress.is_passed if progress else False

    return {
        "uid": str(roadmap.uid),
        "title": roadmap.title,
        "nodes": nodes,
    }


def node_to_js(
    node: Node,
    user_progress=None,
    prev_passed: bool = False,
) -> dict:
    """Один узел в формате JS-объекта NODES[i].

    Статус определяется по прогрессу пользователя:
      - completed — узел пройден
      - active    — начат, но не пройден, ИЛИ доступен (предыдущий пройден)
      - locked    — недоступен (предыдущий не пройден)
    """
    revision = node.current_revision

    # ─── Статус и label ───
    status, status_label = _resolve_status(node, user_progress, prev_passed)

    return {
        "uid": str(node.uid),
        "title": _split_title(revision.title if revision else ""),
        "status": status,
        "statusLabel": status_label,
        "image": _image_url(node.background_image),
        "wave": node.wave,
        "modal": {
            "tag": revision.tag if revision else "",
            "chapter": revision.chapter if revision else "",
            "heading": _split_title(revision.title if revision else ""),
            "narrator": {
                "name": revision.narrator_name if revision else "",
                "role": revision.narrator_role if revision else "",
                "image": _image_url(node.background_image),
            },
            "pages": node.pages if revision else [],
        },
        "form": {
            "chapter": revision.chapter if revision else "",
            "mode": revision.mode if revision else "Самостоятельно",
            "title": revision.title if revision else "",
            "book": revision.book if revision else "",
            "xp": f"+{revision.xp} XP" if revision else "+0 XP",
            "task": revision.task if revision else "",
            "fields": [
                _question_to_field(q, i)
                for i, q in enumerate(node.questions, start=1)
            ],
        },
    }


# ─────────────────────────────────────────────────────
# Определение статуса
# ─────────────────────────────────────────────────────

def _resolve_status(
    node: Node,
    user_progress,
    prev_passed: bool,
) -> tuple[str, str]:
    """Возвращает (status, status_label).

    Приоритет:
      1. Пройден → completed
      2. Начат (есть попытки) → active
      3. Доступен (первый или предыдущий пройден) → active
      4. Иначе → locked
    """
    if user_progress and user_progress.is_passed:
        return "completed", "Пройдено"

    if user_progress and user_progress.attempts_count > 0:
        return "active", "В процессе"

    if prev_passed or node.order == 1:
        return "active", "Доступно"

    return "locked", "Скоро"


# ─────────────────────────────────────────────────────
# Хелперы
# ─────────────────────────────────────────────────────


def _split_title(title: str) -> str:
    """«Долина Первых Строк» → «Долина\\nПервых Строк» для JS."""
    parts = title.split(maxsplit=1)
    return "\n".join(parts) if len(parts) == 2 else title


def _status_to_js(status) -> str:
    return {
        "published": "completed",
        "draft": "active",
        "archived": "locked",
    }.get(str(status), "locked")


def _status_label(status) -> str:
    return {
        "published": "Пройдено",
        "draft": "В процессе",
        "archived": "Скоро",
    }.get(str(status), "—")


def _image_url(image_field) -> str:
    if not image_field:
        return ""
    return image_field.url


def _question_to_field(question: Question, num: int) -> dict:
    revision = question.current_revision
    return {
        "question_id": str(question.uid),
        "revision_id": str(revision.uid) if revision else None, 
        "num": f"{num:02d}",
        "label": revision.text[:60] if revision else f"Вопрос {num}",
        "hint": revision.text if revision else "",
        "type": "textarea",
        "placeholder": "Запиши свой ответ здесь…",
    }
