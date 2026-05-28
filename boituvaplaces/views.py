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
    url_marcos = request.build_absolute_uri(reverse("importa_marco"))
    link_rotas = f'<li><a href="{url_rotas}">importa_rotas</a></li>'
    link_pontos = f'<li><a href="{url_pontos}">importa_pontos</a></li>'
    link_locais = f'<li><a href="{url_locais}">importa_locais</a></li>'
    link_marcos = f'<li><a href="{url_marcos}">importa_marco</a></li>'
    html_simples += f'{link_rotas} {link_pontos} {link_locais} {link_marcos}</ul>'
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
    for local in locais:
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


def marcos_turisticos(request):
    locais = importador("pontos_turisticos.json")

    try:
        marco_tur = CategoriaMarco.objects.get(nome="Turístico")
    except CategoriaMarco.DoesNotExist:
        return HttpResponse("Erro: A categoria 'Turístico' não existe no banco de dados. Cadastre-a primeiro.")

    for local in locais:
        lng = local['lon']
        lat = local['lat']
        ponto_geometrico = Point(lng, lat, srid=4326)

        nome_local = local.get('Ponto Turístico') or local.get('nome')
        endereco_local = local.get('Endereço') or local.get('endereco', '')

        local_cidade, created = Local.objects.get_or_create(
            nome=nome_local,
            endereco=endereco_local,
            defaults={
                "coordenadas": ponto_geometrico,
                "e_marco": True,
            }
        )

        local_cidade.tipo_marco.set([marco_tur])

        if not created:
            # Se já existia, atualiza os dados caso tenham mudado no JSON
            local_cidade.endereco = endereco_local
            local_cidade.coordenadas = ponto_geometrico
            local_cidade.e_referencia = True
            local_cidade.save()
            print(f"Local '{nome_local}' já existia (dados atualizados).")
        else:
            print(f"Adicionado: '{nome_local}'")

    return HttpResponse("Locais turísticos importados com sucesso!")

def buscar_proximidades(request):
    query = request.GET.get('q')
    local_id = request.GET.get('local_id')  # Novo parâmetro para seleção exata
    context = {'query': query}

    if query or local_id:
        local_pesquisado = None

        # Se o usuário clicou em uma opção específica da lista de múltiplos resultados
        if local_id:
            local_pesquisado = Local.objects.filter(id=local_id).first()

        # Se é uma busca nova por texto
        elif query:
            locais_encontrados = Local.objects.filter(nome__icontains=query)
            quantidade = locais_encontrados.count()

            if quantidade == 1:
                # Caiu direto em um único resultado
                local_pesquisado = locais_encontrados.first()
            elif quantidade > 1:
                # Encontrou vários, passa a lista para o template
                context['locais_multiplos'] = locais_encontrados
            else:
                context['erro'] = "Nenhum local encontrado no banco de dados."

        # calcula as rotas
        if local_pesquisado:
            context['local_pesquisado'] = local_pesquisado

            # Busca no banco usando graus
            marco_proximo = Local.objects.filter(
                e_marco=True
            ).exclude(
                id=local_pesquisado.id
            ).annotate(
                distancia_graus=Distance('coordenadas', local_pesquisado.coordenadas)
            ).order_by('distancia_graus').first()

            ponto_proximo = ParadaOnibus.objects.annotate(
                distancia_graus=Distance('coordenadas', local_pesquisado.coordenadas)
            ).order_by('distancia_graus').first()

            # Converte para metros na memória
            ponto_ref_metros = local_pesquisado.coordenadas.clone()
            ponto_ref_metros.transform(3857)

            if marco_proximo:
                marco_metros = marco_proximo.coordenadas.clone()
                marco_metros.transform(3857)
                marco_proximo.distancia_em_metros = ponto_ref_metros.distance(marco_metros)
                context['marco_proximo'] = marco_proximo

            if ponto_proximo:
                ponto_metros = ponto_proximo.coordenadas.clone()
                ponto_metros.transform(3857)
                ponto_proximo.distancia_em_metros = ponto_ref_metros.distance(ponto_metros)
                context['ponto_proximo'] = ponto_proximo

    return render(request, 'boituvaplaces/busca_local.html', context)