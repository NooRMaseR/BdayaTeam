from celery import shared_task
from django.utils import timezone

from member.models import Member, MemberStatus
from .models import Attendance, AttendanceAllowedDay, AttendanceStatus

@shared_task
def make_rest_members_absents():
    today = timezone.now().date()
    today_obj = AttendanceAllowedDay.objects.filter(day=today).values_list('id', flat=True)
    
    if len(today_obj) == 0:
        return "no attendance today..."
    
    atts = Attendance.objects.filter(date__in=today_obj).values_list("member__code", flat=True).iterator(500)
    members_marked = Member.objects.only('code', 'name').exclude(code__in=atts).iterator(500)
    
    marked_atts = (Attendance(date_id=today_obj, member=m, status=AttendanceStatus.ABSENT) for m in members_marked)
    Attendance.objects.bulk_create(marked_atts)
    
    return "Done"

@shared_task
def delete_fired_members():
    Member.objects.filter(status=MemberStatus.FIRED).delete()