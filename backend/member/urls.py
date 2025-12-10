from django.urls import path
from . import views

urlpatterns = (
    path("tasks/", views.Tasks.as_view()),
    path("profile/<str:member_code>/", views.MemberProfile.as_view()),
)
