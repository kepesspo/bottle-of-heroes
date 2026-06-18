#!/usr/bin/env python3
"""patch_9_162.py — Ritmus játék: nincs Vesztettem/Nyertem gomb"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.161';" in content
content = content.replace("const APP_VERSION = 'v9.161';", "const APP_VERSION = 'v9.162';")

OLD = "      {currentGame.category === 'Páros' && selectedOpponent && scenario.cta.length > 0 && currentGameId !== 'szamsor' && currentGameId !== 'reakcio' && ("
NEW  = "      {currentGame.category === 'Páros' && selectedOpponent && scenario.cta.length > 0 && currentGameId !== 'szamsor' && currentGameId !== 'reakcio' && currentGameId !== 'ritmus' && ("

assert OLD in content, "Páros CTA not found"
content = content.replace(OLD, NEW, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.162 ready")
