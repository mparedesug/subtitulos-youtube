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

- Levantar el servidor Flask (puerto por defecto: 5000):
  - Activando el virtualenv (PowerShell):
    ```powershell
    .\.venv\Scripts\Activate.ps1
    python app.py
    ```
    Si se experimenta algún problema con la política de ejecución de PowerShell, se puede ejecutar previamente `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` para permitir la ejecución de scripts en esa sesión.

  - CMD:
    ```cmd 
    .\.venv\Scripts\activate.bat
    python app.py
    ```

  - Ejecutar en otro puerto (ej. 5001):
    - PowerShell: `$env:PORT=5001; python app.py`
    - CMD: `set PORT=5001 && python app.py`

- Comprobar en el navegador:
  - Abre `http://localhost:5000` (o `http://localhost:5001` si cambiaste el puerto), pega la URL del vídeo cuyos subtítulos quieras obtener en la caja y pulsa **Obtener subtítulos**. Por defecto, aparece la URL del ejemplo: `https://youtu.be/tYqehyG2K38`, pero se puede probar con cualquier otra URL de YouTube, como por ejemplo `https://www.youtube.com/watch?v=onpLmf3977o`.

NOTAS:
- El script usa `yt-dlp` (instalado en el virtualenv) invocado como `python -m yt_dlp` para mayor portabilidad.
- Si YouTube devuelve HTTP 429 al solicitar subtítulos automáticos (ver https://github.com/yt-dlp/yt-dlp/issues/13831), puedes intentar:
  - pasar cookies actualizadas de navegador a yt-dlp, o
  - aumentar el parámetro sleep_subtitles (por ejemplo 60s) al hacer la petición.
- `--write-auto-sub` descarga subtítulos automáticos; si no existen, no se generará archivo.
