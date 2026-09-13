from django.urls import path
from ..views import RoadmapView

urlpatterns = [
    path(
        "roadmaps/<uuid:roadmap_id>/",
        RoadmapView.as_view(),
        name="roadmap_detail"
    )
]
