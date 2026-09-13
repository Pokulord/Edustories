from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from uuid import UUID


from .infrastructure.repositories import RoadmapRepository
from .application.services import RoadmapService
from .domain.exceptions import RoadmapNotFoundError
from core.apps.users.infrastructure.repositories import DjangoUserRepository
from .presentation.serializers import roadmap_to_page_data

# Create your views here.


class RoadmapView(LoginRequiredMixin, View):
    """Вьюха для получения дорожной карты"""

    def get(self, request, roadmap_id: UUID):
        service = RoadmapService(
            roadmap_repo=RoadmapRepository(), user_repo=DjangoUserRepository()
        )

        try:
            roadmap = service.get_roadmap(roadmap_id)
        except RoadmapNotFoundError:
            raise Http404("Дорожная карта не найдена")

        roadmap_data = roadmap_to_page_data(roadmap)

        print(roadmap_data)

        return render(
            request, "roadmap.html", {"roadmap": roadmap, "roadmap_data": roadmap_data}
        )
