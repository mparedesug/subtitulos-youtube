#!/usr/bin/env python3
"""Flask app to fetch YouTube auto-subtitles using yt-dlp and return plain text.

Endpoints:
- GET /       -> simple HTML UI
- POST /api/captions -> { url: string, lang?: 'es', sleep_subtitles?: int }

The server listens on host 0.0.0.0 and port defined by the PORT env var (default 5000).

Notes about YouTube subtitles and 429 issues (see https://github.com/yt-dlp/yt-dlp/issues/13831):
- Avoid requesting auto-translated subtitles, prefer the video's original language.
- If you hit HTTP 429: options include passing fresh cookies or increasing sleep_subtitles (e.g. 60s).
"""
import os
import tempfile
import shutil
import json
from glob import glob
from flask import Flask, request, jsonify, send_from_directory, render_template
from yt_dlp import YoutubeDL

# reuse helpers from download_subs
from download_subs import extract_plain_from_vtt, extract_plain_from_srt

app = Flask(__name__, static_folder="static", template_folder="templates")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/captions", methods=["POST"])
def captions_api():
    data = request.get_json() or {}
    url = data.get("url")
    lang = data.get("lang", "es")
    sleep_subtitles = data.get("sleep_subtitles")  # optional int

    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    tmpdir = tempfile.mkdtemp(prefix="ytcaps_")
    try:
        # prepare ydl options
        outtmpl = os.path.join(tmpdir, "%(id)s.%(ext)s")
        ydl_opts = {
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": [lang],
            "skip_download": True,
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
            # avoid auto-translated subs where possible
            "extractor_args": {"youtube": "skip=translated_subs"},
        }
        if sleep_subtitles:
            try:
                ydl_opts["sleep_subtitles"] = int(sleep_subtitles)
            except Exception:
                pass

        # prefer srt if ffmpeg available
        import shutil as _sh

        if _sh.which("ffmpeg"):
            ydl_opts["subtitlesformat"] = "srt"
            ydl_opts["convertsubtitles"] = "srt"

        with YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except Exception as e:
                # handle known 429 case
                msg = str(e)
                note = None
                if "429" in msg or "Too Many Requests" in msg:
                    note = "Warning: YouTube returned 429. Try passing fresh cookies or increasing sleep_subtitles (e.g. 60)."
                # continue to try to find any subtitles written

        # locate downloaded subtitle file
        candidates = glob(os.path.join(tmpdir, "*.*"))
        subfile = None
        chosen_ext = None
        for ext in ("srt", "vtt"):
            for c in candidates:
                if c.lower().endswith("." + ext):
                    subfile = c
                    chosen_ext = ext
                    break
            if subfile:
                break

        if not subfile:
            return (
                jsonify(
                    {
                        "error": "No subtitles found",
                        "note": "Try --sleep_subtitles or pass fresh cookies",
                    }
                ),
                502,
            )

        # read and extract plain text
        txt_path = os.path.join(tmpdir, "out.txt")
        if chosen_ext == "srt":
            extract_plain_from_srt(subfile, txt_path)
        else:
            extract_plain_from_vtt(subfile, txt_path)

        with open(txt_path, "r", encoding="utf-8") as fh:
            text = fh.read()

        resp = {"ok": True, "lang": lang, "text": text}
        if "note" in locals() and note:
            resp["note"] = note
        return jsonify(resp)

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
