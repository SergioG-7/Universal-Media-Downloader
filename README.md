# YouTube MP3 Downloader & Zipper

Un script de Python diseñado para descargar música de YouTube (videos individuales o listas de reproducción completas), convertir el audio a formato MP3 y empaquetar todas las canciones automáticamente en un único archivo ZIP. 

Ideal para hacer copias de seguridad de listas de reproducción largas de forma rápida y ordenada.

## Caracteristicas

* **Soporte para Playlists:** Pega el enlace de un video único o de una lista de reproducción entera; el script se encarga del resto.
* **Conversión a MP3:** Extrae el audio y lo convierte a formato MP3 de alta calidad (192 kbps).
* **Empaquetado automático:** Al terminar, agrupa todas las canciones descargadas en un único archivo `musica_descargada.zip`.
* **Auto-instalación de dependencias:** Si el usuario no tiene la librería `yt-dlp`, el script intentará instalarla automáticamente al ejecutarse.
* **Reporte de errores:** Si alguna canción falla (por estar oculta, borrada o geobloqueada), el programa continúa con las demás y al final muestra un resumen detallado de qué falló y por qué.
* **Limpieza inteligente:** Borra los archivos temporales una vez comprimidos para no ocupar espacio innecesario en tu disco duro.

## Requisitos Previos

Para que este script funcione correctamente, necesitas tener instalado en tu sistema:

**Python 3.x**
