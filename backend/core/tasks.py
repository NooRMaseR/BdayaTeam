from django.template.loader import render_to_string
from huey.contrib.djhuey import task, db_task
from django.core.mail import send_mail
from django.db import transaction
from .models import Track

@db_task(retry=2, retry_delay=10)
def delete_all_tracks() -> None:
    with transaction.atomic():
        Track.objects.all().delete()

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
