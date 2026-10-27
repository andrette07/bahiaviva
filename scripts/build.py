#!/usr/bin/env python3
"""Build site/index.html from src/template.html + src/stops.js + src/img/*.jpg.

Usage:  python3 scripts/build.py
Edit card content in src/stops.js, styles/markup in src/template.html, then rebuild.
Only images whose id appears in STOPS (plus maqueta.jpg) are embedded.
Recordings in src/audio/<id>.mp3 (and inicio.mp3) are copied to site/audio/ and played instead of voice synthesis.
"""
import base64, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "site" / "index.html"

template = (SRC / "template.html").read_text(encoding="utf-8")
stops = (SRC / "stops.js").read_text(encoding="utf-8").strip()

# 1. splice the STOPS array into the template
template, n = re.subn(r"const STOPS = \[.*?\n\];", lambda m: stops, template, flags=re.S)
assert n == 1, "STOPS block not found in template.html"

# 2. embed images as data URIs (only the ones used)
ids = re.findall(r"\{ id: '(\w+)'", stops)
def data_uri(name):
    p = SRC / "img" / f"{name}.jpg"
    if not p.exists():
        raise SystemExit(f"Missing image src/img/{name}.jpg for card id '{name}'")
    return "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode()

html = template.replace("{{IMG:maqueta}}", data_uri("maqueta"))
html = html.replace("{{IMGMAP}}", json.dumps({i: data_uri(i) for i in ids}))

# 2b. students' recordings: src/audio/<id>.mp3 -> site/audio/<id>.mp3 (loaded on demand, not inlined)
import shutil
audio_src = SRC / "audio"
audio_out = OUT.parent / "audio"
if audio_out.exists():
    shutil.rmtree(audio_out)
audio_ids = []
if audio_src.exists():
    audio_out.mkdir()
    for f in sorted(audio_src.glob("*.mp3")):
        shutil.copy2(f, audio_out / f.name)
        audio_ids.append(f.stem)
unknown = [a for a in audio_ids if a not in ids and a != "inicio"]
if unknown:
    raise SystemExit(f"Audio without a matching card id: {unknown}")
html = html.replace("{{AUDIO}}", json.dumps(audio_ids))
assert "{{" not in html, "unreplaced placeholder left in template"

# 3. wrap as a standalone document (template is a body fragment)
doc = ('<!doctype html>\n<html lang="es"><head><meta charset="utf-8">'
       '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
       '</head><body>\n' + html + '\n</body></html>\n')
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(doc, encoding="utf-8")
print(f"Built {OUT.relative_to(ROOT)}  ({len(doc)//1024} KB, {len(ids)} cards: {', '.join(ids)})")
missing = [i for i in ids if i not in audio_ids]
print(f"Audio: {len(audio_ids)} files in site/audio" + (f"; cards without recording (use voice synth): {', '.join(missing)}" if missing else ""))
