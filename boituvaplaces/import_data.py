import json

def importador():
    nome = input('digite o nome do arquivo json: ')
    with open(f'../piplaces/boituvaplaces/{nome}', 'r') as j:
        file = j.read()

    dados = json.loads(file)

    return dados
    
