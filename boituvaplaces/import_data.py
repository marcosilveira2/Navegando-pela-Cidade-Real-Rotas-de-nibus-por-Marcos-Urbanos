import json

def importador(arquivo: str) -> dict:
    """importa arquivo json e retorna um dicionario (dict)."""
    # nome = input('digite o nome do arquivo json: ')
    nome = arquivo
    with open(f'../piplaces/boituvaplaces/{nome}', 'r') as j:
        file = j.read()

    dados = json.loads(file)
    print(type(dados))

    return dados
    
