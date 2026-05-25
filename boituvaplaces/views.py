from django.shortcuts import render
from django.http import HttpResponse
from django.urls import get_resolver, reverse
from boituvaplaces.models import *
from .import_data import importador
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance


# data = importador()
def index(request):
    resolver = get_resolver()
    html_simples = "<h1>Links de importação do banco de dados</h1><ul>"
    url_rotas = request.build_absolute_uri(reverse("importa_rotas"))
    url_pontos = request.build_absolute_uri(reverse("importa_pontos"))
    url_locais = request.build_absolute_uri(reverse("importa_locais"))
    link_rotas = f'<li><a href="{url_rotas}">importa_rotas</a></li>'
    link_pontos = f'<li><a href="{url_pontos}">importa_pontos</a></li>'
    link_locais = f'<li><a href="{url_locais}">importa_locais</a></li>'
    html_simples += f'{link_rotas} {link_pontos} {link_locais}</ul>'
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

def importa_locais(request):
    locais = importador("lista_de_locais_1.json")
    resposta = type(locais)
    for local in locais:
        print(local['tipo'])
        lng = local['lng']
        lat = local['lat']
        ponto_geometrico = Point(lng, lat, srid=4326)
        local_cidade, created = Local.objects.get_or_create(
            nome=local['nome'],
            endereco=local['endereco'],
            coordenadas=ponto_geometrico,
            tipo_local=local['tipo']
        )
        if not created:
            print(f"local {local['nome']} já existia")
        else:
            print(f"adicionado{local['nome']}")

    return HttpResponse("Locais adicionados ao banco de dados!")

def buscar_proximidades(request):
    query = request.GET.get('q')
    context = {'query': query}

    if query:
        # Encontra o local pesquisado (pegando o primeiro resultado que contenha o termo)
        local_pesquisado = Local.objects.filter(nome__icontains=query).first()

        if local_pesquisado:
            context['local_pesquisado'] = local_pesquisado

            # Encontra o marco urbano mais próximo
            # e calcula a distância entre as coordenadas.
            marco_proximo = Local.objects.filter(
                e_marco=True
            ).exclude(
                id=local_pesquisado.id
            ).annotate(
                distancia=Distance('coordenadas', local_pesquisado.coordenadas)
            ).order_by('distancia').first()

            # Encontra o ponto de ônibus mais próximo
            ponto_proximo = ParadaOnibus.objects.annotate(
                distancia=Distance('coordenadas', local_pesquisado.coordenadas)
            ).order_by('distancia').first()

            context['marco_proximo'] = marco_proximo
            context['ponto_proximo'] = ponto_proximo
        else:
            context['erro'] = "Local não encontrado no banco de dados."

    return render(request, 'boituvaplaces/busca_local.html', context)