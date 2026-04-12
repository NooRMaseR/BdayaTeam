from pywebpush import webpush, webpush_async, WebPushException
from django.template.loader import render_to_string
from core.models import PushSubscription, UserRole
from huey.contrib.djhuey import task, db_task
from django.core.mail import send_mail
from django.conf import settings
import asyncio
import json

@task(retries=3, retry_delay=10)
def send_member_email(username: str, email: str, password: str, code: str, track: str) -> None:
    template = render_to_string(
        "register_email.html", 
        {
            "username": username,
            "email": email,
            "password": password,
            "code": code,
            "track": track
        }
    )
    send_mail(
        "Welcome to Team Bdaya",
        "Welcome",
        from_email=None,
        recipient_list=[email],
        html_message=template
    )


@db_task(retries=2, retry_delay=60)
def send_notification_to_track_members(track_id: int, title: str, body: str, url: str = "/") -> None:
    subscriptions = PushSubscription.objects.filter(user__track_id=track_id).iterator(300)
    
    payload = json.dumps({
        "title": title,
        "body": body,
        "url": url
    })

    for sub in subscriptions:
        sub_info = {
            "endpoint": sub.endpoint,
            "keys": {"auth": sub.auth, "p256dh": sub.p256dh}
        }
        
        try:
            webpush(
                subscription_info=sub_info,
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_ADMIN_EMAIL}
            )
        except WebPushException as ex:
            if ex.response is not None and ex.response.status in [404, 410]:
                sub.delete()

async def _send_to_single_user(sub: PushSubscription, payload: str) -> None:
    sub_info = {
        "endpoint": sub.endpoint,
        "keys": {"auth": sub.auth, "p256dh": sub.p256dh}
    }
    
    try:
        await webpush_async(
            subscription_info=sub_info,
            data=payload,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.VAPID_ADMIN_EMAIL}
        )
    except WebPushException as ex:
        if ex.response is not None and ex.response.status in [404, 410]:
            await sub.adelete()

async def send_notification_to_user(user_id: int, title: str, body: str, url: str = "/") -> None:
    subscriptions = PushSubscription.objects.filter(user_id=user_id)
    
    payload = json.dumps({
        "title": title,
        "body": body,
        "url": url
    })
    
    tasks = [
        asyncio.create_task(_send_to_single_user(sub, payload))
        async for sub in subscriptions
    ]
    await asyncio.gather(*tasks)

async def send_notification_to_track_technicals(track_id: int, title: str, body: str, url: str = "/") -> None:
    subscriptions = PushSubscription.objects.filter(user__track_id=track_id, user__role=UserRole.TECHNICAL)
    
    payload = json.dumps({
        "title": title,
        "body": body,
        "url": url
    })
    
    tasks = [
        asyncio.create_task(_send_to_single_user(sub, payload))
        async for sub in subscriptions
    ]
    await asyncio.gather(*tasks)
    
