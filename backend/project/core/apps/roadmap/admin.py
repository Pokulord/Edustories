from django.contrib import admin
from django.db.models import Count, Prefetch
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    Node,
    NodeRevision,
    Question,
    QuestionRevision,
    Roadmap,
)

# ─────────────────────────────────────────────────────────────
# Inlines
# ─────────────────────────────────────────────────────────────

class NodeRevisionInline(admin.TabularInline):
    """Ревизии узла — показываем прямо внутри Node."""

    model = NodeRevision
    extra = 0
    fields = ("id", "title", "created_at", "question_order")
    readonly_fields = ("id", "created_at")
    show_change_link = True
    classes = ("collapse",)


class QuestionRevisionInline(admin.TabularInline):
    """Ревизии вопроса — показываем внутри Question."""

    model = QuestionRevision
    extra = 0
    fields = ("id", "text", "correct_answer", "created_at")
    readonly_fields = ("id", "created_at")
    show_change_link = True


class QuestionInline(admin.StackedInline):
    """Вопросы внутри узла."""

    model = Question
    extra = 0
    fields = ("id", "order", "current_revision")
    readonly_fields = ("id",)
    show_change_link = True
    autocomplete_fields = ("current_revision",)


class NodeInline(admin.StackedInline):
    """Узлы внутри дорожной карты."""

    model = Node
    extra = 0
    fields = ("id", "order", "status", "available_from", "current_revision", "background_image")
    readonly_fields = ("id",)
    show_change_link = True
    autocomplete_fields = ("current_revision",)


# ─────────────────────────────────────────────────────────────
# Roadmap
# ─────────────────────────────────────────────────────────────

@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ("title", "nodes_count", "created_at", "updated_at")
    search_fields = ("title",)
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [NodeInline]

    fieldsets = (
        (None, {
            "fields": ("id", "title"),
        }),
        (_("Даты"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_nodes_count=Count("nodes"))

    @admin.display(description=_("Узлов"), ordering="_nodes_count")
    def nodes_count(self, obj):
        return obj._nodes_count


# ─────────────────────────────────────────────────────────────
# Node
# ─────────────────────────────────────────────────────────────

@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "short_title",
        "roadmap",
        "status",
        "available_from",
        "has_image",
        "created_revisions_count",
    )
    list_filter = ("status", "roadmap", "available_from")
    search_fields = ("current_revision__title", "roadmap__title")
    ordering = ("roadmap", "order")
    list_select_related = ("roadmap", "current_revision")
    autocomplete_fields = ("roadmap", "current_revision")
    readonly_fields = ("id", "image_preview")
    inlines = [QuestionInline, NodeRevisionInline]

    fieldsets = (
        (None, {
            "fields": ("id", "roadmap", "order", "status", "available_from"),
        }),
        (_("Текущая ревизия"), {
            "fields": ("current_revision",),
        }),
        (_("Изображение"), {
            "fields": ("background_image", "image_preview"),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("roadmap", "current_revision").annotate(
            _revisions_count=Count("revisions", distinct=True)
        )

    @admin.display(description=_("Название"), ordering="current_revision__title")
    def short_title(self, obj):
        if not obj.current_revision:
            return "—"
        title = obj.current_revision.title
        return title[:60] + ("…" if len(title) > 60 else "")

    @admin.display(description=_("Есть изображение"), boolean=True)
    def has_image(self, obj):
        return bool(obj.background_image)

    @admin.display(description=_("Ревизий"), ordering="_revisions_count")
    def created_revisions_count(self, obj):
        return obj._revisions_count

    @admin.display(description=_("Превью"))
    def image_preview(self, obj):
        if not obj.background_image:
            return "—"
        return format_html(
            '<img src="{}" style="max-height: 200px; max-width: 300px; border-radius: 6px;" />',
            obj.background_image.url,
        )


# ─────────────────────────────────────────────────────────────
# NodeRevision
# ─────────────────────────────────────────────────────────────

@admin.register(NodeRevision)
class NodeRevisionAdmin(admin.ModelAdmin):
    list_display = ("id", "node", "title", "created_at")
    list_filter = ("created_at", "node__roadmap")
    search_fields = ("title", "node__roadmap__title")
    ordering = ("-created_at",)
    list_select_related = ("node", "node__roadmap")
    autocomplete_fields = ("node",)
    readonly_fields = ("id", "created_at")

    fieldsets = (
        (None, {
            "fields": ("id", "node", "title"),
        }),
        (_("Порядок вопросов"), {
            "fields": ("question_order",),
            "description": _("Список UUID вопросов в порядке на момент ревизии."),
        }),
        (_("Дата"), {
            "fields": ("created_at",),
        }),
    )

    def save_model(self, request, obj, form, change):
        # Заполняем перед сохранением
        if not obj.question_order and obj.node_id:
            obj.question_order = [
                str(qid) for qid in (
                    obj.node.questions
                    .order_by("order")
                    .values_list("id", flat=True)
                )
            ]
        super().save_model(request, obj, form, change)


# ─────────────────────────────────────────────────────────────
# Question
# ─────────────────────────────────────────────────────────────

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("order", "short_text", "node", "roadmap_link")
    list_filter = ("node__roadmap",)
    search_fields = ("current_revision__text", "node__current_revision__title")
    ordering = ("node", "order")
    list_select_related = ("node", "node__roadmap", "current_revision")
    autocomplete_fields = ("node", "current_revision")
    readonly_fields = ("id",)
    inlines = [QuestionRevisionInline]

    fieldsets = (
        (None, {
            "fields": ("id", "node", "order"),
        }),
        (_("Текущая ревизия"), {
            "fields": ("current_revision",),
        }),
    )

    @admin.display(description=_("Текст"))
    def short_text(self, obj):
        if not obj.current_revision:
            return "—"
        text = obj.current_revision.text
        return text[:80] + ("…" if len(text) > 80 else "")

    @admin.display(description=_("Дорожная карта"), ordering="node__roadmap__title")
    def roadmap_link(self, obj):
        return obj.node.roadmap.title


# ─────────────────────────────────────────────────────────────
# QuestionRevision
# ─────────────────────────────────────────────────────────────

@admin.register(QuestionRevision)
class QuestionRevisionAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "short_text", "correct_answer", "created_at")
    list_filter = ("created_at", "question__node__roadmap")
    search_fields = ("text", "correct_answer")
    ordering = ("-created_at",)
    list_select_related = ("question", "question__node")
    autocomplete_fields = ("question",)
    readonly_fields = ("id", "created_at")

    fieldsets = (
        (None, {
            "fields": ("id", "question", "text", "correct_answer"),
        }),
        (_("Дата"), {
            "fields": ("created_at",),
        }),
    )

    @admin.display(description=_("Текст"))
    def short_text(self, obj):
        return obj.text[:60] + ("…" if len(obj.text) > 60 else "")