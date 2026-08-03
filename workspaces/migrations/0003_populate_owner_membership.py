from django.db import migrations


def add_owner_memberships(apps, schema_editor):
    Workspace = apps.get_model('workspaces', 'Workspace')
    Membership = apps.get_model('workspaces', 'Membership')
    for ws in Workspace.objects.all():
        Membership.objects.get_or_create(
            workspace=ws,
            user=ws.owner,
            defaults={'role': 'admin'}
        )

class Migration(migrations.Migration):
    dependencies = [  # noqa: RUF012
        ('workspaces', '0002_rename_workspaces_workspace_invitation'),
    ]
    operations = [  # noqa: RUF012
        migrations.RunPython(add_owner_memberships, migrations.RunPython.noop),
    ]