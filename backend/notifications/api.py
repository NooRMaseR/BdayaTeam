from django.conf import settings
from .models import PushSubscription
from core.auth import JWT_COOKIES_AUTH
from .api_schemas import SubscriptionRequestMSG, UnsubscribeRequestMSG
from django_bolt import BoltAPI, IsAuthenticated, Request, Response, status

bolt = BoltAPI(
    prefix="/api/notifications/",
    trailing_slash="append",
    validate_response=False,
    django_middleware=settings.BOLT_MIDDLEWARE
)

@bolt.post("/subscribe/", status_code=204, auth=[JWT_COOKIES_AUTH], guards=[IsAuthenticated()])
async def save_subscription(request: Request, payload: SubscriptionRequestMSG):
    "notification subscribtion"
    
    await PushSubscription.objects.aupdate_or_create(
        user=request.user,
        endpoint=payload.endpoint,
        defaults={
            "auth": payload.auth,
            "p256dh": payload.p256dh
        }
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@bolt.post('/unsubscribe/', status_code=204, auth=[JWT_COOKIES_AUTH], guards=[IsAuthenticated()])
async def unsubscribe_device(request: Request, payload: UnsubscribeRequestMSG):
    "notification unsubscribtion"
    
    await PushSubscription.objects.filter(
        user=request.user, 
        endpoint=payload.endpoint
    ).adelete()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
