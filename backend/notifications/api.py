from django.http import HttpRequest
from .models import PushSubscription
from ninja_extra import api_controller, route, status
from .api_schemas import SubscriptionRequest, UnsubscribeRequest

@api_controller("notifications")
class NotificationController:
    
    @route.post("/subscribe/", response={204: None})
    async def save_subscription(self, request: HttpRequest, payload: SubscriptionRequest):
        await PushSubscription.objects.aupdate_or_create(
            user=request.user,
            endpoint=payload.endpoint,
            defaults={
                "auth": payload.auth,
                "p256dh": payload.p256dh
            }
        )
        return status.HTTP_204_NO_CONTENT, None
    
    @route.post('/unsubscribe/', response={204: None})
    async def unsubscribe_device(self, request, payload: UnsubscribeRequest):
        await PushSubscription.objects.filter(
            user=request.user, 
            endpoint=payload.endpoint
        ).adelete()
        
        return status.HTTP_204_NO_CONTENT, None