from django.urls import path
from .views import coleta, dashboard, equipe, home, indicador_detail, indicador_excluir, indicadores

urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("coleta/", coleta, name="coleta"),
    path("coleta/<int:pk>/", coleta, name="coleta_edit"),
    path("indicadores/", indicadores, name="indicadores"),
    path("indicadores/<int:pk>/", indicador_detail, name="indicador_detail"),
    path("indicadores/<int:pk>/excluir/", indicador_excluir, name="indicador_excluir"),
    path("equipe/", equipe, name="equipe"),
]
