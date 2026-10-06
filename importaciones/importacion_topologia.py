import io
import urllib.request
from getpass import getpass

import paramiko
from netmiko import ConnectHandler


# =========================
# COMPATIBILIDAD SSH (GNS3 / Paramiko Moderno)
# =========================
from paramiko.transport import Transport

legacy_kex = [
    "diffie-hellman-group1-sha1",
    "diffie-hellman-group14-sha1",
    "diffie-hellman-group-exchange-sha1"
]

for k in legacy_kex:
    if k not in Transport._kex_info and "diffie-hellman-group14-sha1" in Transport._kex_info:
        Transport._kex_info[k] = Transport._kex_info["diffie-hellman-group14-sha1"]
    if k in Transport._kex_info and k not in Transport._preferred_kex:
        Transport._preferred_kex += (k,)


# GitHub
BASE = (
    "https://raw.githubusercontent.com/"
    "vbarraganescudero-tech/configuraciones-router/"
    "main/Router_Topologia/"
)


# Routers y ficheros
ROUTERS = {
    "cisco": ("cisco_ios", "Cisco_Albania.cfg"),
    "mikrotik": ("mikrotik_routeros", "mikrotik.rsc"),
    "vyos": ("vyos", "vyos_argentina.boot"),
    "frr": ("linux", "frr.conf"),
    "junos": ("juniper_junos", "junOS_Australia.conf")
}


# =========================
# DATOS DEL ROUTER
# =========================

router = input(
    "Router (cisco/mikrotik/vyos/frr/junos): "
).lower()

ip = input("IP: ")
usuario = input("Usuario: ")
password = getpass("Contraseña: ")


if router not in ROUTERS:
    print("[ERROR] Router no válido.")
    exit()


tipo, archivo = ROUTERS[router]


# =========================
# DESCARGAR DE GITHUB
# =========================

try:
    texto = urllib.request.urlopen(
        BASE + archivo
    ).read().decode()

    print("[OK] Configuración descargada.")

except Exception as e:
    print("[ERROR] GitHub:", e)
    exit()


# =========================
# CONECTAR
# =========================

try:
    conexion = ConnectHandler(
        device_type=tipo,
        host=ip,
        username=usuario,
        password=password
    )

    print("[OK] Conectado.")


    # ==================================================
    # CISCO (Protegiendo GigabitEthernet0/9)
    # ==================================================

    if router == "cisco":
        lineas = []
        ignorar_banner = False
        ignorar_line = False
        ignorar_eth9 = False

        for linea in texto.splitlines():
            linea_str = linea.strip()

            if not linea_str:
                continue

            # Detectar si el bloque de configuración pertenece a la interfaz 9 (gestión)
            if linea_str.startswith("interface GigabitEthernet0/9") or linea_str.startswith("interface Gi0/9"):
                ignorar_eth9 = True
                continue
            if ignorar_eth9:
                if linea_str.startswith("!") or linea_str.startswith("interface "):
                    ignorar_eth9 = False
                else:
                    continue

            # Ignorar banners y líneas vty de acceso
            if linea_str.startswith("banner "):
                ignorar_banner = True
                continue
            if ignorar_banner:
                if linea_str.startswith("!"):
                    ignorar_banner = False
                continue

            if (
                linea_str.startswith("line con") or
                linea_str.startswith("line aux") or
                linea_str.startswith("line vty")
            ):
                ignorar_line = True
                continue
            if ignorar_line:
                if linea_str.startswith("!"):
                    ignorar_line = False
                continue

            if linea_str == "end" or linea_str.startswith("version ") or linea_str.startswith("!"):
                continue

            lineas.append(linea_str)

        salida = conexion.send_config_set(
            lineas,
            cmd_verify=False,
            read_timeout=60
        )
        print(salida)

        try:
            conexion.save_config()
        except:
            pass


    # ==================================================
    # MIKROTIK (Protegiendo eth9)
    # ==================================================

    elif router == "mikrotik":
        # Filtrar el archivo .rsc para quitar líneas que toquen la interfaz eth9
        lineas_seguras = []
        for linea in texto.splitlines():
            if "eth9" in linea:
                continue  # Omite cualquier comando que afecte a eth9
            lineas_seguras.append(linea)
        
        texto_seguro = "\n".join(lineas_seguras)

        sftp = conexion.remote_conn_pre.open_sftp()
        sftp.putfo(
            io.BytesIO(texto_seguro.encode()),
            "restaurar.rsc"
        )
        sftp.close()

        salida = conexion.send_command_timing(
            "/import file-name=restaurar.rsc",
            read_timeout=180
        )
        print(salida)

        conexion.send_command_timing(
            '/file remove [find name="restaurar.rsc"]'
        )


    # ==================================================
    # VYOS (Protegiendo eth9)
    # ==================================================

    elif router == "vyos":
        conexion.send_command(
            ": > /tmp/config.boot",
            cmd_verify=False
        )

        for linea in texto.splitlines():
            # Si la línea configura ethernet eth9, la omitimos para proteger la gestión
            if "ethernet eth9" in linea:
                continue

            if linea.strip():
                linea_escapada = linea.replace("'", "'\\''")
                conexion.send_command(
                    f"echo '{linea_escapada}' >> /tmp/config.boot",
                    cmd_verify=False
                )

        salida = conexion.send_config_set(
            [
                "load /tmp/config.boot",
                "commit",
                "save"
            ]
        )
        print(salida)


    # ==================================================
    # FRR / ALPINE (Protegiendo eth9)
    # ==================================================

    elif router == "frr":
        lineas_filtradas = []
        saltar_bloque_eth9 = False

        for linea in texto.splitlines():
            if "interface eth9" in linea:
                saltar_bloque_eth9 = True
                continue
            if saltar_bloque_eth9 and linea.strip() == "!":
                saltar_bloque_eth9 = False
                continue
            if not saltar_bloque_eth9:
                lineas_filtradas.append(linea)

        texto_seguro = "\n".join(lineas_filtradas)

        conexion.send_command(
            ": > /tmp/frr.conf",
            cmd_verify=False
        )

        for linea in texto_seguro.splitlines():
            if linea.strip():
                linea_escapada = linea.replace("'", "'\\''")
                conexion.send_command(
                    f"echo '{linea_escapada}' >> /tmp/frr.conf",
                    cmd_verify=False
                )

        salida = conexion.send_command(
            "vtysh -f /tmp/frr.conf"
        )
        print(salida)

        conexion.send_command(
            "vtysh -c 'write memory'"
        )


    # ==================================================
    # JUNOS (Usando load merge en vez de override para proteger ge-0/0/9)
    # ==================================================

    elif router == "junos":
        sftp = conexion.remote_conn_pre.open_sftp()
        sftp.putfo(
            io.BytesIO(texto.encode()),
            "/var/tmp/restaurar.conf"
        )
        sftp.close()

        conexion.config_mode()

        # Usamos 'load merge' para fusionar la config de GitHub sin borrar la eth9 actual
        salida = conexion.send_command_timing(
            "load merge /var/tmp/restaurar.conf",
            read_timeout=120
        )
        print(salida)

        salida = conexion.commit(
            read_timeout=120
        )
        print(salida)


    # =========================
    # CERRAR CONEXIÓN
    # =========================
    conexion.disconnect()

    print()
    print("[OK] Proceso terminado con éxito (gestión y eth9 protegidas).")


except Exception as e:
    print()
    print("[ERROR]", e)