# -*- coding: utf-8 -*-
import base64

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

def b64img(fname):
    with open(fname, 'rb') as f:
        return f"data:image/png;base64,{base64.b64encode(f.read()).decode('ascii')}"

old_busz = b64img('busz.png')
new_busz = b64img('busz-2.png')
assert old_busz in html, "Old busz banner not found"
html = html.replace(old_busz, new_busz, 1)

assert 'Verzió 5.62 · DNR · 2026.06.02 16:30' in html, "Version not found"
html = html.replace('Verzió 5.62 · DNR · 2026.06.02 16:30', 'Verzió 5.63 · DNR · 2026.06.02 17:00', 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Done — v5.63")
