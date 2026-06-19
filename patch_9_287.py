#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. StatsScreen profil tab: sort by totalPoints instead of win rate
old = """          const profilRows = [...profiles].sort((a, b) => {
            const sa = stats[a.id] || {}, sb = stats[b.id] || {};
            const wrA = sa.totalSessions > 0 ? (sa.totalWins||0)/sa.totalSessions : -1;
            const wrB = sb.totalSessions > 0 ? (sb.totalWins||0)/sb.totalSessions : -1;
            return wrB - wrA;"""
new = """          const profilRows = [...profiles].sort((a, b) => {
            const sa = stats[a.id] || {}, sb = stats[b.id] || {};
            return (sb.totalPoints||0) - (sa.totalPoints||0);"""
assert old in html, "FAIL: profilRows sort"
html = html.replace(old, new, 1)

# ── 2. shuffle: exclude comingSoon games
old = """    const pool = GAMES.filter(g=>g.id!=='busz'&&g.id!=='beerpong'&&g.id!=='powerhour'&&g.id!=='ovfj'&&g.id!=='ringfire');"""
new = """    const pool = GAMES.filter(g=>g.id!=='busz'&&g.id!=='beerpong'&&g.id!=='powerhour'&&g.id!=='ovfj'&&g.id!=='ringfire'&&!g.comingSoon);"""
assert old in html, "FAIL: shuffle pool"
html = html.replace(old, new, 1)

html = html.replace("const APP_VERSION = 'v9.285';", "const APP_VERSION = 'v9.287';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.287 — profil stat pont sorrend, shuffle kizárja comingSoon játékokat")
