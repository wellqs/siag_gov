from django.urls import path
from .views import coleta, dashboard, equipe, home

urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("coleta/", coleta, name="coleta"),
    path("equipe/", equipe, name="equipe"),
]
