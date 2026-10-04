import io
import urllib.request
from getpass import getpass

import paramiko
from netmiko import ConnectHandler


# Compatibilidad SSH
for k in (
    "diffie-hellman-group14-sha1",
    "diffie-hellman-group-exchange-sha1"
):
    if k in paramiko.Transport._kex_info:
        if k not in paramiko.Transport._preferred_kex:
            paramiko.Transport._preferred_kex += (k,)


# GitHub
BASE = (
    "https://raw.githubusercontent.com/"
    "vbarraganescudero-tech/configuraciones-router/"
    "main/Router_monitorización/"
)


# Routers y ficheros
ROUTERS = {
    "cisco": ("cisco_ios", "router.cfg"),
    "mikrotik": ("mikrotik_routeros", "mikrotik.rsc"),
    "vyos": ("vyos", "config.boot"),
    "frr": ("linux", "frr.conf"),
}


# =========================
# DATOS DEL ROUTER
# =========================

router = input(
    "Router (cisco/mikrotik/vyos/frr): "
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
    # CISCO
    # ==================================================

    if router == "cisco":

        lineas = []

        ignorar_banner = False
        ignorar_line = False

        for linea in texto.splitlines():

            linea = linea.strip()

            if not linea:
                continue

            # Ignorar banners
            if linea.startswith("banner "):

                ignorar_banner = True
                continue

            if ignorar_banner:

                if linea.startswith("!"):
                    ignorar_banner = False

                continue

            # Ignorar líneas de consola, AUX y VTY
            if (
                linea.startswith("line con") or
                linea.startswith("line aux") or
                linea.startswith("line vty")
            ):

                ignorar_line = True
                continue

            if ignorar_line:

                if linea.startswith("!"):
                    ignorar_line = False

                continue

            # No enviar estos comandos
            if linea == "end":
                continue

            if linea.startswith("version "):
                continue

            if linea.startswith("!"):
                continue

            lineas.append(linea)


        salida = conexion.send_config_set(
            lineas,
            cmd_verify=False
        )

        print(salida)


        try:
            conexion.save_config()
        except:
            pass


    # ==================================================
    # MIKROTIK
    # ==================================================

    elif router == "mikrotik":

        sftp = conexion.remote_conn_pre.open_sftp()

        sftp.putfo(
            io.BytesIO(texto.encode()),
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
    # VYOS
    # ==================================================

    elif router == "vyos":

        conexion.send_command(
            ": > /tmp/config.boot",
            cmd_verify=False
        )


        for linea in texto.splitlines():

            if linea.strip():

                linea = linea.replace(
                    "'",
                    "'\\''"
                )

                conexion.send_command(
                    "echo '" + linea + "' >> /tmp/config.boot",
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
    # FRR
    # ==================================================

    elif router == "frr":

        conexion.send_command(
            ": > /tmp/frr.conf",
            cmd_verify=False
        )


        for linea in texto.splitlines():

            if linea.strip():

                linea = linea.replace(
                    "'",
                    "'\\''"
                )

                conexion.send_command(
                    "echo '" + linea + "' >> /tmp/frr.conf",
                    cmd_verify=False
                )


        salida = conexion.send_command(
            "vtysh -f /tmp/frr.conf"
        )

        print(salida)


        conexion.send_command(
            "vtysh -c 'write memory'"
        )


    # =========================
    # CERRAR CONEXIÓN
    # =========================

    conexion.disconnect()

    print()
    print("[OK] Proceso terminado.")


except Exception as e:

    print()
    print("[ERROR]", e)