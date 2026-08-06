from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Project(models.Model):
    class Meta:
        ordering = ['-created_at']  # noqa: RUF012

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='projects'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.workspace.name})"


class ProjectMember(models.Model):
    class Meta:
        unique_together = ('project', 'user')

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_memberships'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} – {self.project.name} ({self.get_role_display()})"


class Board(models.Model):
    class Meta:
        ordering = ['created_at']

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='boards'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_boards'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.project.name})"


class Task(models.Model):
    class Meta:
        ordering = ['order']

    STATUS_CHOICES = (
        ('backlog', 'Backlog'),
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    )
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='backlog')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assignee = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )
    order = models.PositiveIntegerField(default=0)   # для сортировки внутри статуса
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
