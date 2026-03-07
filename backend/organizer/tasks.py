from huey import crontab
from member.models import Member
from django.utils import timezone
from huey.contrib.djhuey import db_periodic_task
from .models import Attendance, AttendanceAllowedDay, AttendanceStatus

@db_periodic_task(crontab(hour='22', minute='0'), retries=3, retry_delay=10)
def make_rest_members_absents():
    today = timezone.now().date()
    today_obj = AttendanceAllowedDay.objects.filter(day=today).first()
    
    if not today_obj:
        return "no attendance today..."
    
    members_without_attendance = Member.objects.only('code').exclude(attendances__date=today_obj).iterator(300)
    
    marked_atts = [Attendance(date=today_obj, member=m, status=AttendanceStatus.ABSENT) for m in members_without_attendance]
    Attendance.objects.bulk_create(marked_atts, batch_size=300, ignore_conflicts=True)
    
    return f"{len(marked_atts)} Members has been marked as absent"
