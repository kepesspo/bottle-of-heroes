#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = """                          const newP = { id:Date.now().toString(), name:pr.name, drinks:0, points:0, color:pr.color||PLAYER_COLORS[players.length%PLAYER_COLORS.length], profileId:pr.id, img:pr.img||null };"""
new = """                          const newP = { id:Date.now().toString(), name:pr.nickname||pr.name, drinks:0, points:0, color:pr.color||PLAYER_COLORS[players.length%PLAYER_COLORS.length], profileId:pr.id, img:pr.img||null };"""
assert old in html, "FAIL: profil picker name"
html = html.replace(old, new, 1)

old2 = """                          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.ink, whiteSpace:'nowrap' }}>{pr.nickname || pr.name}</span>"""
new2 = """                          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.ink, whiteSpace:'nowrap' }}>{pr.name}</span>"""
assert old2 in html, "FAIL: profil picker label"
html = html.replace(old2, new2, 1)

html = html.replace("const APP_VERSION = 'v9.298';", "const APP_VERSION = 'v9.299';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.299 — picker: teljes név, hozzáadva: becenév")
