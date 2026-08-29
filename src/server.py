import http.server
import socket
import socketserver
import time
from pathlib import Path
import qrcode


def obtener_ip_local() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def servir_archivo_y_mostrar_qr(ruta_archivo: Path, puerto: int = 8000, timeout_seg: int = 600) -> None:
    ip = obtener_ip_local()
    url_descarga = f"http://{ip}:{puerto}/{ruta_archivo.name}"
    directorio_padre = str(ruta_archivo.parent)
    nombre_archivo = ruta_archivo.name

    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directorio_padre, **kwargs)

        def log_message(self, format, *args):
            pass

        def do_GET(self):
            # Solo se sirve el archivo compartido, no el resto del directorio
            if self.path.lstrip("/") != nombre_archivo:
                self.send_error(404, "No encontrado")
                return
            super().do_GET()
            self.server.descarga_completa = True

    qr = qrcode.QRCode(border=1)
    qr.add_data(url_descarga)
    qr.make(fit=True)

    print("\n" + "=" * 50)
    print("TRANSFERENCIA LOCAL (MOVIL / LAN)")
    print("=" * 50)
    print(f"[*] Conecta tu movil a la misma red Wi-Fi.")
    print(f"[*] Escanea el codigo QR o accede a: {url_descarga}\n")

    qr.print_ascii(invert=True)
    print(f"\n[*] Servidor activo (se cierra solo tras la descarga o a los {timeout_seg}s). Ctrl+C para cancelar.")

    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer((ip, puerto), CustomHandler) as httpd:
            httpd.descarga_completa = False
            httpd.timeout = timeout_seg
            limite = time.monotonic() + timeout_seg
            while not httpd.descarga_completa and time.monotonic() < limite:
                httpd.handle_request()
        print("\n[*] Servidor local cerrado correctamente.")
    except KeyboardInterrupt:
        print("\n[*] Servidor local cerrado correctamente.")
    except Exception as e:
        print(f"[-] Error en el servidor: {e}")