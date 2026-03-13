import tkinter as tk
from steam_api import buscar_detalhes_jogo
from steam_api import extrair_ram, extrair_disco, extrair_cpu, buscar_appid_por_nome
from pcinfo import pegar_info_pc
from cmd_info import obter_cmd
from cpu_compare import comparar_cpu, nivel_cpu
from gpu_compare import comparar_gpu, nivel_gpu
import threading
import math
import random
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import re

FONT_ICON = ("Segoe UI Emoji", 16)
FONT_ROW_LABEL = ("Segoe UI", 10)
FONT_ROW_VALUE = ("Segoe UI", 10, "bold")
FONT_DISPLAY = ("Segoe UI", 38, "bold") 
FONT_GAUGE_LABEL = ("Segoe UI", 9, "bold")


COLOR_BG = "#000000"           
COLOR_PURPLE = "#7e22ce"       
COLOR_ORANGE = "#ea580c"       
COLOR_CARD_BG = "#0a0a0a"      
COLOR_CARD_BORDER = "#1f1f1f"
COLOR_GREEN_BTN = "#84cc16"


class CyberGauge(tk.Canvas):
    def __init__(self, parent, width=340, height=240, bg_color="#0f0f0f"):
        super().__init__(parent, width=width, height=height, bg=bg_color, highlightthickness=0)
        self.width = width
        self.height = height
        self.cx = width // 2
        self.cy = height - 40
        self.radius = 90
        self.thickness = 18
        self.current_value = 0
        self.draw_background()
        self.draw_progress(0, "secondary")

    def draw_background(self):
        x0, y0, x1, y1 = self.cx-self.radius, self.cy-self.radius, self.cx+self.radius, self.cy+self.radius
        self.create_arc(x0, y0, x1, y1, start=180, extent=-180, style=tk.ARC, width=self.thickness, outline="#1a1a1a")
        # Pequenos traços do medidor (ticks)
        for i in range(13):
            angle = math.radians(180 - (i * 15))
            x1, y1 = self.cx + (self.radius-15) * math.cos(angle), self.cy - (self.radius-15) * math.sin(angle)
            x2, y2 = self.cx + (self.radius-5) * math.cos(angle), self.cy - (self.radius-5) * math.sin(angle)
            self.create_line(x1, y1, x2, y2, fill="#333", width=2)

    def draw_progress(self, value, bootstyle_color):
        self.delete("progress")
        colors = {"danger": "#ff3b3b", "warning": "#ffb300", "success": "#00ff88", "secondary": "#444"}
        color = colors.get(bootstyle_color, "#444")
        extent = (value / 100) * 180
        x0, y0, x1, y1 = self.cx-self.radius, self.cy-self.radius, self.cx+self.radius, self.cy+self.radius
        self.create_arc(x0, y0, x1, y1, start=180, extent=-extent, style=tk.ARC, width=self.thickness, outline=color, tags="progress")
        self.create_text(self.cx, self.cy - 30, text=f"{int(value)}%", fill="white", font=("Segoe UI", 35, "bold"), tags="progress")
        self.create_text(self.cx, self.cy + 15, text="COMPATIBILIDADE", fill="#888", font=("Segoe UI", 8, "bold"), tags="progress")

    def animate_to(self, target, color):
        step = 1 if target > self.current_value else -1
        def anim():
            if self.current_value != target:
                self.current_value += step
                self.draw_progress(self.current_value, color)
                self.after(10, anim)
        anim()

class GameCompatibilityPro(ttk.Window):
    def __init__(self):
        super().__init__(themename="cyborg")
        self.title("Verificador de Compatibilidade")
        self.geometry("1300x800")
        self.state("zoomed")
        
        # 1. Container principal
        self.container = ttk.Frame(self, padding=20)
        self.container.pack(fill=BOTH, expand=True)

        # 2. Header (Busca e Botão)
        self.header_frame = ttk.Frame(self.container)
        self.header_frame.pack(fill=X, pady=(0, 20))
        
        # Alinhando busca à direita igual à foto
        search_sub = ttk.Frame(self.header_frame)
        search_sub.pack(side=RIGHT)
        ttk.Label(search_sub, text="JOGO:", font=("Segoe UI", 9, "bold")).pack(side=LEFT, padx=5)
        self.jogo_entry = ttk.Entry(search_sub, width=30)
        self.jogo_entry.pack(side=LEFT, padx=5)
        self.botao = ttk.Button(search_sub, text="ANALISAR", bootstyle="success", command=self.iniciar_calculo)
        self.botao.pack(side=LEFT, padx=5)

        # 3. Content Frame (As 3 Colunas)
        self.content_frame = ttk.Frame(self.container)
        self.content_frame.pack(fill=BOTH, expand=True)
        self.content_frame.columnconfigure(0, weight=1, uniform="a")
        self.content_frame.columnconfigure(1, weight=1, uniform="a")
        self.content_frame.columnconfigure(2, weight=1, uniform="a")

        # PAINEL PC (ESQUERDA) - Bordas Roxas
        self.pc_panel = tk.Frame(self.content_frame, bg="#050505", highlightbackground="#7e22ce", highlightthickness=1)
        self.pc_panel.grid(row=0, column=0, sticky="nsew", padx=10)
        tk.Label(self.pc_panel, text=" MEU PC ", bg="#050505", fg="#7e22ce", font=("Segoe UI", 10, "bold")).place(x=20, y=-8)
        self.pc_specs_container = ttk.Frame(self.pc_panel, padding=15)
        self.pc_specs_container.pack(fill=BOTH, expand=True, pady=10)

        # PAINEL CENTRAL (METER)
        self.center_panel = ttk.Frame(self.content_frame)
        self.center_panel.grid(row=0, column=1, sticky="nsew")
        self.meter = CyberGauge(self.center_panel, bg_color=self.style.lookup("TFrame", "background"))
        self.meter.pack(pady=40)
        self.status_badge = ttk.Label(self.center_panel, text="AGUARDANDO...", font=("Segoe UI", 10, "bold"), bootstyle="secondary", padding=10)
        self.status_badge.pack()

        # PAINEL REQUISITOS (DIREITA) - Bordas Laranjas
        self.req_panel = tk.Frame(self.content_frame, bg="#050505", highlightbackground="#ea580c", highlightthickness=1)
        self.req_panel.grid(row=0, column=2, sticky="nsew", padx=10)
        tk.Label(self.req_panel, text=" REQUISITOS DO JOGO ", bg="#050505", fg="#ea580c", font=("Segoe UI", 10, "bold")).place(x=20, y=-8)
        self.req_specs_container = ttk.Frame(self.req_panel, padding=15)
        self.req_specs_container.pack(fill=BOTH, expand=True, pady=10)
        #Faz o botão enter iniciar a pesquisa
        self.jogo_entry.bind("<Return>", lambda event: self.iniciar_calculo())

        self.label_descricao = ttk.Label(
            self.container, 
            text="Aguardando...", 
            justify="center", 
            wraplength=1000, # Quebra o texto se for muito longo
            font=("Segoe UI", 10, "italic"),
            bootstyle="secondary"
        )
        self.label_descricao.pack(pady=(0, 20))

        self.label_detalhes = ttk.Label(self.container, text="") # Invisível para lógica

        # Inicializa widgets
        self.criar_interface_rows()
        self.carregar_dados_pc()

    def criar_interface_rows(self):
        self.pc_rows = {
            "cpu": self.create_pro_row(self.pc_specs_container, "⚡", "PROCESSADOR", "...", "success"),
            "gpu": self.create_pro_row(self.pc_specs_container, "🎮", "PLACA VÍDEO", "...", "success"),
            "ram": self.create_pro_row(self.pc_specs_container, "💾", "RAM", "...", "success"),
            "disco": self.create_pro_row(self.pc_specs_container, "💿", "DISCO", "...", "success"),
            "os": self.create_pro_row(self.pc_specs_container, "🪟", "SISTEMA", "...", "secondary")
        }
        self.req_rows = {
            "ram": self.create_pro_row(self.req_specs_container, "💾", "MEMÓRIA MÍNIMA", "--", "warning"),
            "cpu": self.create_pro_row(self.req_specs_container, "⚡", "PROCESSADOR", "--", "warning"),
            "gpu": self.create_pro_row(self.req_specs_container, "🎮", "GRAPHICS", "--", "warning"),
            "disco": self.create_pro_row(self.req_specs_container, "💿", "STORAGE", "--", "warning"),
            "os": self.create_pro_row(self.req_specs_container, "🪟", "OPERATING SYSTEM", "--", "secondary")
        }
    def animar_status(self, etapa=0):
        # Só continua animando se o texto ainda for de carregamento
        texto_atual = self.status_badge.cget("text")
        if "BUSCANDO" in texto_atual or "CARREGANDO" in texto_atual or "..." in texto_atual:
            pontos = "." * (etapa % 4) # Gera "", ".", "..", "..."
            self.status_badge.configure(text=f"BUSCANDO{pontos}", bootstyle= "Light")
            # Chama ela mesma 400ms para o próximo frame da animação
            self.after(400, lambda: self.animar_status(etapa + 1))


    def atualizar_requisitos_jogo(self, req):
        cpu_exibir= self.limpar_nome_peca(req.get("cpu", "Não Informado."))
        gpu_exibir= self.limpar_nome_peca(req.get("gpu", "Não Informado."))


        self.req_rows["ram"]["value"].config(text=req.get("ram", "--"))
        self.req_rows["cpu"]["value"].configure(text= cpu_exibir)
        self.req_rows["gpu"]["value"].configure(text= gpu_exibir)
        self.req_rows["disco"]["value"].config(text=req.get("disco", "--"))
        self.req_rows["os"]["value"].config(text=req.get("os", "--"))    


    def carregar_dados_pc(self):
        from pcinfo import pegar_info_pc

        try:
            info_pc = pegar_info_pc()
        except:
            info = {} #se der pau, cria vazio

        try:
            cmd_pc = obter_cmd()
        except:
            cmd = {}

        self.update_pc_row("ram", f"{info_pc.get('ram', 0)} GB", "success")
        self.update_pc_row("disco", f"{info_pc.get('disco', 0)} GB", "success")
        self.update_pc_row("os", str(info_pc.get('os', 'Windows')), "secondary")
        self.update_pc_row("cpu", str(cmd_pc.get('cpu', '--')), "success")
        self.update_pc_row("gpu", str(cmd_pc.get('gpu', '--')), "success")

    def update_pc_row(self, key, text, status="secondary"):
        row = self.pc_rows.get(key)
        if not row:
            return 
        
        row["value"].configure(text=text)
        row["icon"].configure(bootstyle=status)     

    def limpar_nome_peca(self, texto):
        if not texto or "Não indet" in texto or len(texto) < 2:
            return "Padrão (Médio)"
        texto = texto.upper()
        
        if len(texto) < 60:
            return texto.strip()
            
        texto_limpo = texto.replace("Equivalent", " ").replace("Equivalent", " ")

        if len(texto_limpo) > 80:
            return texto_limpo[:77]+ "..."
        
        return texto_limpo.strip()

    def create_pro_row(self, parent, icon, title, value, status_color="secondary", clicavel=False):
        # Card principal
        card = tk.Frame(parent, bg="#0a0a0a", highlightbackground="#1f1f1f", highlightthickness=1)
        card.pack(fill=X, pady=4)

        # Inner e Text Frame com fundo definido para não dar erro visual
        inner = tk.Frame(card, bg="#0a0a0a")
        inner.pack(fill=BOTH, expand=True)

        icon_lbl = ttk.Label(inner, text=icon, font=FONT_ICON, width=3, anchor=CENTER, bootstyle=status_color)
        icon_lbl.pack(side=LEFT, padx=(10, 5), pady=10)

        text_frame = tk.Frame(inner, bg="#0a0a0a")
        text_frame.pack(side=LEFT, fill=BOTH, expand=True, pady=2)

        ttk.Label(text_frame, text=title, font=FONT_ROW_LABEL, bootstyle="secondary", background="#0a0a0a").pack(anchor=W)
        val_lbl = ttk.Label(text_frame, text=value, font=FONT_ROW_VALUE, bootstyle="light", wraplength=300, background="#0a0a0a")
        val_lbl.pack(anchor=W)        

        return {"value": val_lbl, "icon": icon_lbl, "card": card}         


    def thread_background(self, nome_jogo):
        # Chama a função de lógica que está lá no final do arquivo
        try:
            resultado = calcular_logica_pura(nome_jogo)
        except Exception as e:
            resultado = {"erro": str(e)}
            
        # Devolve para a interface principal
        self.after(0, lambda: self.atualizar_tela(resultado))    

    def iniciar_calculo(self):
        nome_jogo = self.jogo_entry.get()    
        if not nome_jogo:
            return
        self.botao.configure(state= "disabled")
        self.status_badge.configure(text= "BUSCANDO...", bootstyle= "inverse-Light")
        self.animar_status()
        threading.Thread(target=self.thread_background, args=(nome_jogo,), daemon=True).start()

        
    def atualizar_tela(self, resultado):
        self.botao.configure(state="normal")

        if "erro" in resultado:
            self.label_resultado.configure(text=resultado["erro"], bootstyle="danger")
            self.status_badge.configure(text="ERRO", bootstyle="inverse-danger")
            self.meter.draw_progress(0, "danger")
            return

        #Chama apenas esta função para cuidar dos cards da direita
        self.atualizar_requisitos_jogo(resultado["req"])

        # Atualiza o restante da interface
        pct = resultado["porcentagem"]
        self.label_descricao.configure(text=resultado["descricao"])
        
        cor = "success" if pct >= 70 else "warning" if pct >= 40 else "danger"
        self.meter.animate_to(pct, cor)
        
        status_txt = "RODA LISO" if pct >= 70 else "JOGÁVEL" if pct >= 40 else "INCOMPATÍVEL"
        self.status_badge.configure(text=f"{status_txt} ({pct}%)", bootstyle=f"inverse-{cor}")

        self.update_idletasks()

    def simplificar_hardware(texto):
        texto = texto.upper()
        #Simplificar Intel
        if "I9" in texto: return "Intel Core i9"
        if "I7" in texto: return "Intel Core i7"
        if "I5" in texto: return "Intel Core i5"
        if "I3" in texto: return "Intel Core i3"
        #Simplificar AMD
        if "RYZEN 9" in texto: return "AMD Ryzen 9"
        if "RYZEN 7" in texto: return "AMD Ryzen 7"
        if "RYZEN 5" in texto: return "AMD Ryzen 5"
        if "RYZEN 3" in texto: return "AMD Ryzen 3"
        
        return texto[:20] + "..." if len(texto) > 20 else texto


def calcular_logica_pura(nome_jogo):
    #Busca
    appid = buscar_appid_por_nome(nome_jogo)
    if not appid: return {"erro": "Jogo não encontrado."}
    
    detalhes = buscar_detalhes_jogo(appid)
    if not detalhes: return {"erro": "Sem requisitos."}

    req_txt_bruto = detalhes.get("requisitos", " ")

    req_txt = re.sub(r'<.*?>', ' ', req_txt_bruto)
    
    #Dados do PC
    info_pc = pegar_info_pc()
    cmd_pc = obter_cmd()

    # Extração dos Requisitos
    ram_min = extrair_ram(req_txt) or 2 # Se falhar, assume 2GB
    
    # Tratamento do Disco
    dados_disco = extrair_disco(req_txt)
    if isinstance(dados_disco, dict): 
        disco_min = dados_disco.get("minimum", 0)
    else:
        try: disco_min = int(str(dados_disco).replace("GB", "").strip())
        except: disco_min = 0

    #Cálculo de Pontos
    pontos = 0
    max_pts = 0
    flags = {"ram": False, "sto": False, "cpu": False, "gpu": False}

    # RAM (Peso 2)
    max_pts += 2
    if info_pc["ram"] >= ram_min:
        pontos += 2
        flags["ram"] = True
    elif ram_min > 0:
        pontos += 2 * (info_pc["ram"] / ram_min)
    
    # Disco (Peso 1)
    max_pts += 1
    if info_pc["disco"] >= disco_min:
        pontos += 1
        flags["sto"] = True
    
    # CPU (Peso 3) 
    max_pts += 3
    cpu_jogo = extrair_cpu(req_txt)
    n_cpu_pc = nivel_cpu(cmd_pc.get("cpu", "")) or 1 # Seu PC nunca é 0
    
    if cpu_jogo:
        n_cpu_jg = nivel_cpu(cpu_jogo) or 3
    else:
        n_cpu_jg = 3 # Assume requisito médio se falhar a leitura
        
    if n_cpu_pc >= n_cpu_jg:
        pontos += 3
        flags["cpu"] = True
    elif n_cpu_pc == n_cpu_jg - 1:
        pontos += 1.5

    # GPU 
    max_pts += 4
    n_gpu_pc = nivel_gpu(cmd_pc.get("gpu", "")) or 1
    
    # Tenta ler do texto. Se falhar (retornar 0), assume Nível 3 (GTX média)
    n_gpu_jg = nivel_gpu(req_txt)
    if n_gpu_jg == 0: n_gpu_jg = 3 
    
    if n_gpu_pc >= n_gpu_jg:
        pontos += 4
        flags["gpu"] = True
    elif n_gpu_pc == n_gpu_jg - 1:
        pontos += 2

    # Finaliza Nota
    if max_pts == 0: max_pts = 1
    pct = int((pontos / max_pts) * 100)
    if pct > 100: pct = 100

    # Textos Finais
    def ic(b): return "✅" if b else "❌"
    
    # Formata a string de descrição (corrige o erro KeyError: 'descricao')
    desc_limpa = req_txt.strip()
    if len(desc_limpa) > 300: 
        desc_limpa = desc_limpa[:300] + "..."

    # Formata os detalhes
    detalhes_txt = f"RAM {ic(flags['ram'])} | DISCO {ic(flags['sto'])} | CPU {ic(flags['cpu'])} | GPU {ic(flags['gpu'])}"

    cpu_nome = busca_simples(req_txt,["Processor", "Processador", "cpu", "CPU"])
    gpu_nome = busca_simples(req_txt,["Graphics", "Video Card", "Placa de vídeo", "Video card", "Placa gráfica", "Vídeo", "Video", "Placa grafica"])

    return {
        "porcentagem": pct,
        "detalhes": detalhes_txt,
        "descricao": desc_limpa,
        "req": {
            "ram": f"{ram_min} GB",
            "cpu": cpu_nome if cpu_nome else "Não indetificada",
            "gpu": gpu_nome if gpu_nome else "Não indetificada",
            "disco": f"{disco_min} GB",
            "os": "Windows"
        }
    }

def busca_simples(texto, palavras_chave):
    if not texto: return None
    
    # Substitui br e li por quebra de linha
    texto_tratado = re.sub(r'(<br\s*/?>|<li>|</li>|<ul>|<div>)', '\n', texto)
    # Remove qualquer outra tag <p>, <b>, etc.
    texto_tratado = re.sub(r'<.*?>', '', texto_tratado)

    
    linhas = texto_tratado.split('\n')
    
    for linha in linhas:
        linha_min = linha.lower().strip()
        for p in palavras_chave:
            if p.lower() in linha_min:
                if ":" in linha:
                    # Pega tudo que vem depois do ":"
                    info = linha.split(":", 1)[1].strip()

                    # Se a linha for muito grande, corta no ponto final
                    if "." in info and len(info) > 50:
                        info = info.split(".")[0]

                    if len(info) > 2:
                        return info

    return None #Só retorna None depois de verificar todas as linhas

if __name__ == "__main__":
    app = GameCompatibilityPro()
    app.mainloop()
