from django.shortcuts import render
from django.http import HttpResponse
from boituvaplaces.models import *
from .import_data import importador


# data = importador()
def index(request):
    return HttpResponse("Bem vindo a lugares em Boituva!")


def importa_rotas(request):
    data_rotas = importador("rotas_limpo.json")
    retorno = 'Registros importados: '
    for rota, descricao in data_rotas.items():
        nova_rota, created = Rota.objects.get_or_create(codigo=rota,
                                                         nome=descricao)
        if created == False:
            print(f'{rota}: {descricao} já existe.')
            falha = f', {rota}: {descricao} já existe.'
            retorno += falha

        retorno += f', {rota}'


    return HttpResponse(f'{retorno}')


def importa_pontos(request):
    pontos = importador("pontos_onibus.json")
    for ponto, info in pontos.items():
        # print(ponto, len(pontos[ponto]))
        if type(info[0]) == list:
            rotas = info[0] # pega a lista de rotas que passam por este ponto
            lat = info[1]["latitude"]
            lng = info[2]["longitude"]
        else:
            rotas = info
            lat = 0.0
            lng = 0.0
        print(ponto, rotas, lat, lng)

        parada, created = ParadaOnibus.objects.get_or_create(endereco=ponto,
                                                             defaults={"latitude": lat,
                                                                       "longitude": lng})

        parada.rotas.set(rotas)
        if created == False:
            print(f'ponto {ponto} já existe')
        else: print(f'adicionado ponto {ponto}')
    return HttpResponse("Teste")
