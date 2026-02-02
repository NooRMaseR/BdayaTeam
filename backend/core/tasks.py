from django.template.loader import render_to_string
from django.core.mail import send_mail
from huey.contrib.djhuey import task


@task(retries=3, retry_delay=10)
def send_member_email(username: str, email: str, password: str, code: str, track: str):
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
        "Team Bdaya Info",
        "Welcome",
        from_email=None,
        recipient_list=[email],
        html_message=template
    )