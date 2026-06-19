#!/usr/bin/env python3
import base64, os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

changes = []

# Map: filename → IMGS key
banners = [
    ('meduza.png',        'meduza_banner.png'),
    ('gyorsmatek.png',    'matek_banner.png'),
    ('farkasos.png',      'farkasos_banner.png'),
    ('mutasdnemondo.png', 'mutasd_banner.png'),
    ('emojikviz.png',     'emojikv_banner.png'),
    ('mitvalasztanal.png','mitval_banner.png'),
    ('idoparbaj.png',     'idoparbaj_banner.png'),
    ('csakegyszo.png',    'csakegyszo_banner.png'),
    ('szolanc.png',       'szolanc_banner.png'),
]

# 1. Embed images into IMGS object — insert before closing };
# The IMGS object ends at a line that is just "};"
# Find it: after "const IMGS = {"
imgs_start = html.find("const IMGS = {")
assert imgs_start != -1, "FAIL: IMGS not found"
imgs_end = html.find("\n};", imgs_start)
assert imgs_end != -1, "FAIL: IMGS closing not found"

insertions = []
for fname, key in banners:
    if not os.path.exists(fname):
        print(f"SKIP (missing file): {fname}")
        continue
    if f"'{key}'" in html:
        print(f"SKIP (already in IMGS): {key}")
        continue
    with open(fname, 'rb') as f2:
        b64 = base64.b64encode(f2.read()).decode()
    insertions.append(f"  '{key}': 'data:image/png;base64,{b64}',")
    changes.append(f"embedded {key}")

if insertions:
    insert_block = '\n' + '\n'.join(insertions)
    html = html[:imgs_end] + insert_block + html[imgs_end:]
    print(f"Inserted {len(insertions)} banners into IMGS")

# 2. Update game definitions banner: field
game_patches = [
    ("id:'meduza'",     "img:IMGS['meduza_icon.png'],",    "img:IMGS['meduza_icon.png'], banner:IMGS['meduza_banner.png'],"),
    ("id:'matek'",      "img:IMGS['matek_icon.png'],",     "img:IMGS['matek_icon.png'], banner:IMGS['matek_banner.png'],"),
    ("id:'farkasos'",   "img:IMGS['farkasos_icon.png'],",  "img:IMGS['farkasos_icon.png'], banner:IMGS['farkasos_banner.png'],"),
    ("id:'mutasd'",     "img:IMGS['mutasd_icon.png'],",    "img:IMGS['mutasd_icon.png'], banner:IMGS['mutasd_banner.png'],"),
    ("id:'emojikv'",    "img:IMGS['emojikv_icon.png'],",   "img:IMGS['emojikv_icon.png'], banner:IMGS['emojikv_banner.png'],"),
    ("id:'mitval'",     "img:IMGS['mitval_icon.png'],",    "img:IMGS['mitval_icon.png'], banner:IMGS['mitval_banner.png'],"),
    ("id:'idopárbaj'",  "banner:null,",                    "banner:IMGS['idoparbaj_banner.png'],"),
    ("id:'csakegyszó'", "banner:null,",                    "banner:IMGS['csakegyszo_banner.png'],"),
    ("id:'szolánc'",    "banner:null,",                    "banner:IMGS['szolanc_banner.png'],"),
]

for gid, old_field, new_field in game_patches:
    idx = html.find(gid)
    if idx == -1:
        print(f"FAIL: game not found: {gid}")
        continue
    end_line = html.find('\n', idx)
    game_line = html[idx:end_line]
    if old_field not in game_line:
        print(f"SKIP (field not found / already patched): {gid}")
        continue
    html = html[:idx] + game_line.replace(old_field, new_field, 1) + html[end_line:]
    changes.append(f"banner set: {gid}")
    print(f"  ✓ banner: {gid}")

# Version bump
old_ver = "const APP_VERSION = 'v9.266';"
new_ver = "const APP_VERSION = 'v9.267';"
assert old_ver in html, "FAIL: version"
html = html.replace(old_ver, new_ver, 1)
changes.append("v9.267")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nDone! {len(changes)} changes applied.")
