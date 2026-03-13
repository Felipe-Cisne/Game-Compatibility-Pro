import platform
import psutil

def pegar_info_pc():
    ram_pc = int(psutil.virtual_memory().total / (1024 ** 3))
    disco_pc = int(psutil.disk_usage("C:\\").total / (1024 ** 3))
    so = platform.system()

    return {
        "ram": ram_pc,
        "disco": disco_pc,
        "so": so
    }
