from .models import PushSubscription
from core.permissions import get_any_authenticated_user
from django_bolt import BoltAPI, Depends, Response, status
from .api_schemas import SubscriptionRequestMSG, UnsubscribeRequestMSG

bolt = BoltAPI(
    prefix="/api/notifications/",
    trailing_slash="append",
    django_middleware=[
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ],
    validate_response=False,
)

@bolt.post("/subscribe/", status_code=204)
async def save_subscription(payload: SubscriptionRequestMSG, user = Depends(get_any_authenticated_user)):
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
    await PushSubscription.objects.filter(
        user=user, 
        endpoint=payload.endpoint
    ).adelete()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# @api_controller("notifications")
# class NotificationController:
    
#     @route.post("/subscribe/", response={204: None})
#     async def save_subscription(self, request: HttpRequest, payload: SubscriptionRequest):
#         await PushSubscription.objects.aupdate_or_create(
#             user=request.user,
#             endpoint=payload.endpoint,
#             defaults={
#                 "auth": payload.auth,
#                 "p256dh": payload.p256dh
#             }
#         )
#         return status.HTTP_204_NO_CONTENT, None
    
#     @route.post('/unsubscribe/', response={204: None})
#     async def unsubscribe_device(self, request, payload: UnsubscribeRequest):
#         await PushSubscription.objects.filter(
#             user=request.user, 
#             endpoint=payload.endpoint
#         ).adelete()
        
#         return status.HTTP_204_NO_CONTENT, None
