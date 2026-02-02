from django.urls import path
from . import views

urlpatterns = (
    path("tasks/", views.Tasks.as_view()),
    path("tasks/<int:task_id>/", views.TaskView.as_view()),
    path("tasks/recived/<int:task_id>/", views.TasksFromMembers.as_view()),
)