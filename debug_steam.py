import requests
from bs4 import BeautifulSoup

url = "https://store.steampowered.com/search/?term=GTA+V"

headers = {
    "user-agent":"Mozilla/5.0"
}

response = requests.get(url, headers=headers)
html = response.text

soup = BeautifulSoup(html, "lxml")

resultado= soup.find("a,",class_='search_result_row')

if resultado is None:
    print("Não encontrou nenhum resultado")

else:
    print("===TAG ENCONTRADA===")
    print(resultado)

    texto_do_jogo = resultado.get_text(strip = True)
    print(texto_do_jogo)

    print("\n===LINK DO JOGO===")
    print(resultado["href"])


