# -*- coding: utf-8 -*-
import base64, os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

def b64img(fname):
    with open(fname, 'rb') as f:
        return f"data:image/png;base64,{base64.b64encode(f.read()).decode('ascii')}"

# Map: game id -> (header filename, game definition old/new img field anchor)
HEADERS = [
    ('anagramma',   'anagramma.png',     "id:'anagramma',"),
    ('busz',        'busz.png',          "id:'busz',"),
    ('collect',     'collect.png',       "id:'collect',"),
    ('fingerit',    'fingerit.png',      "id:'fingerit',"),
    ('hajime',      'hajime.png',        "id:'hajime',"),
    ('igazhamis',   'igazhamis.png',     "id:'igazhamis',"),
    ('imposztor',   'imposztor.png',     "id:'imposztor',"),
    ('kategoria',   'kategoria.png',     "id:'kategoria',"),
    ('kezcsere',    'kezcsere.png',      "id:'kezcsere',"),
    ('kisebb',      'kisebbnagyobb.png', "id:'kisebb',"),
    ('kivagyok',    'kivagyok.png',      "id:'kivagyok',"),
    ('kopapir',     'kopapir.png',       "id:'kopapir',"),
    ('loverseny',   'loverseny.png',     "id:'loverseny',"),
    ('memoria',     'memoria.png',       "id:'memoria',"),
    ('mindenki',    'mindenki.png',      "id:'mindenki',"),
    ('otdolog',     'otdolog.png',       "id:'otdolog',"),
    ('ringfire',    'ringfire.png',      "id:'ringfire',"),
    ('rulett',      'rulett.png',        "id:'rulett',"),
    ('sohanem',     'sohanem.png',       "id:'sohanem',"),
    ('szerencse',   'szerencse.png',     "id:'szerencse',"),
    ('tapper',      'tapper.png',        "id:'tapper',"),
    ('ticktak',     'ticktak.png',       "id:'ticktak',"),
    ('uveg',        'uveg.png',          "id:'uveg',"),
    ('zene',        'zene.png',          "id:'zene',"),
]

# 1. Build IMGS entries for all new banners
imgs_insert = ""
for gid, fname, _ in HEADERS:
    key = f'{gid}_banner.png'
    data = b64img(f'game-headers/{fname}')
    imgs_insert += f"  '{key}': '{data}',\n"

# Insert after last existing banner entry (imposztor_banner)
anchor = "  'imposztor_banner.png':"
idx = html.find(anchor)
line_end = html.find('\n', idx)
old_line = html[idx:line_end+1]
# Remove existing busz_banner and memoria_banner entries too (they'll be re-added fresh)
# Actually just insert all new ones after imposztor line, they'll overwrite via IMGS key lookup
# Better: replace the whole block of banner entries
# Find end of IMGS block by looking for the closing };
# Simple approach: insert all new banner keys right after imposztor_banner line
html = html.replace(old_line, old_line + imgs_insert, 1)

# 2. Add banner field to each game definition (skip ones already having it)
for gid, fname, anchor in HEADERS:
    key = f"IMGS['{gid}_banner.png']"
    # Check if already has banner field
    if f"banner:{key}" in html or f"banner: {key}" in html:
        print(f"  {gid}: already has banner, skipping")
        continue
    # Find the game definition line and add banner field after img field
    # Pattern: img:IMGS['xxx_icon.png'],
    img_key = f"IMGS['{gid}_icon.png'],"
    # Special case for kezcsere (typo in original: kezcere)
    if gid == 'kezcsere':
        img_key = "IMGS['kezcere_icon.png'],"
    if img_key not in html:
        print(f"  WARNING: {gid} img key not found: {img_key}")
        continue
    # Find the occurrence near the anchor
    anchor_idx = html.find(anchor)
    img_idx = html.find(img_key, anchor_idx)
    if img_idx == -1:
        print(f"  WARNING: {gid} img not found after anchor")
        continue
    old = img_key
    new = img_key + f" banner:{key},"
    html = html[:img_idx] + new + html[img_idx+len(old):]
    print(f"  {gid}: added banner")

# 3. Version bump
html = html.replace('Verzió 5.64 · DNR · 2026.06.02 17:30', 'Verzió 5.65 · DNR · 2026.06.02 18:00')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Done — v5.65")
