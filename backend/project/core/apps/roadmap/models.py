import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator

from .uploaders import node_background_upload_to
# Create your models here.


class Roadmap(models.Model):
    """Модель для дорожной карты"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Название"), max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Дорожная карта"
        verbose_name_plural = "Дорожные карты"

    def __str__(self):
        return f"{self.title}"


class Node(models.Model):
    """Модель для узла дорожной карты"""

    class NodeStatuses(models.TextChoices):
        PUBLISHED = "published", _("Опубликован")
        DRAFT = "draft", _("Черновик")
        ARCHIEVED = "archieved", _("Архивный")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    roadmap = models.ForeignKey(
        Roadmap,
        on_delete=models.CASCADE,
        related_name="nodes",
        verbose_name=_("Дорожная карта"),
    )
    order = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20, choices=NodeStatuses.choices, default=NodeStatuses.DRAFT
    )
    available_from = models.DateTimeField(null=True, blank=True)
    current_revision = models.OneToOneField(
        "NodeRevision",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_revision",
        verbose_name=_("Текущая ревизия"),
    )

    wave = models.FloatField(
        default=0.5,
        verbose_name=_("Высота на карте"),
        help_text=_("Позиция по вертикали: 0.0 — низ, 1.0 — верх"),
    )
    lore = models.TextField(
        _("Лор узла"),
        blank=True,
        help_text=_("Лор для узла. Каждая новая страница-отдельный абзац"),
    )
    background_image = models.ImageField(
        upload_to=node_background_upload_to, null=True, blank=True
    )

    class Meta:
        ordering = ("order",)
        unique_together = ("roadmap", "order")
        verbose_name = "Узел карты"
        verbose_name_plural = "Узлы карты"

    def __str__(self):
        title = self.current_revision.title if self.current_revision else "-"
        return f"{self.order}. {title}"


class NodeRevision(models.Model):
    """Модель для ревизий узлов"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="revisions",
        verbose_name=_("Узел"),
    )
    title = models.CharField(max_length=255)
    question_order = models.JSONField(
        default=list,
        help_text="Список UUID вопросов в порядке на момент ревизии",
        blank=True,
    )
    chapter = models.CharField(max_length=50, blank=True)
    tag = models.CharField(max_length=100, blank=True)
    book = models.CharField(max_length=255, blank=True)
    task = models.TextField(blank=True)
    xp = models.PositiveIntegerField(default=0)
    narrator_name = models.CharField(max_length=100, blank=True)
    narrator_role = models.CharField(max_length=150, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Ревизия узла"
        verbose_name_plural = "Ревизии узлов"


class Question(models.Model):
    """Модель для вопросов к узлам"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Вопрос к узлу",
    )
    order = models.PositiveIntegerField(default=1)
    current_revision = models.OneToOneField(
        "QuestionRevision",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_revision_for_question",
    )

    class Meta:
        ordering = ("order",)
        unique_together = ("node", "order")
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        text = self.current_revision.text[:50] if self.current_revision else "—"
        return f"{self.order}: {text}"


class QuestionRevision(models.Model):
    """Ревизия контента вопроса. Никогда не обновляется."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="revisions",
    )
    text = models.TextField()
    correct_answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Ревизия вопроса"
        verbose_name_plural = "Ревизии вопросов"

    def __str__(self):
        return f"{self.text[:40]}... ({self.created_at:%d.%m.%Y})"


class UserNodeProgress(models.Model):
    """Прогресс пользователя по узлу."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        related_name="node_progress",
        verbose_name=_("Пользователь")
    )
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="user_progress",
        verbose_name=_("Узел карты")
    )

    is_passed = models.BooleanField(_("Пройден"),default=False)
    correct_count = models.PositiveIntegerField(_("Количество правильных ответов"),
                                                default=0)
    total_count = models.PositiveIntegerField(default=0)
    attempts_count = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0, help_text=_("XP, начисленные при первом прохождении"))
    first_passed_at = models.DateTimeField(null=True, blank=True, help_text=_("Когда узел впервые пройден"))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "node")
        ordering = ("-updated_at",)
        verbose_name = "Прогресс по узлу"
        verbose_name_plural = "Прогресс по узлам"
        indexes = [
            models.Index(fields=["user", "is_passed"]),
        ]

    def __str__(self):
        status = "✓" if self.is_passed else "…"
        return f"{status} {self.user_id} / {self.node_id}"


    def apply_result(
    self,
    correct: int,
    total: int,
    xp: int,
    now,
    ) -> None:
        """
        Применяет результат попытки. Не сохраняет.

        Идемпотентно по is_passed: уже пройденный узел
        не сбрасывается при неудачной попытке.
        """
        self.correct_count = correct
        self.total_count = total
        self.attempts_count += 1

        was_passed = self.is_passed
        is_passed_now = self._evaluate_passed()

        if is_passed_now and not was_passed:
            # Первое прохождение — фиксируем
            self.is_passed = True
            self.first_passed_at = now
            self.xp_earned = xp

    def _evaluate_passed(self) -> bool:
        """Пересчитывает «пройдено» из счётчиков."""
        if self.total_count <= 0:
            return False
        return self.correct_count == self.total_count
