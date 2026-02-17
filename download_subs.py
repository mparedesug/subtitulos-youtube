#!/usr/bin/env python3
"""download_subs.py

Descarga subtítulos autogenerados de YouTube en español usando yt-dlp.
Uso mínimo:
  python download_subs.py

Opciones claves:
  --url       URL del vídeo (por defecto: https://youtu.be/tYqehyG2K38)
  --lang      Código de idioma para los subtítulos (por defecto: es)
  --outdir    Carpeta destino (por defecto: downloads)
  --no-convert  No convertir VTT->SRT (por defecto convierte a SRT)
  --plain     Extraer texto plano (sin timestamps) a un archivo .txt
"""
import argparse
import os
import subprocess
import sys
import shutil
import re
import html
from glob import glob
import srt

DEFAULT_URL = "https://youtu.be/tYqehyG2K38"

# Guardar por defecto en la carpeta del proyecto (donde está este script)
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_OUTDIR = SCRIPT_DIR


def build_yt_dlp_cmd(url, lang="es", outdir=DEFAULT_OUTDIR, convert=True):
    outtmpl = os.path.join(outdir, "%(id)s.%(ext)s")
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--skip-download",
        "--write-auto-sub",
        "--sub-lang",
        lang,
        "--output",
        outtmpl,
    ]
    if convert:
        cmd += ["--convert-subs", "srt"]
    # añadir la URL al final para que yt-dlp sepa qué procesar
    cmd += [url]
    return cmd


def find_subfile(outdir, video_id=None, lang="es", ext="srt"):
    pattern = os.path.join(outdir, f"*.{ext}")
    matches = glob(pattern)
    if not matches:
        return None
    if video_id:
        for m in matches:
            if video_id in os.path.basename(m):
                return m
    # fallback: return newest
    return sorted(matches, key=os.path.getmtime, reverse=True)[0]


def extract_plain_from_srt(srt_path, txt_path):
    with open(srt_path, "r", encoding="utf-8") as fh:
        content = fh.read()
    subs = list(srt.parse(content))
    plain = "\n".join(s.content.replace("\n", " ") for s in subs)
    with open(txt_path, "w", encoding="utf-8") as out:
        out.write(plain)


def extract_plain_from_vtt(vtt_path, txt_path):
    """Extractor robusto de texto desde WebVTT:
    - elimina todas las marcas entre `<` y `>` (timestamps embebidos, etiquetas `<c>`, etc.)
    - unescape de entidades HTML
    - normaliza espacios y deduplica líneas consecutivas
    """
    texts = []
    with open(vtt_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            # Saltar cabecera WEBVTT y líneas de timestamps
            if line.upper().startswith("WEBVTT") or "-->" in line:
                continue
            # Omitir índices numéricos
            if line.isdigit():
                continue
            # Eliminar todo lo que esté entre < y > (ej: <00:00:02.840>, <c>..</c>)
            clean = re.sub(r"<[^>]+>", "", line)
            # Deshacer entidades HTML si existen
            clean = html.unescape(clean)
            # Normalizar espacios
            clean = re.sub(r"\s+", " ", clean).strip()
            if not clean:
                continue
            # Evitar duplicados consecutivos
            if len(texts) == 0 or texts[-1] != clean:
                texts.append(clean)
    plain = "\n".join(texts)
    with open(txt_path, "w", encoding="utf-8") as out:
        out.write(plain)


def main():
    ap = argparse.ArgumentParser(
        description="Descargar subtítulos autogenerados (yt-dlp)"
    )
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--lang", default="es", help="Código de idioma (ej: es)")
    ap.add_argument(
        "--outdir",
        default=DEFAULT_OUTDIR,
        help=f"Carpeta destino (por defecto: {DEFAULT_OUTDIR})",
    )
    ap.add_argument(
        "--no-convert",
        dest="convert",
        action="store_false",
        help="No convertir subtítulos a SRT",
    )
    ap.add_argument(
        "--plain", metavar="OUT.txt", help="Generar texto plano sin timestamps"
    )
    ap.add_argument(
        "--keep-subs",
        action="store_true",
        help="Conservar archivos de subtítulos después de extraer texto plano (por defecto se borran).",
    )
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # Comprobar disponibilidad de ffmpeg y adaptar si hace falta
    has_ffmpeg = shutil.which("ffmpeg") is not None
    if args.convert and not has_ffmpeg:
        print(
            "Aviso: ffmpeg no encontrado, se omitirá la conversión a SRT y se usará VTT si está disponible."
        )
        convert_flag = False
    else:
        convert_flag = args.convert

    cmd = build_yt_dlp_cmd(
        args.url, lang=args.lang, outdir=args.outdir, convert=convert_flag
    )
    print("Ejecutando:", " ".join(cmd))
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(
            "Advertencia: yt-dlp devolvió código",
            res.returncode,
            "- intentaré localizar subtítulos si están presentes.",
        )

    # intentar localizar subtítulos (.srt preferido si se convirtió, si no usar .vtt)
    ext_candidates = []
    if convert_flag:
        ext_candidates.append("srt")
    ext_candidates.append("vtt")

    # intentar extraer id del url (parte después de último '/')
    video_id = args.url.strip().split("/")[-1]
    subfile = None
    chosen_ext = None
    for ext in ext_candidates:
        subfile = find_subfile(args.outdir, video_id=video_id, lang=args.lang, ext=ext)
        if subfile:
            chosen_ext = ext
            break

    if not subfile:
        print("No se encontró archivo de subtítulos (revisa la carpeta).")
        if res.returncode != 0:
            sys.exit(res.returncode)
        return

    print(f"Subtítulos guardados en: {subfile}")

    if args.plain:
        txt_path = args.plain
        if not txt_path.lower().endswith(".txt"):
            txt_path += ".txt"
        if chosen_ext == "srt":
            extract_plain_from_srt(subfile, txt_path)
        else:
            extract_plain_from_vtt(subfile, txt_path)
        print(f"Texto plano extraído a: {txt_path}")

        # Por defecto, si se pidió --plain, eliminar el archivo de subtítulos intermedio
        if not args.keep_subs:
            try:
                os.remove(subfile)
                print(f"Archivo de subtítulos eliminado: {subfile}")
            except Exception as e:
                print(f"No se pudo eliminar {subfile}:", e)


if __name__ == "__main__":
    main()
