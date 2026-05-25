from django.shortcuts import render
from django.http import HttpResponse
from django.urls import get_resolver, reverse
from boituvaplaces.models import *
from .import_data import importador
from django.contrib.gis.geos import Point


# data = importador()
def index(request):
    resolver = get_resolver()
    html_simples = "<h1>Links de importação do banco de dados</h1><ul>"
    url_rotas = request.build_absolute_uri(reverse("importa_rotas"))
    url_pontos = request.build_absolute_uri(reverse("importa_pontos"))
    link_rotas = f'<li><a href="{url_rotas}">importa_rotas</a></li>'
    link_pontos = f'<li><a href="{url_pontos}">importa_pontos</a></li>'
    html_simples += f'{link_rotas} {link_pontos} </ul>'
    return HttpResponse(html_simples)


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

    for endereco_nome, info in pontos.items():
        endereco_nome = endereco_nome.lstrip('"')
        endereco_nome = endereco_nome.rstrip('",')
        if isinstance(info[0], list):
            nomes_rotas = info[0]
            lat = info[1]["latitude"]
            lng = info[2]["longitude"]
            ponto_geometrico = Point(lng, lat, srid=4326)  # Mantendo Longitude primeiro (X, Y)
        else:
            nomes_rotas = info
            ponto_geometrico = Point(0.0, 0.0, srid=4326)

        parada, created = ParadaOnibus.objects.get_or_create(
            endereco=endereco_nome,
            defaults={"coordenadas": ponto_geometrico})
        objetos_rotas = []

        if isinstance(nomes_rotas, str):
            nomes_rotas = [nomes_rotas]

        for nome_rota in nomes_rotas:
            try:
                rota_obj = Rota.objects.get(codigo=nome_rota)
                objetos_rotas.append(rota_obj)
            except Rota.DoesNotExist:
                print(f"Rota{nome_rota} não existe")

        parada.rotas.set(objetos_rotas)

        if not created:
            parada.coordenadas = ponto_geometrico
            parada.save()
            print(f'Ponto "{endereco_nome}" já existia (coordenadas atualizadas).')
        else:
            print(f'Adicionado ponto: "{endereco_nome}"')

    return HttpResponse("Importação concluída com sucesso!")