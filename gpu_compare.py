def nivel_gpu(nome_gpu: str) -> int:
    nome = nome_gpu.lower()

    if "intel hd" in nome or "uhd" in nome:
        return 1
    if "gt 710" in nome or "gt 730" in nome or "r7" in nome:
        return 2
    if "gtx 750" in nome or "gtx 950" in nome or "gtx 960" in nome:
        return 3
    if "gtx 1050" in nome or "gtx 1060" in nome or "rx 570" in nome:
        return 4
    if "gtx 1660" in nome or "rtx 2060" in nome or "rx 6600" in nome:
        return 5
    if "rtx 3060" in nome or "rtx 3070" in nome or "rtx 3080" in nome:
        return 6

    return 1

def comparar_gpu(gpu_pc: str, gpu_jogo: str) -> int:
    nivel_pc = nivel_gpu(gpu_pc)
    nivel_jogo = nivel_gpu(gpu_jogo)

    if nivel_pc >= nivel_jogo:
        return 100
    
    return int((nivel_pc / nivel_jogo) * 100)