# CLI_YouTube — descarga subtítulos autogenerados

Script mínimo para descargar subtítulos autogenerados de YouTube en español usando `yt-dlp`.

Instalación (usando el virtualenv creado por VS Code):

- Asegúrate de usar el entorno Python del proyecto (o activa `.venv`):
  & "./.venv/Scripts/Activate.ps1" (PowerShell)
- Instala dependencias: `python -m pip install -r requirements.txt`

Uso:

- Descargar subtítulos (SRT convertido por defecto y guardado en la carpeta del proyecto):
  `python download_subs.py`

- Especificar otra URL o carpeta:
  `python download_subs.py --url "https://youtu.be/VIDEO_ID" --outdir mysubs`

- Extraer texto plano sin timestamps (por defecto elimina el archivo de subtítulos intermedio):
  `python download_subs.py --plain subs.txt`

- Mantener subtítulos además del `.txt` (no los borra):
  `python download_subs.py --plain subs.txt --keep-subs`

Web app demo
------------

- Levantar servidor Flask (usa `PORT` si quieres cambiar el puerto):
  `PORT=8000 python app.py`

- Abre http://localhost:8000 y pega la URL del vídeo, pulsa "Obtener subtítulos".

Notes:
- El script usa `yt-dlp` (instalado en el virtualenv) invocado como `python -m yt_dlp` para mayor portabilidad.
- Si YouTube devuelve HTTP 429 al solicitar subtítulos automáticos (ver https://github.com/yt-dlp/yt-dlp/issues/13831), puedes intentar:
  - pasar cookies actualizadas de navegador a yt-dlp, o
  - aumentar el parámetro sleep_subtitles (por ejemplo 60s) al hacer la petición.
- `--write-auto-sub` descarga subtítulos automáticos; si no existen, no se generará archivo.
