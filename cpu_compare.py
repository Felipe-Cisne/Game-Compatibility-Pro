def nivel_cpu(nome_cpu: str) -> int:
    nome = nome_cpu.lower()

    if "celeron" in nome or "pentium" in nome or "core 2" in nome:
        return 1
    if "i3" in nome or "ryzen 3" in nome:
        return 2
    if "i5" in nome or "ryzen 5" in nome:
        return 3
    if "i7" in nome or "ryzen 7" in nome:
        return 4
    if "i9" in nome or "ryzen 9" in nome or "xeon" in nome:
        return 5

    return 1  



def comparar_cpu(cpu_pc: str, cpu_jogo: str) -> int:
    nivel_pc = nivel_cpu(cpu_pc)
    nivel_jogo = nivel_cpu(cpu_jogo)

    if nivel_pc >= nivel_jogo:
        return 100
    else:
        return int((nivel_pc / nivel_jogo) * 100)
