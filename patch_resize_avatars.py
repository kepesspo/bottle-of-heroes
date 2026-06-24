#!/usr/bin/env python3
"""
v9.600 — Optimalizálás:
1. SW cache (sw.js már frissítve)
2. Avatárok 80x80px-re kicsinyítve (512x512 → 80x80, ~10x méretcsökkentés)
   Teljes CHAR_AVATARS blokk újraépítve.
"""
import base64, io
from PIL import Image

UPLOAD = '/root/.claude/uploads/ac37e0ea-6dd5-542a-9365-8ab2fbe09fab'
SIZE = 80  # px

all_avatars = [
    ('char_girl',      f'{UPLOAD}/507804b8-avatar.png',    '#F4C57E'),
    ('char_old',       f'{UPLOAD}/1d846591-man_2.png',     '#4FC2A0'),
    ('char_glasses',   f'{UPLOAD}/1b3921b4-people.png',    '#3DA888'),
    ('char_asian',     f'{UPLOAD}/fe670fbd-avatar_3.png',  '#5BA0DB'),
    ('char_curly',     f'{UPLOAD}/c7aaa68e-black.png',     '#F97316'),
    ('char_hijab',     f'{UPLOAD}/561bbb5f-avatar_4.png',  '#FBBF24'),
    ('char_ginger',    f'{UPLOAD}/89fa9324-man_3.png',     '#38BDF8'),
    ('char_bun',       f'{UPLOAD}/05afdd50-avatar_2.png',  '#FB923C'),
    ('char_beard',     f'{UPLOAD}/249212ef-person.png',    '#E985B8'),
    ('char_biz',       f'{UPLOAD}/172393a1-man.png',       '#14B8A6'),
    ('char_bald',      f'{UPLOAD}/176b536b-black.png',     '#F59E0B'),
    ('char_afro',      f'{UPLOAD}/af90cf11-black2.png',    '#EAB308'),
    ('char_darkbeard', f'{UPLOAD}/646a6ca0-man.png',       '#FBBF24'),
    ('char_spiky',     f'{UPLOAD}/dea508cf-person.png',    '#22C55E'),
    ('char_longhair',  f'{UPLOAD}/c65c6838-man2.png',      '#F87171'),
    ('char_blond',     f'{UPLOAD}/01b3e08f-man3.png',      '#7C3AED'),
    ('char_bigbeard',  f'{UPLOAD}/f8bcbb80-people.png',    '#10B981'),
    ('char_necktie',   f'{UPLOAD}/db21659e-man6.png',      '#34D399'),
    ('char_shades',    f'{UPLOAD}/cce0728e-man4.png',      '#16A34A'),
    ('char_curlboy',   f'{UPLOAD}/dec39abb-man5.png',      '#C026D3'),
]

def resize_b64(path, size):
    img = Image.open(path).convert('RGBA')
    img = img.resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='PNG', optimize=True)
    return base64.b64encode(buf.getvalue()).decode('ascii')

print(f"Resizing {len(all_avatars)} avatars to {SIZE}x{SIZE}px...")
total_before = total_after = 0

char_js = "const CHAR_AVATARS = [\n"
for aid, path, color in all_avatars:
    # original size
    with open(path, 'rb') as f:
        orig = base64.b64encode(f.read()).decode('ascii')
    b64 = resize_b64(path, SIZE)
    total_before += len(orig)
    total_after += len(b64)
    char_js += f"  {{ id:'{aid}', color:'{color}', img:'data:image/png;base64,{b64}' }},\n"
    print(f"  {aid}: {len(orig):,} → {len(b64):,} b64 chars ({len(b64)*100//len(orig)}%)")
char_js += "];"

print(f"\nÖsszes: {total_before:,} → {total_after:,} b64 chars ({total_after*100//total_before}%)")
print(f"Megtakarítás: {(total_before-total_after)//1024:,} KB")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.599') >= 1
html = html.replace('v9.599', 'v9.600', 1)

# Teljes CHAR_AVATARS blokk cseréje
import re
# Find from "const CHAR_AVATARS = [" to "];" (the closing of the array)
pattern = r'const CHAR_AVATARS = \[[\s\S]*?\];'
matches = list(re.finditer(pattern, html))
assert len(matches) == 1, f"CHAR_AVATARS matches: {len(matches)}"
html = html[:matches[0].start()] + char_js + html[matches[0].end():]

assert html.count('const CHAR_AVATARS') == 1
print(f"\nFinal HTML size: {len(html):,} chars ({len(html)//1024//1024} MB)")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
