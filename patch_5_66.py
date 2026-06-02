# -*- coding: utf-8 -*-
import base64, os

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

def b64img(fname):
    with open(fname, 'rb') as f:
        return f"data:image/png;base64,{base64.b64encode(f.read()).decode('ascii')}"

# Map game id -> centered image file
HEADERS = [
    ('anagramma', 'anagramma.png'), ('busz', 'busz.png'), ('collect', 'collect.png'),
    ('fingerit', 'fingerit.png'), ('hajime', 'hajime.png'), ('igazhamis', 'igazhamis.png'),
    ('imposztor', 'imposztor.png'), ('kategoria', 'kategoria.png'), ('kezcsere', 'kezcsere.png'),
    ('kisebb', 'kisebbnagyobb.png'), ('kivagyok', 'kivagyok.png'), ('kopapir', 'kopapir.png'),
    ('loverseny', 'loverseny.png'), ('memoria', 'memoria.png'), ('mindenki', 'mindenki.png'),
    ('otdolog', 'otdolog.png'), ('ringfire', 'ringfire.png'), ('rulett', 'rulett.png'),
    ('sohanem', 'sohanem.png'), ('szerencse', 'szerencse.png'), ('tapper', 'tapper.png'),
    ('ticktak', 'ticktak.png'), ('uveg', 'uveg.png'), ('zene', 'zene.png'),
]

for gid, fname in HEADERS:
    key = f"'{gid}_banner.png'"
    old_data = b64img(f'game-headers/{fname}')
    new_data = b64img(f'game-headers-centered/{fname}')
    old_entry = f"{key}: '{old_data}'"
    new_entry = f"{key}: '{new_data}'"
    if old_entry in html:
        html = html.replace(old_entry, new_entry, 1)
        print(f"  {gid}: updated")
    else:
        print(f"  {gid}: NOT FOUND")

html = html.replace('Verzió 5.65 · DNR · 2026.06.02 18:00', 'Verzió 5.66 · DNR · 2026.06.02 18:30')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Done — v5.66")
