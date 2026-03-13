import requests
import re


def buscar_detalhes_jogo(appid):
    url = "https://store.steampowered.com/api/appdetails"

    params = {"appids":appid, "cc":"BR","l":"portuguese"}

    response = requests.get(url,params = params)
    dados = response.json()

    appid_str = str(appid)

    texto_min = dados[appid_str]["data"]["pc_requirements"]["minimum"]

    
    texto_min = re.split(r"Notas adicionais:",texto_min,flags=re.IGNORECASE)[0]

    texto_min = texto_min.replace("<br>", "\n")
    texto_min = texto_min.replace("<br />", "\n")
    texto_min = texto_min.replace("<strong>", "")
    texto_min = texto_min.replace("</strong>", "")
    texto_min = texto_min.replace("<li>", "")
    texto_min = texto_min.replace("</li>", "")
    texto_min = texto_min.replace('<ul class="bb_ul">', "")
    texto_min = texto_min.replace("</ul>", "")

    return {"requisitos": texto_min.strip(), "gpu_min":"Consta nos requisitos abaixo", "cpu_min":"Consta nos requisitos abaixo"}

texto_limpo = buscar_detalhes_jogo(271590)

print("REQUISITOS:\n")   
print(texto_limpo)     
    
def extrair_ram(texto):
    for linha in texto.split("\n"):
        if "memória" in linha.lower():
            match = re.search(r"(\d+)\s*gb", linha.lower())
            if match:
                return int(match.group(1))

    return None


print("==== TEXTO RECEBIDO ====")
print(texto_limpo)

ram_min = extrair_ram(texto_limpo["requisitos"])
print("RAM minima:", ram_min, "GB")



def extrair_disco(texto):
    for linha in texto.split("\n"):
        l = linha.lower()

        if any(p in l for p in ["disco", "armazenamento", "espaço"]):
            match = re.search(r"(\d+)\s*gb", l)
            if match:
                return int(match.group(1))
    return {"ram_min":ram_min, "disco_min":disco_min,"requisitos":texto_limpo}

    

disco_min = extrair_disco(texto_limpo["requisitos"])
print("Disco minimo:", disco_min, "GB")

def extrair_cpu(texto):
    for linha in texto.split("\n"):
        if "processador" in linha.lower():
            
            cpu = linha.split(":",1)[-1].strip()
            return cpu
        return None

def buscar_appid_por_nome(nome_jogo):
    url = "https://store.steampowered.com/api/storesearch"
    params = {"term": nome_jogo, "cc": "BR","l":"Portuguese"}

    response = requests.get(url, params= params)
    dados = response.json()

    if dados["total"] == 0:
        return None
    return dados["items"][0]["id"]
 







    