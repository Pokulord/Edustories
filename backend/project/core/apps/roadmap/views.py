import json
from uuid import UUID

from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import JsonResponse

from .infrastructure.repositories import RoadmapRepository, QuestionRepository, UserNodeProgressRepository
from .application.services import AnswerService, RoadmapService, ProgressService
from .domain.exceptions import RoadmapNotFoundError
from core.apps.users.infrastructure.repositories import DjangoUserRepository
from .presentation.serializers import roadmap_to_page_data


# Create your views here.


class RoadmapView(LoginRequiredMixin, View):
    """GET — карта с прогрессом пользователя."""

    template_name = "roadmap.html"

    def get(self, request, roadmap_id: UUID):
        # ─── Сервисы ───
        roadmap_service = RoadmapService(
            roadmap_repo=RoadmapRepository(),
            user_repo=DjangoUserRepository(),
        )
        progress_service = ProgressService(
            progress_repo=UserNodeProgressRepository(),
        )

        # ─── Загрузка ───
        try:
            roadmap = roadmap_service.get_roadmap(roadmap_id)
        except RoadmapNotFoundError:
            raise Http404("Дорожная карта не найдена")

        progress_map = progress_service.get_progress_map(
            user_id=request.user.id,
            roadmap_id=roadmap_id,
        )
        total_xp = progress_service.get_total_xp(request.user.id)

        # ─── Сериализация ───
        roadmap_data = roadmap_to_page_data(roadmap, progress_map)

        print(roadmap_data)

        return render(request, self.template_name, {
            "roadmap": roadmap,
            "roadmap_data": roadmap_data,
            "total_xp": total_xp,
        })
    

class CheckAnswersView(LoginRequiredMixin, View):
    """POST — проверка ответов на узел."""

    def post(self, request, node_id: UUID):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        answers = data.get("answers", {})
        if not answers:
            return JsonResponse({"error": "Нет ответов"}, status=400)

        service = AnswerService(QuestionRepository())
        result = service.check_answers(
            node_id=node_id,
            answers=answers,
            user_id=request.user.id,
        )

        
        print(result)
        return JsonResponse(result)
