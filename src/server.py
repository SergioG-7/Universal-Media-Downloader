import http.server
import socket
import socketserver
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


def servir_archivo_y_mostrar_qr(ruta_archivo: Path, puerto: int = 8000) -> None:
    ip = obtener_ip_local()
    url_descarga = f"http://{ip}:{puerto}/{ruta_archivo.name}"
    directorio_padre = str(ruta_archivo.parent)

    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directorio_padre, **kwargs)

        def log_message(self, format, *args):
            pass

    qr = qrcode.QRCode(border=1)
    qr.add_data(url_descarga)
    qr.make(fit=True)

    print("\n" + "=" * 50)
    print("TRANSFERENCIA LOCAL (MOVIL / LAN)")
    print("=" * 50)
    print(f"[*] Conecta tu movil a la misma red Wi-Fi.")
    print(f"[*] Escanea el codigo QR o accede a: {url_descarga}\n")

    qr.print_ascii(invert=True)
    print("\n[*] Servidor activo. Presiona Ctrl+C cuando finalice la descarga en tu movil.")

    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", puerto), CustomHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Servidor local cerrado correctamente.")
    except Exception as e:
        print(f"[-] Error en el servidor: {e}")