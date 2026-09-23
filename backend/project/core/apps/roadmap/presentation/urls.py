from django.urls import path
from ..views import RoadmapView, CheckAnswersView

app_name = "roadmap"

urlpatterns = [
    path(
        "roadmaps/<uuid:roadmap_id>/",
        RoadmapView.as_view(),
        name="roadmap_detail"
    ),
    path(
    "nodes/<uuid:node_id>/check/",
    CheckAnswersView.as_view(),
    name="check_answers",
),
]
