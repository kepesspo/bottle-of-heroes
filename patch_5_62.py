# -*- coding: utf-8 -*-
import base64

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

def b64img(fname):
    with open(fname, 'rb') as f:
        return f"data:image/png;base64,{base64.b64encode(f.read()).decode('ascii')}"

# Replace old banner data with new ones
old_imp = b64img('imposztor.png')
new_imp = b64img('imposztor-2.png')
assert old_imp in html, "Old imposztor banner not found"
html = html.replace(old_imp, new_imp, 1)

old_mem = b64img('memoria.png')
new_mem = b64img('memoria-2.png')
assert old_mem in html, "Old memoria banner not found"
html = html.replace(old_mem, new_mem, 1)

# Version bump
assert 'Verzió 5.61 · DNR · 2026.06.02 16:00' in html, "Version not found"
html = html.replace('Verzió 5.61 · DNR · 2026.06.02 16:00', 'Verzió 5.62 · DNR · 2026.06.02 16:30', 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done — v5.62")
