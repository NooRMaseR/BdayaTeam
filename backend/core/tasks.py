from django.template.loader import render_to_string
from huey.contrib.djhuey import task
from django.core.mail import send_mail

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
