from django.urls import path
from . import views

urlpatterns = [
    path("register",views.register.as_view()),
    path("login",views.login.as_view()),
    path("scanCode",views.scanCode.as_view()),
    path("startService",views.startService.as_view()),
    path("getAppointment",views.myAppointment.as_view()),
    path("submitTicket",views.submitTicket.as_view()),
    path("pdf",views.createPdf.as_view()),
    path("download",views.download.as_view()),
    path("cancelwork",views.modifyAppointment.as_view()),
    path("loadTicket",views.modifyAppointment.as_view()),
]