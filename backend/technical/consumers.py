from channels.generic.websocket import AsyncJsonWebsocketConsumer
from organizer.api_schemas import OrganizerBroudCast

class LiveMemberEditConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        track_name: str = self.scope['url_route']['kwargs']['track_name'].replace(' ', '_') # type: ignore
        self.current_username = self.scope['user'].username # type: ignore
        self.group_name = f"technical_live_member_edit_{track_name}"
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, code: int) -> None:
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    async def receive_json(self, content: OrganizerBroudCast, **kwargs: dict) -> None:
        if content:
            content['data']['by'] = self.current_username
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "technical_edit_member",
                    "data": content
                }
            )
    
    async def technical_edit_member(self, data: dict) -> None:
        await self.send_json(data['data'])
    

class OnlineTechnicalTaskConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        track_name: str = self.scope['url_route']['kwargs']['track_name'].replace(' ', '_') # type: ignore
        self.group_name = f"technical_live_member_tasks_opened_{track_name}"
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, code: int) -> None:
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    async def receive_json(self, content: OrganizerBroudCast, **kwargs: dict) -> None:
        if content:
            content['viewer'] = self.scope['user'].username # type: ignore            
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "technical_member_task_live",
                    "data": content
                }
            )
    
    async def technical_member_task_live(self, data: dict) -> None:
        await self.send_json(data['data'])
    