from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("importa_rotas/", views.importa_rotas, name="importa_rotas"),
    path("importa_pontos/", views.importa_pontos, name="importa_pontos"),
    path("importa_locais/", views.importa_locais, name="importa_locais"),
]
