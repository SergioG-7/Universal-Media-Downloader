# YouTube MP3 Downloader & Zipper

CLI optimizada en Python para descargar audio de videos individuales o listas de reproducción de YouTube, convertirlo automáticamente a formato MP3 (192 kbps) y empaquetar todas las pistas en un único archivo ZIP de forma limpia y ordenada.

## Características

* **Soporte Completo para Playlists:** Procesa enlaces simples o listas de reproducción completas con extracción de metadatos en segundo plano.
* **Conversión Automática:** Extracción y transcodificación directa a MP3 (192 kbps) mediante binarios integrados de FFmpeg.
* **Manejo Seguro de Archivos:** Limpieza atómica mediante directorios temporales (`tempfile`); no deja archivos residuales si la ejecución se cancela.
* **Resiliencia ante Fallos:** Si una pista de la playlist está bloqueada, eliminada o privada, el proceso continúa y genera un reporte detallado de errores al finalizar.
* **Doble Modo de Uso:** Funciona como interfaz de comandos (CLI) con parámetros o en modo interactivo guiado por consola.

## Requisitos Previos

* Python 3.9 o superior.
* Conexión a internet estable.

## Instalación

1. Clona este repositorio:
```bash
git clone [https://github.com/tu-usuario/youtube-mp3-zipper.git](https://github.com/tu-usuario/youtube-mp3-zipper.git)
cd youtube-mp3-zipper
