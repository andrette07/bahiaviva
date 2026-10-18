#!/usr/bin/env python3
"""Generate the printable QR label sheet (Letter size) for the live site.

Usage:  python3 scripts/make_qr.py bahiaviva.co
Needs:  pip install qrcode[pil] reportlab   (verification: pip install opencv-python-headless pymupdf)

One label for the home page + one per card in src/stops.js, numbered and colored
like the app (green = Zona 1, blue = animal, red = Zona 2). Each card label links to
https://<domain>/#<id>, which the app opens straight to that card.
"""
import re, sys
from pathlib import Path
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import ImageReader

if len(sys.argv) != 2:
    raise SystemExit("Usage: python3 scripts/make_qr.py <domain>   e.g. bahiaviva.co")
DOMAIN = sys.argv[1].strip().removeprefix("https://").removeprefix("http://").strip("/")
BASE = f"https://{DOMAIN}/"

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / "src" / "stops.js").read_text(encoding="utf-8")
stops = re.findall(r"\{ id: '(\w+)', z: '(\w+)'.*?title: '([^']+)'", src, re.S)

COL = {"z1": "#24793a", "an": "#1b78c4", "z2": "#d9472a", "home": "#1b2a5e"}
LAB = {"z1": "ZONA 1", "an": "ANIMAL", "z2": "ZONA 2", "home": "INICIO"}
items = [("", "home", "Bahía del Pacífico Colombiano", "")] + \
        [(i, z, t, str(n + 1)) for n, (i, z, t) in enumerate(stops)]

out = ROOT / "qr" / f"etiquetas-qr-{DOMAIN}.pdf"
out.parent.mkdir(exist_ok=True)
W, H = letter
cols, rows = 3, 4
lw, lh = 6.4 * cm, 6.2 * cm
mx = (W - cols * lw) / (cols + 1)
my = (H - rows * lh) / (rows + 1)
c = canvas.Canvas(str(out), pagesize=letter)
c.setTitle(f"Etiquetas QR - {DOMAIN}")
urls = []
for k, (i, z, t, num) in enumerate(items):
    if k and k % (cols * rows) == 0:
        c.showPage()
    p = k % (cols * rows)
    col, row = p % cols, p // cols
    x = mx + col * (lw + mx)
    y = H - (my + (row + 1) * lh + row * my)
    url = BASE + (f"#{i}" if i else "")
    urls.append(url)
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    q.add_data(url); q.make(fit=True)
    img = q.make_image(fill_color="black", back_color="white").get_image()
    color = HexColor(COL[z])
    c.setStrokeColor(color); c.setLineWidth(3); c.setFillColor(white)
    c.roundRect(x, y, lw, lh, 10, stroke=1, fill=1)
    home = not num
    if not home:
        c.setFillColor(color); c.circle(x + 0.75 * cm, y + lh - 0.75 * cm, 0.45 * cm, stroke=0, fill=1)
        c.setFillColor(white); c.setFont("Helvetica-Bold", 13 if len(num) < 2 else 11)
        c.drawCentredString(x + 0.75 * cm, y + lh - 0.75 * cm - 4.5, num)
    c.setFillColor(color); c.setFont("Helvetica-Bold", 9)
    c.drawString(x + (0.5 if home else 1.4) * cm, y + lh - 0.85 * cm, LAB[z])
    qs = 3.9 * cm
    c.drawImage(ImageReader(img), x + (lw - qs) / 2, y + 1.2 * cm, qs, qs)
    title = t.split(":")[0] if i.startswith("zona") else t
    c.setFillColor(HexColor("#1b2a5e")); c.setFont("Helvetica-Bold", 12 if len(title) <= 24 else 10)
    c.drawCentredString(x + lw / 2, y + 0.65 * cm, title)
    c.setFont("Helvetica", 7.5); c.setFillColor(HexColor("#4c5d84"))
    c.drawCentredString(x + lw / 2, y + 0.25 * cm, "Escanea con la cámara del celular")
c.save()
(ROOT / "qr" / f"urls-{DOMAIN}.txt").write_text("\n".join(urls) + "\n")
print(f"Wrote {out.relative_to(ROOT)} with {len(items)} labels")

# optional self-check: decode every QR from the rendered PDF
try:
    import cv2, numpy as np
    import pymupdf as fitz
    det, found = cv2.QRCodeDetector(), set()
    for page in fitz.open(str(out)):
        pix = page.get_pixmap(dpi=150)
        im = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :3].copy()
        ok, vals, _, _ = det.detectAndDecodeMulti(im)
        found.update(v for v in vals if v)
    missing = [u for u in urls if u not in found]
    print("QR check:", "all codes decode correctly" if not missing else f"NOT decoded: {missing}")
except ImportError:
    print("QR check skipped (pip install opencv-python-headless pymupdf to enable)")
