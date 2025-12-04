from django.urls import path
from . import views

urlpatterns = (
    path("tasks/", views.Tasks.as_view()),
    path("tasks/recived/", views.TasksFromMembers.as_view()),
)