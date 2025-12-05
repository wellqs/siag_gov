from django.urls import path
from .views import coleta, dashboard, home

urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("coleta/", coleta, name="coleta"),
]
