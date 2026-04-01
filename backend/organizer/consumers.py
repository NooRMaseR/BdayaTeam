from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .api_schemas import OrganizerBroudCast

class LiveMemberEditConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        self.track_name: str = self.scope['url_route']['kwargs']['track_name'].replace(' ', '_') # type: ignore
        self.group_name = f"organizer_live_member_edit_{self.track_name}"
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, code: int) -> None:
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    async def receive_json(self, content: OrganizerBroudCast, **kwargs: dict) -> None:
        if content:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "organizer_edit_member",
                    "data": content
                }
            )
    
    async def organizer_edit_member(self, data: dict) -> None:
        await self.send_json(data['data'])
    