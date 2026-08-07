import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class WorkspaceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.workspace_id = self.scope['url_route']['kwargs']['workspace_id']
        self.room_group_name = f'workspace_{self.workspace_id}'
        user = self.scope['user']
        print(f"DEBUG: user.is_anonymous={user.is_anonymous}, user.id={getattr(user, 'id', None)}")

        if user.is_anonymous:
            print("DEBUG: Rejected because anonymous")
            await self.close()
            return

        is_member = await self.is_member(user.id, self.workspace_id)
        print(f"DEBUG: is_member={is_member}")
        if not is_member:
            print("DEBUG: Rejected because not member")
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def workspace_message(self, event):
        await self.send(text_data=json.dumps(event['message'], ensure_ascii=False))

    @database_sync_to_async
    def is_member(self, user_id, workspace_id):
        from workspaces.models import Membership
        return Membership.objects.filter(workspace_id=workspace_id, user_id=user_id).exists()