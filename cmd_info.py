import subprocess

def executar(cmd):
    try:
        # shell=True e encoding utf-8 garantem compatibilidade
        return subprocess.check_output(cmd, shell=True, text=True, encoding="utf-8").strip()
    except:
        return "Não encontrado"

def obter_so():
    # Pega o nome do SO independente da tradução da interface
    return executar('powershell -Command "(Get-CimInstance Win32_OperatingSystem).Caption"')

def obter_cpu():
    # ExpandProperty ignora rótulos de idioma e pega o valor direto
    return executar('powershell -Command "(Get-CimInstance Win32_Processor) | Select-Object -ExpandProperty Name -Unique"')

def obter_gpu():
    # Detecta todas as GPUs e as junta com vírgula, sem depender de tradução
    return executar('powershell -Command "((Get-CimInstance Win32_VideoController) | Select-Object -ExpandProperty Name) -join \', \'"')

def obter_cmd():
    return {"so": obter_so(), "cpu": obter_cpu(), "gpu": obter_gpu()}

if __name__ == "__main__":
    print(obter_cmd())
