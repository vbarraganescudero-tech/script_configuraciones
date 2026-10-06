#!/usr/bin/env python3

import os
import subprocess
import pexpect
from datetime import datetime

CARPETA = "configuraciones"
os.makedirs(CARPETA, exist_ok=True)

FECHA = datetime.now().strftime("%Y%m%d_%H%M%S")

ROUTERS = {
    "Albania": {
        "ip": "192.168.122.2",
        "usuario": "admin",
        "password": "admin123",
        "tipo": "cisco"
    },

    "Andorra": {
        "ip": "192.168.122.3",
        "usuario": "admin",
        "password": "Victortk123",
        "tipo": "mikrotik"
    },

    "Angola": {
        "ip": "192.168.122.4",
        "usuario": "admin",
        "password": "admin123",
        "tipo": "cisco"
    },

    "Argentina": {
        "ip": "192.168.122.5",
        "usuario": "vyos",
        "password": "vyos",
        "tipo": "vyos"
    },

    "Australia": {
        "ip": "192.168.122.6",
        "usuario": "admin",
        "password": "Victortk123",
        "tipo": "junos"
    }
}


def crear_copia_cisco(router):

    comando = f"ssh -o StrictHostKeyChecking=no {router['usuario']}@{router['ip']}"

    ssh = pexpect.spawn(comando, encoding="utf-8", timeout=15)

    ssh.expect("[Pp]assword:")
    ssh.sendline(router["password"])

    ssh.expect("#")

    ssh.sendline("copy running-config flash:copia.cfg")

    ssh.expect("Destination filename")
    ssh.sendline("")

    indice = ssh.expect([
        r"Do you want to over write\? \[confirm\]",
        r"#"
    ])

    if indice == 0:
        ssh.sendline("")
        ssh.expect("#")

    ssh.sendline("exit")

    try:
        ssh.expect(pexpect.EOF, timeout=5)
    except:
        pass

    ssh.close()


def crear_copia_mikrotik(router):

    comando = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        f"{router['usuario']}@{router['ip']}",
        "/export file=copia"
    ]

    subprocess.run(
        comando,
        input=router["password"] + "\n",
        text=True,
        timeout=20
    )


def copiar_scp(router, remoto, local):

    comando = [
        "scp",
        "-O",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        f"{router['usuario']}@{router['ip']}:{remoto}",
        local
    ]

    proceso = subprocess.run(
        comando,
        input=router["password"] + "\n",
        text=True,
        timeout=30
    )

    return proceso.returncode == 0


def copiar_scp_cisco(router, local):

    # Primero intenta la ruta flash:copia.cfg
    rutas = [
        "flash:copia.cfg",
        "copia.cfg"
    ]

    for remoto in rutas:

        print(f"Probando SCP: {remoto}")

        comando = [
            "scp",
            "-O",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
            f"{router['usuario']}@{router['ip']}:{remoto}",
            local
        ]

        try:

            proceso = subprocess.run(
                comando,
                input=router["password"] + "\n",
                text=True,
                timeout=30
            )

            if proceso.returncode == 0:
                return True

        except subprocess.TimeoutExpired:
            pass

    return False


for nombre, router in ROUTERS.items():

    print(f"\n=== {nombre} ({router['ip']}) ===")

    try:

        if router["tipo"] == "cisco":

            print("Creando copia...")
            crear_copia_cisco(router)

            local = os.path.join(
                CARPETA,
                f"{nombre}_{FECHA}.cfg"
            )

            print("Descargando mediante SCP...")

            if copiar_scp_cisco(router, local):
                print(f"OK -> {local}")
            else:
                print(f"ERROR -> {nombre}")

            continue

        elif router["tipo"] == "mikrotik":

            print("Creando exportación...")
            crear_copia_mikrotik(router)

            remoto = "/copia.rsc"
            local = os.path.join(
                CARPETA,
                f"{nombre}_{FECHA}.rsc"
            )

        elif router["tipo"] == "vyos":

            remoto = "/config/config.boot"
            local = os.path.join(
                CARPETA,
                f"{nombre}_{FECHA}.boot"
            )

        elif router["tipo"] == "junos":

            remoto = "/config/juniper.conf.gz"
            local = os.path.join(
                CARPETA,
                f"{nombre}_{FECHA}.conf.gz"
            )

        print("Descargando mediante SCP...")

        if copiar_scp(router, remoto, local):
            print(f"OK -> {local}")
        else:
            print(f"ERROR -> {nombre}")

    except subprocess.TimeoutExpired:
        print(f"TIMEOUT -> {nombre}")

    except Exception as e:
        print(f"ERROR -> {nombre}: {e}")


print("\n===================================")
print("       COPIAS FINALIZADAS")
print("===================================")