from django.urls import path

from . import views

urlpatterns = [
    path('workspaces/<int:workspace_id>/projects/', views.ProjectListCreateView.as_view(), name='project-list'),
    path('workspaces/<int:workspace_id>/projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:project_id>/members/', views.ProjectMemberCreateView.as_view(), name='project-member-create'),
    path('projects/<int:project_id>/boards/', views.BoardListCreateView.as_view(), name='board-list'),
    path('projects/<int:project_id>/boards/<int:pk>/', views.BoardDetailView.as_view(), name='board-detail'),
    path('boards/<int:board_id>/tasks/', views.TaskListCreateView.as_view(), name='task-list'),
    path('boards/<int:board_id>/tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
]