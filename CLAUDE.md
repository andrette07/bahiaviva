# Bahía Viva — school project app

A one-page, phone-first web app in **Spanish** for a **2nd-grade** class project in Colombia: a diorama
("maqueta") of a Colombian Pacific bay titled *Bahía del Pacífico Colombiano — Cuidemos la vida marina*.
Kids tap numbered spots on a photo of their diorama (or scan QR labels stuck next to each animal/sign)
to open a card with a photo, 2–4 short facts, a "¿Cómo lo cuidamos?" line, and a read-aloud button.

Owner: Andrés (uncle). His sister (Spanish only) and the students use it. Talk to Andrés in English;
everything user-facing in the app stays in Spanish.

## Dates
- **Mon Oct 19, 2026** — classroom exhibition: demo runs from the standalone HTML file on an Android phone (already sent).
- **Wed Oct 28, 2026** — presentation to the whole school: needs the public domain + QR labels.

## Layout
```
src/template.html   page markup, CSS tokens, JS (body fragment; STOPS array is replaced at build)
src/stops.js        THE CONTENT — one object per card (id, zone, hotspot x/y %, title, short, facts, care)
src/img/*.jpg       card photos cropped from the family's own diorama photos; maqueta.jpg = map photo
src/audio/<id>.mp3  students' recordings (mono 40 kbps MP3 from the WhatsApp .ogg); inicio.mp3 = home welcome
scripts/build.py    -> site/index.html (single self-contained file, images inlined as data URIs)
scripts/make_qr.py  -> qr/etiquetas-qr-<domain>.pdf (Letter, 3x4 labels) + decode self-check
site/               what gets deployed (index.html, audio/*.mp3, .nojekyll, CNAME)
```
Workflow: edit `src/stops.js` or `src/template.html` → `python3 scripts/build.py` → commit `site/` → deploy.
Never hand-edit `site/index.html`.

Deploy (GitHub Pages serves the `gh-pages` branch, which holds only the contents of `site/`):
```
git subtree push --prefix site origin gh-pages
```
Pages takes ~1 min to publish. Ask Andrés before every deploy.

## Content rules (keep)
- Audience is 7–8 years old: short sentences, simple words, max ~4 facts per card.
- Card ids are part of the QR URLs (`https://<domain>/#<id>`). **Renaming or removing an id breaks printed labels** — if you must, regenerate and reprint the QR sheet.
- Zones follow the class's printed signs: green = Zona 1 *Convivencia sostenible* (artisanal fishing good),
  red = Zona 2 *Prácticas dañinas* (industrial trawling, trash, boats too close to whales, mangrove damage), blue = animals.
- Card list follows the sister's list: ballena jorobada, delfines, conchas, corales, arrecife, pez globo, plus zone cards.
- Extra photo crops in src/img (langosta, pulpo, tiburon, caballito, peces, captura, playa) are unused; add a card back only if asked.
- Facts are sourced (footer of the page). Don't add numbers without a source.

## Hosting (live since 2026-10-18)
- https://bahiaviva.co — GitHub Pages, repo `andrette07/bahiaviva` (public), serving the `gh-pages` branch
  (= contents of `site/`). Custom domain + Enforce HTTPS set; cert valid to 2027-01-16. www → 301 to apex.
- GoDaddy DNS: A @ → 185.199.108/109/110/111.153; CNAME www → andrette07.github.io.
- `gh` has two accounts on this machine; use `andrette07` for this repo (`gh auth switch --user andrette07`).
- The permission classifier blocks pushes/deploys for Claude; Andrés runs them with the `!` prefix.
- QR labels: `qr/etiquetas-qr-bahiaviva.co.pdf` (15 labels, self-check passed). Reprint only if an id changes.

## Audio (added 2026-10-27)
- The students read each card's text aloud, so **card text and recordings must stay in sync**: don't reword a card that has a recording.
- Recordings are served as separate files (`site/audio/`) and loaded when a card opens, not inlined, to keep QR page loads fast.
- Cards without a recording (lancha, manglar_danado, basura) fall back to voice synthesis. To add one:
  `ffmpeg -i in.ogg -ac 1 -ar 24000 -b:a 40k src/audio/<id>.mp3`, rebuild.
- Originals live in `audios/` (gitignored) together with the sister's proposal .docx.

## Pending
1. Hotspot positions for corales/arrecife/pez globo are best guesses (colored stones = corals); adjust x/y if the sister corrects them.
