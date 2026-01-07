from django.urls import path
from . import views

urlpatterns = (
    path("members/<str:track_name>/", view=views.Members.as_view(), name="members-list"),
    path("attendance/<str:track_name>/days/", view=views.AttendanceDayApi.as_view(), name="attendance-days"),
    path("attendance/<str:track_name>/editor/", view=views.MemberEdit.as_view(), name="attendance-editor"),
    path("settings/", view=views.SettingsApi.as_view(), name="settings"),
)