from django.urls import path
from . import views

urlpatterns = [
    path("login",views.login.as_view()),
    path("scanCode",views.scanCode.as_view())
]