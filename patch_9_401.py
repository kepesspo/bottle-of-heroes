#!/usr/bin/env python3
"""v9.401 — Hotfix: GameContent függvény fejléc visszaállítása (patch_9_399 kivágta)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# A routing block jelenleg lebegő kód — hiányzik a function GameContent({...}) { fejléc
# Vissza kell illeszteni a szolánc routing sor elé

old_routing_start = """  if (gameId === 'szolánc') return <SzolancGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} />;"""

new_routing_start = """function GameContent({ gameId, gameIdx, players, onAdvance, onUnready, onResult, onLiveDrinkUpdate, roomCode, gameMeta, challenger, opponent, onSetHideFooter, onSetBuszSwitch, onCommit }) {
  if (gameId === 'szolánc') return <SzolancGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} />;"""

assert old_routing_start in html, "FAIL: routing start not found"
html = html.replace(old_routing_start, new_routing_start, 1)

html = html.replace("const APP_VERSION = 'v9.400';", "const APP_VERSION = 'v9.401';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.401 — GameContent fejléc visszaállítva, app újra működik")
