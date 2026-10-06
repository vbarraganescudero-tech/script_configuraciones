#!/usr/bin/env python3
"""
enlaces_malla.py
Configura los enlaces nuevos de la malla completa en los cinco
routers de la topología en A, en doble pila (IPv4 + IPv6) y con OSPFv2/OSPFv3.

Autora: Noelia López Poyatos - ASIR - Servicios en Red

Uso:
    python scripts/enlaces_malla.py
    python scripts/enlaces_malla.py Albania
"""

import sys
from datetime import datetime
from pathlib import Path

from netmiko import ConnectHandler


# ---------------------------------------------------------------------------
# Enlaces nuevos de la malla
#
# L1  Albania  - Australia   10.255.255.16/30   2021:16:17:14::/64
# L2  Albania  - Argentina   10.255.255.20/30   2021:16:17:15::/64
# L3  Albania  - Angola      10.255.255.24/30   2021:16:17:16::/64
# L4  Andorra  - Australia   10.255.255.28/30   2021:16:17:17::/64
# L5  Andorra  - Argentina   10.255.255.32/30   2021:16:17:18::/64
# L6  Angola   - Australia   10.255.255.36/30   2021:16:17:19::/64
# ---------------------------------------------------------------------------


# Albania (Cisco): G2 -> Australia, G3 -> Argentina, G4 -> Angola
ALBANIA = {
    "nombre": "Albania",
    "conexion": {
        "device_type": "cisco_ios",
        "host": "192.168.122.2",
        "username": "admin",
        "password": "admin123",
    },
    "comandos": [
        "interface GigabitEthernet0/2",
        " description Hacia Australia (L1)",
        " ip address 10.255.255.17 255.255.255.252",
        " ipv6 address 2021:16:17:14::1/64",
        " ip ospf 1 area 0",
        " ipv6 ospf 1 area 0",
        " no shutdown",
        "interface GigabitEthernet0/3",
        " description Hacia Argentina (L2)",
        " ip address 10.255.255.21 255.255.255.252",
        " ipv6 address 2021:16:17:15::1/64",
        " ip ospf 1 area 0",
        " ipv6 ospf 1 area 0",
        " no shutdown",
        "interface GigabitEthernet0/4",
        " description Hacia Angola (L3)",
        " ip address 10.255.255.25 255.255.255.252",
        " ipv6 address 2021:16:17:16::1/64",
        " ip ospf 1 area 0",
        " ipv6 ospf 1 area 0",
        " no shutdown",
    ],
}


# Andorra (MikroTik): ether4 -> Australia, ether5 -> Argentina
ANDORRA = {
    "nombre": "Andorra",
    "conexion": {
        "device_type": "mikrotik_routeros",
        "host": "192.168.122.3",
        "username": "admin",
        "password": "Victortk123",
    },
    "comandos": [
        ':if ([:len [/ip address find address="10.255.255.29/30"]] = 0) do={',
        '/ip address add address=10.255.255.29/30 interface=ether4 comment="L4 Australia"}',
        ':if ([:len [/ipv6 address find address="2021:16:17:17::1/64"]] = 0) do={',
        '/ipv6 address add address=2021:16:17:17::1/64 interface=ether4 advertise=no}',
        ':if ([:len [/ip address find address="10.255.255.33/30"]] = 0) do={',
        '/ip address add address=10.255.255.33/30 interface=ether5 comment="L5 Argentina"}',
        ':if ([:len [/ipv6 address find address="2021:16:17:18::1/64"]] = 0) do={',
        '/ipv6 address add address=2021:16:17:18::1/64 interface=ether5 advertise=no}',
    ],
}


# Angola (Cisco): G4 -> Albania, G3 -> Australia
ANGOLA = {
    "nombre": "Angola",
    "conexion": {
        "device_type": "cisco_ios",
        "host": "192.168.122.4",
        "username": "admin",
        "password": "admin123",
    },
    "comandos": [
        "interface GigabitEthernet0/4",
        " description Hacia Albania (L3)",
        " ip address 10.255.255.26 255.255.255.252",
        " ipv6 address 2021:16:17:16::2/64",
        " ip ospf 1 area 0",
        " ipv6 ospf 1 area 0",
        " no shutdown",
        "interface GigabitEthernet0/3",
        " description Hacia Australia (L6)",
        " ip address 10.255.255.37 255.255.255.252",
        " ipv6 address 2021:16:17:19::1/64",
        " ip ospf 1 area 0",
        " ipv6 ospf 1 area 0",
        " no shutdown",
    ],
}


# Argentina (VyOS): eth4 -> Albania, eth5 -> Andorra
ARGENTINA = {
    "nombre": "Argentina",
    "conexion": {
        "device_type": "vyos",
        "host": "192.168.122.5",
        "username": "vyos",
        "password": "vyos",
    },
    "comandos": [
        "set interfaces ethernet eth4 address '10.255.255.22/30'",
        "set interfaces ethernet eth4 address '2021:16:17:15::2/64'",
        "set interfaces ethernet eth5 address '10.255.255.34/30'",
        "set interfaces ethernet eth5 address '2021:16:17:18::2/64'",
        "set protocols ospf interface eth4 area '0'",
        "set protocols ospf interface eth4 network 'broadcast'",
        "set protocols ospf interface eth5 area '0'",
        "set protocols ospf interface eth5 network 'broadcast'",
        "set protocols ospfv3 interface eth4 area '0.0.0.0'",
        "set protocols ospfv3 interface eth5 area '0.0.0.0'",
    ],
}


# Australia (Juniper): ge-0/0/3 -> Albania,
# ge-0/0/4 -> Angola, ge-0/0/5 -> Andorra
AUSTRALIA = {
    "nombre": "Australia",
    "conexion": {
        "device_type": "juniper_junos",
        "host": "192.168.122.6",
        "username": "admin",
        "password": "Victortk123",
    },
    "comandos": [
        "set interfaces ge-0/0/3 unit 0 family inet address 10.255.255.18/30",
        "set interfaces ge-0/0/3 unit 0 family inet6 address 2021:16:17:14::2/64",
        "set interfaces ge-0/0/4 unit 0 family inet address 10.255.255.38/30",
        "set interfaces ge-0/0/4 unit 0 family inet6 address 2021:16:17:19::2/64",
        "set interfaces ge-0/0/5 unit 0 family inet address 10.255.255.30/30",
        "set interfaces ge-0/0/5 unit 0 family inet6 address 2021:16:17:17::2/64",
        "set protocols ospf area 0.0.0.0 interface ge-0/0/3.0",
        "set protocols ospf area 0.0.0.0 interface ge-0/0/4.0",
        "set protocols ospf area 0.0.0.0 interface ge-0/0/5.0",
        "set protocols ospf3 area 0.0.0.0 interface ge-0/0/3.0",
        "set protocols ospf3 area 0.0.0.0 interface ge-0/0/4.0",
        "set protocols ospf3 area 0.0.0.0 interface ge-0/0/5.0",
    ],
}


# ---------------------------------------------------------------------------
# Funciones de configuración
# ---------------------------------------------------------------------------

def configurar_cisco(conn, comandos):
    salida = conn.send_config_set(comandos)
    salida += conn.save_config()
    return salida


def configurar_mikrotik(conn, comandos):
    salida = ""
    for comando in comandos:
        salida += f"\n> {comando}\n"
        salida += conn.send_command_timing(comando)
    return salida


def configurar_junos(conn, comandos):
    salida = conn.send_config_set(comandos, exit_config_mode=False)
    salida += conn.commit()
    salida += conn.exit_config_mode()
    return salida


def configurar_vyos(conn, comandos):
    salida = conn.send_config_set(comandos, exit_config_mode=False)
    salida += conn.send_command("commit")
    salida += conn.send_command("save")
    salida += conn.exit_config_mode()
    return salida


FUNCIONES = {
    "cisco_ios": configurar_cisco,
    "mikrotik_routeros": configurar_mikrotik,
    "juniper_junos": configurar_junos,
    "vyos": configurar_vyos,
}


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def main():
    carpeta_logs = Path(__file__).resolve().parent.parent / "logs"
    carpeta_logs.mkdir(exist_ok=True)
    fecha = datetime.now().strftime("%Y%m%d-%H%M")
    fichero_log = carpeta_logs / f"enlaces_malla_{fecha}.log"

    todos = [ALBANIA, ANDORRA, ANGOLA, ARGENTINA, AUSTRALIA]

    elegidos = [n.lower() for n in sys.argv[1:]]
    routers = [
        r for r in todos
        if not elegidos or r["nombre"].lower() in elegidos
    ]

    resumen = []

    with open(fichero_log, "w", encoding="utf-8") as log:
        for router in routers:
            nombre = router["nombre"]
            tipo = router["conexion"]["device_type"]

            print(f"\n=== {nombre} ({router['conexion']['host']}) ===")
            log.write(f"\n===== {nombre} =====\n")

            try:
                with ConnectHandler(**router["conexion"]) as conn:
                    salida = FUNCIONES[tipo](conn, router["comandos"])

                print(salida)
                log.write(salida + "\n")
                resumen.append((nombre, "OK"))

            except Exception as error:
                print(f"ERROR en {nombre}: {error}")
                log.write(f"ERROR: {error}\n")
                resumen.append((nombre, f"ERROR: {error}"))

    print("\n===== RESUMEN =====")

    for nombre, estado in resumen:
        print(f"{nombre:10} {estado}")

    print(f"\nRegistro guardado en: {fichero_log}")


if __name__ == "__main__":
    main()