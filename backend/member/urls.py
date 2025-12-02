from django.urls import path
from . import views

urlpatterns = [
    path("tasks/<str:track_name>", views.Tasks.as_view()),
]