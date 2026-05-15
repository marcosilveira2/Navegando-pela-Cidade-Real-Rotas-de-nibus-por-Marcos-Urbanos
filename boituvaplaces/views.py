from django.shortcuts import render
from django.http import HttpResponse
from boituvaplaces.models import *
from .import_data import importador


# data = importador()

print(importador())

def index(request):
    rotas = Rotas.objects.all()
    return HttpResponse("Teste")

