import requests

def buscar_jogo_na_steam(nome_do_jogo):
    print("Buscando:", nome_do_jogo)
    
    url= "https://store.steampowered.com/api/storesearch"
    params = {"term": nome_do_jogo, "cc": "BR","l": "Portuguese", "limit":5}

    response = requests.get(url, params=params)
    if response.status_code != 200:

        return None
    

    dados = response.json()
    if not dados["items"]:
        return None

    return dados["items"][0]



def buscar_jogo(nome):
    print("Buscando jogo na Steam...")
    print("Nome digitado:", nome)

    return {"nome": nome, "platafoma": "Steam"}

nome = input("Digite o nome do jogo:")
jogo = buscar_jogo_na_steam(nome)

print("Resultado", nome)

      