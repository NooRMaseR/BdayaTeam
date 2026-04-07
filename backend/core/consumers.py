from channels.generic.websocket import AsyncJsonWebsocketConsumer

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        self.track_name: str = self.scope['url_route']['kwargs']['track_name'].replace(' ', '_') # type: ignore
        self.group_name = f"technical_{self.track_name}_notifications"
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, code: int) -> None:
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    async def receive_json(self, content: dict, **kwargs: dict) -> None:
        if content:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "broadcast_technical",
                    "data": content
                }
            )
    
    async def broadcast_technical(self, data: dict) -> None:
        await self.send_json(data['data'])
    