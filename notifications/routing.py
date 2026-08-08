from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'workspace/workspace/(?P<workspace_id>\d+)/$', consumers.WorkspaceConsumer.as_asgi()),
]
