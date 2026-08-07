from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_workspace_notification(workspace_id, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'workspace_{workspace_id}',
        {
            'type': 'workspace_message',
            'message': message
        }
    )