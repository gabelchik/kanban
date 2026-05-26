from django.urls import path
from . import views

urlpatterns = [
    path("", views.WorkspaceListCreateView.as_view(), name="workspace-list"),
    path("<int:pk>/", views.WorkspaceDetailView.as_view(), name="workspace-detail"),
    path("<int:workspace_id>/members/", views.MembershipCreateView.as_view(), name="membership-create"),
]
