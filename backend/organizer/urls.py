from django.urls import path
from . import views

urlpatterns = (
    path("members/bonus/", view=views.MemberBonus.as_view()),
    path("members/<str:track_name>/", view=views.Members.as_view()),
)