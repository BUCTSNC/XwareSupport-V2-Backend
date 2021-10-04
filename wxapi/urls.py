from django.urls import path

from . import views
urlpatterns = [
    path("login", views.login.as_view()),
    path("timeslotList",views.TimeslotList.as_view()),
    path("problemTypes",views.ProblemType.as_view()),
    path("Appointment",views.Appointment.as_view()),
    path("myAppointmentList",views.myAppointmentList.as_view()),
    path("delModAppointment",views.delModAppointment_view.as_view())
]