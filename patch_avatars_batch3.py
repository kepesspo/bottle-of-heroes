#!/usr/bin/env python3
"""v9.593 — 10 új karakter avatar (összesen 20 db)"""
import base64

UPLOAD = '/root/.claude/uploads/ac37e0ea-6dd5-542a-9365-8ab2fbe09fab'

new_avatars = [
    # Első adag (5)
    ('char_bald',      f'{UPLOAD}/176b536b-black.png',   '#F59E0B'),  # kopasz, narancssárga
    ('char_afro',      f'{UPLOAD}/af90cf11-black2.png',  '#EAB308'),  # afro szakáll, sárga
    ('char_darkbeard', f'{UPLOAD}/646a6ca0-man.png',     '#FBBF24'),  # sötét szakáll, sárga
    ('char_spiky',     f'{UPLOAD}/dea508cf-person.png',  '#22C55E'),  # szemüveges tüskés, zöld
    ('char_longhair',  f'{UPLOAD}/c65c6838-man2.png',    '#F87171'),  # hosszú hajú, piros
    # Második adag (5)
    ('char_blond',     f'{UPLOAD}/01b3e08f-man3.png',    '#7C3AED'),  # szőke, lila
    ('char_bigbeard',  f'{UPLOAD}/f8bcbb80-people.png',  '#10B981'),  # nagy szakáll, türkiz
    ('char_necktie',   f'{UPLOAD}/db21659e-man6.png',    '#34D399'),  # nyakkendős, zöld
    ('char_shades',    f'{UPLOAD}/cce0728e-man4.png',    '#16A34A'),  # napszemüveges, zöld
    ('char_curlboy',   f'{UPLOAD}/dec39abb-man5.png',    '#C026D3'),  # göndör fiú, lila
]

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.592') >= 1
html = html.replace('v9.592', 'v9.593', 1)

OLD_END = "];\n\nconst INITIAL_PLAYERS"
new_entries = ""
for aid, path, color in new_avatars:
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    new_entries += f"  {{ id:'{aid}', color:'{color}', img:'data:image/png;base64,{b64}' }},\n"
    print(f"  {aid}: {len(b64)} b64 chars")

NEW_END = new_entries + "];\n\nconst INITIAL_PLAYERS"
assert html.count(OLD_END) == 1
html = html.replace(OLD_END, NEW_END, 1)

assert html.count('const CHAR_AVATARS') == 1
print(f"\nFinal size: {len(html):,} chars")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
