#!/usr/bin/env python3
"""
v9.605:
1. Alapértelmezett játék nézet: 'netflix' → 'grid'
2. Gyula ↔ KKK avatar csere (char_bald ↔ char_shades)
3. 5 új female avatar hozzáadása a CHAR_AVATARS tömbhöz
"""
import base64, io, re
from PIL import Image

UPLOAD = '/root/.claude/uploads/ac37e0ea-6dd5-542a-9365-8ab2fbe09fab'
SIZE = 80

new_avatars = [
    ('char_bun2',      f'{UPLOAD}/e56c82eb-avatar.png',    '#A855F7'),
    ('char_longhair2', f'{UPLOAD}/c2fcae40-people2.png',   '#EC4899'),
    ('char_blond2',    f'{UPLOAD}/6f144d4e-avatar4.png',   '#B45309'),
    ('char_glasses2',  f'{UPLOAD}/be2c012c-avatar3.png',   '#06B6D4'),
    ('char_curly2',    f'{UPLOAD}/25c63b89-avatar2.png',   '#F87171'),
]

def resize_b64(path):
    img = Image.open(path).convert('RGBA')
    img = img.resize((SIZE, SIZE), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='PNG', optimize=True)
    return base64.b64encode(buf.getvalue()).decode('ascii')

print("Resizing new avatars...")
new_entries = []
for aid, path, color in new_avatars:
    b64 = resize_b64(path)
    new_entries.append(f"  {{ id:'{aid}', color:'{color}', img:'data:image/png;base64,{b64}' }},")
    print(f"  {aid}: {len(b64):,} b64 chars")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.604') >= 1
html = html.replace('v9.604', 'v9.605', 1)

# ── 1. Alapértelmezett nézet: netflix → grid ──────────────────────────────────
OLD_VIEW = "localStorage.getItem('boh_games_view') || 'netflix'"
NEW_VIEW = "localStorage.getItem('boh_games_view') || 'grid'"
assert html.count(OLD_VIEW) == 1, f"view: {html.count(OLD_VIEW)}"
html = html.replace(OLD_VIEW, NEW_VIEW, 1)
print("OK: default view → grid")

# ── 2. Gyula ↔ KKK avatar csere ──────────────────────────────────────────────
OLD_KKK   = "{ id:'preset_kkk',    name:'Tóth Gergő',        nickname:'KKK',    color:'#16A34A', ...av('char_shades')   },"
NEW_KKK   = "{ id:'preset_kkk',    name:'Tóth Gergő',        nickname:'KKK',    color:'#16A34A', ...av('char_bald')     },"
OLD_GYULA = "{ id:'preset_gyula',  name:'Németh Gyula',       nickname:'Gyula',  color:'#F59E0B', ...av('char_bald')     },"
NEW_GYULA = "{ id:'preset_gyula',  name:'Németh Gyula',       nickname:'Gyula',  color:'#F59E0B', ...av('char_shades')   },"

assert html.count(OLD_KKK) == 1, f"kkk: {html.count(OLD_KKK)}"
assert html.count(OLD_GYULA) == 1, f"gyula: {html.count(OLD_GYULA)}"
html = html.replace(OLD_KKK, NEW_KKK, 1)
html = html.replace(OLD_GYULA, NEW_GYULA, 1)
print("OK: Gyula ↔ KKK avatar csere")

# ── 3. Új avatarok hozzáadása a CHAR_AVATARS tömb végéhez ────────────────────
# Find the closing "];" of CHAR_AVATARS
pattern = r'(const CHAR_AVATARS = \[[\s\S]*?)(];)'
matches = list(re.finditer(pattern, html))
assert len(matches) == 1, f"CHAR_AVATARS: {len(matches)}"
m = matches[0]
insert_pos = m.start(2)  # before "];"
new_lines = '\n' + '\n'.join(new_entries) + '\n'
html = html[:insert_pos] + new_lines + html[insert_pos:]
print(f"OK: {len(new_entries)} új avatar hozzáadva")

print(f"Final size: {len(html):,} chars ({len(html)//1024//1024} MB)")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
