from django.conf import settings
from .models import PushSubscription
from core.permissions import get_any_authenticated_user
from django_bolt import BoltAPI, Depends, Response, status
from .api_schemas import SubscriptionRequestMSG, UnsubscribeRequestMSG

bolt = BoltAPI(
    prefix="/api/notifications/",
    trailing_slash="append",
    validate_response=False,
    django_middleware=settings.BOLT_MIDDLEWARE
)

@bolt.post("/subscribe/", status_code=204)
async def save_subscription(payload: SubscriptionRequestMSG, user = Depends(get_any_authenticated_user)):
    "notification subscribtion"
    
    await PushSubscription.objects.aupdate_or_create(
        user=user,
        endpoint=payload.endpoint,
        defaults={
            "auth": payload.auth,
            "p256dh": payload.p256dh
        }
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@bolt.post('/unsubscribe/', status_code=204)
async def unsubscribe_device(payload: UnsubscribeRequestMSG, user = Depends(get_any_authenticated_user)):
    "notification unsubscribtion"
    
    await PushSubscription.objects.filter(
        user=user, 
        endpoint=payload.endpoint
    ).adelete()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
