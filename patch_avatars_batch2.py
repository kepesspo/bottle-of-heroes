#!/usr/bin/env python3
"""v9.588 — 5 új karakter avatar hozzáadva (összesen 10 db)"""
import base64

UPLOAD = '/root/.claude/uploads/ac37e0ea-6dd5-542a-9365-8ab2fbe09fab'

new_avatars = [
    ('char_hijab',    f'{UPLOAD}/561bbb5f-avatar_4.png', '#F4C57E'),  # sárga
    ('char_ginger',   f'{UPLOAD}/89fa9324-man_3.png',    '#38BDF8'),  # kék
    ('char_bun',      f'{UPLOAD}/05afdd50-avatar_2.png', '#F97316'),  # narancs
    ('char_beard',    f'{UPLOAD}/249212ef-person.png',   '#E985B8'),  # pink
    ('char_biz',      f'{UPLOAD}/172393a1-man.png',      '#14B8A6'),  # türkiz
]

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Version bump
assert html.count('v9.587') >= 1
html = html.replace('v9.587', 'v9.588', 1)

# Find the end of CHAR_AVATARS array and insert new entries before the closing ];
OLD_CHAR_END = "];\n\nconst INITIAL_PLAYERS"
new_entries = ""
for aid, path, color in new_avatars:
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    new_entries += f"  {{ id:'{aid}', color:'{color}', img:'data:image/png;base64,{b64}' }},\n"
    print(f"{aid}: {len(b64)} chars")

NEW_CHAR_END = new_entries + "];\n\nconst INITIAL_PLAYERS"
assert html.count(OLD_CHAR_END) == 1
html = html.replace(OLD_CHAR_END, NEW_CHAR_END, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Done. CHAR_AVATARS now has 10 entries.")
