from django.urls import path
from . import views

urlpatterns = [
    path("register",views.register.as_view()),
    path("login",views.login.as_view()),
    path("scanCode",views.scanCode.as_view()),
    path("startService",views.startService.as_view()),
    path("getAppointment",views.myAppointment.as_view())
]