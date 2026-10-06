#!/usr/bin/env python3

import os
import subprocess
from datetime import datetime

CARPETA = "configuraciones"
os.makedirs(CARPETA, exist_ok=True)

routers = [
    {
        "nombre": "Albania",
        "ip": "192.168.122.2",
        "usuario": "victor",
        "fichero": "/home/victor/cisco.cfg",
        "destino": "Albania.cfg"
    },
    {
        "nombre": "Andorra",
        "ip": "192.168.122.3",
        "usuario": "victor",
        "fichero": "/home/victor/mikrotik.rsc",
        "destino": "Andorra.rsc"
    },
    {
        "nombre": "Angola",
        "ip": "192.168.122.4",
        "usuario": "victor",
        "fichero": "/home/victor/cisco.cfg",
        "destino": "Angola.cfg"
    },
    {
        "nombre": "Argentina",
        "ip": "192.168.122.5",
        "usuario": "victor",
        "fichero": "/home/victor/config.boot",
        "destino": "Argentina.config.boot"
    },
    {
        "nombre": "Australia",
        "ip": "192.168.122.6",
        "usuario": "victor",
        "fichero": "/home/victor/config",
        "destino": "Australia.config"
    }
]

fecha = datetime.now().strftime("%Y%m%d_%H%M%S")

print("\n=== COPIA DE CONFIGURACIONES ===\n")

for router in routers:

    print(f"=== {router['nombre']} ({router['ip']}) ===")

    destino = os.path.join(
        CARPETA,
        f"{router['destino']}_{fecha}"
    )

    comando = [
        "scp",
        "-O",
        f"{router['usuario']}@{router['ip']}:{router['fichero']}",
        destino
    ]

    resultado = subprocess.run(comando)

    if resultado.returncode == 0:
        print(f"OK: {destino}\n")
    else:
        print(f"ERROR al copiar {router['nombre']}\n")

print("=== FIN ===")