from django.urls import path

from . import views

urlpatterns = [
    path('workspaces/<int:workspace_id>/projects/', views.ProjectListCreateView.as_view(), name='project-list'),
    path('workspaces/<int:workspace_id>/projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:project_id>/members/', views.ProjectMemberCreateView.as_view(), name='project-member-create'),
]