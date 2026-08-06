from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_invitation_email(invitation_id):
    """Отправляет письмо с приглашением по ID приглашения."""
    from .models import Invitation
    try:
        invitation = Invitation.objects.get(id=invitation_id, accepted=False)

    except Invitation.DoesNotExist:
        return

    accept_url = f"http://localhost:8000/api/v1/invitations/{invitation.token}/memberships/"
    subject = f"Вас пригласили в рабочее пространство {invitation.workspace.name}"
    message = (
        f"Здравствуйте!\n\n"
        f"Вас пригласили присоединиться к рабочему пространству «{invitation.workspace.name}».\n"
        f"Перейдите по ссылке, чтобы принять приглашение: {accept_url}\n\n"
        f"Ссылку можно открыть только 1 раз!"
    )

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [invitation.email])
