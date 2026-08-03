from django.urls import path
from . import views

urlpatterns = [
    path("", views.WorkspaceListCreateView.as_view(), name="workspace-list"),
    path("workspaces/<int:pk>/", views.WorkspaceDetailView.as_view(), name="workspace-detail"),
    path("workspaces/<int:workspace_id>/members/", views.MembershipCreateView.as_view(), name="membership-create"),
    path("workspaces/<int:workspace_id>/invitations/", views.InvitationCreateView.as_view(), name="invitation-create"),
]
