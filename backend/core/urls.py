from django.urls import path
from . import views

urlpatterns = (
    path("login/", views.Login.as_view()),
    path("logout/", views.Logout.as_view()),
    path("register/", views.Register.as_view()),
    path("test-auth/", views.TestAuthCredentials.as_view()),
    path("tracks/", views.Tracks.as_view()),
)