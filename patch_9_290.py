#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = """    onResult && onResult({ correct: losers.length === 0, playerName: losers[0]?.name || null, drinks: losers.length > 0 ? 1 : 0, subtitle });
    onAdvance && onAdvance(dm);"""
new = """    const pm = {};
    players.forEach(p => { if (!(dm[p.id] > 0)) pm[p.id] = 1; });
    onResult && onResult({ correct: losers.length === 0, playerName: losers[0]?.name || null, drinks: losers.length > 0 ? 1 : 0, subtitle });
    onAdvance && onAdvance(dm, pm);"""
assert old in html, "FAIL: finish onAdvance"
html = html.replace(old, new, 1)

html = html.replace("const APP_VERSION = 'v9.289';", "const APP_VERSION = 'v9.290';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.290 — KezCsere: hibátlan játékosok pontot kapnak")
