Paste this into Claude Code from inside the `bahiaviva` folder:

---

Read CLAUDE.md first. This is a finished single-page Spanish web app for my nephew's 2nd-grade class
project; your job is to put it online on my domain and regenerate the QR labels.

The domain I bought on GoDaddy is: **bahiaviva.co**   ← (change if different)

Do this:
1. `pip install qrcode[pil] reportlab opencv-python-headless pymupdf` if missing, then run
   `python3 scripts/build.py` and confirm site/index.html builds with 14 cards.
2. Write `site/CNAME` containing only the domain.
3. Create a public GitHub repo `andrette07/bahiaviva` (use `gh repo create` if I'm logged in; otherwise tell me
   to create it empty and wait). Commit everything, push to `main`.
4. Enable GitHub Pages to serve the `site/` folder. GitHub's branch deploy only allows `/` or `/docs`, so either
   add a small GitHub Actions workflow that deploys `site/` (actions/upload-pages-artifact + deploy-pages), or
   use a `gh-pages` branch containing only the contents of `site/`. Pick one, tell me which, and set the custom domain.
5. Give me the exact GoDaddy DNS records to add (or confirm the ones in CLAUDE.md), and remind me to delete the
   parked record. Check DNS with `dig` until it resolves to GitHub, then tell me to enable Enforce HTTPS.
6. Run `python3 scripts/make_qr.py <domain>`, confirm the self-check passes, and give me the PDF path.
7. Test https://<domain>/ and https://<domain>/#ballena at 400px wide (Playwright is fine): no horizontal scroll,
   the deep link opens the "La ballena jorobada" card.

Be brief with me; I'll ask if I need detail.
