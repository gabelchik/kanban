import uuid
from django.db import models
from accounts.models import User
from django.conf import settings
from django.core.mail import send_mail


class Workspace(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_workspaces'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Membership(models.Model):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("member", "Member"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="member"
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "workspace")

    def __str__(self):
        return f"{self.user.email} - {self.workspace.name} ({self.get_role_display()})"


class Invitation(models.Model):
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="invitations"
    )
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4(), unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Приглашение {self.email} в {self.workspace.name}"

    def send_invitation_email(self, request=None):
        """Отправляет приглашение по email. Пока что локально в терминал,
        позже можно заменить на Celery-задачу"""

        accept_url = f"http://localhost:8000/api/v1/invitations/{self.token}/memberships/"
        subject = f"Вас пригласили в рабочее пространство {self.workspace.name}"
        message = (
            f"Здравствуйте!\n\n"
            f"Вас пригласили присоединиться к рабочему пространству «{self.workspace.name}»\n"
            f"Перейдите по ссылке, чтобы принять приглашение: {accept_url}\n\n"
            f"Ссылка можно открыть только 1 раз!"
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [self.email]
        send_mail(subject, message, from_email, recipient_list)
