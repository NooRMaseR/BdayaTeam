from huey.contrib.djhuey import task, db_task, periodic_task
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.db import transaction
from django.conf import settings
from .models import Track
from huey import crontab
import subprocess
import tarfile
import os

def automated_backup_pg() -> None:
    db_settings = settings.DATABASES['default']
    db_name = db_settings['NAME']
    db_user = db_settings['USER']
    db_password = db_settings['PASSWORD']
    db_host = db_settings['HOST']
    db_port = str(db_settings.get('PORT', '5432'))

    backup_dir = '/app/backups'
    os.makedirs(backup_dir, exist_ok=True)

    filename = f"{db_name}.dump"
    filepath = os.path.join(backup_dir, filename)

    env = os.environ.copy()
    env['PGPASSWORD'] = db_password

    command = [
        'pg_dump',
        '-h', db_host,
        '-p', db_port,
        '-U', db_user,
        '-F', 'c',
        '-f', filepath,
        db_name
    ]

    print(f"Starting automated backup for database '{db_name}'...")

    try:
        subprocess.run(command, env=env, check=True, capture_output=True, text=True)
        print(f"Successfully created backup: {filename}")
        
    except subprocess.CalledProcessError as e:
        print(f"Automated backup failed! Error: {e.stderr}")


def backup_media_files() -> None:
    media_dir = '/app/media_files'
    backup_dir = '/app/backups'
    backup_filename = f"media.tar.gz"
    filepath = os.path.join(backup_dir, backup_filename)

    print("Backing up media files...")
    
    with tarfile.open(filepath, "w:gz") as tar:
        tar.add(media_dir, arcname=os.path.basename(media_dir))
    
    print(f"Successfully backed up media to: {backup_filename}")

@periodic_task(crontab(minute='0', hour='3', day_of_week='4'))
def backup_db() -> None:
    automated_backup_pg()
    backup_media_files()

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
