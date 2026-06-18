#!/usr/bin/env python3
"""patch_9_161.py — Szám sorrend + reakció: nincs Vesztettem/Nyertem gomb"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.160';" in content
content = content.replace("const APP_VERSION = 'v9.160';", "const APP_VERSION = 'v9.161';")

OLD = "      {currentGame.category === 'Páros' && selectedOpponent && scenario.cta.length > 0 && ("
NEW  = "      {currentGame.category === 'Páros' && selectedOpponent && scenario.cta.length > 0 && currentGameId !== 'szamsor' && currentGameId !== 'reakcio' && ("

assert OLD in content, "Páros CTA not found"
content = content.replace(OLD, NEW, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.161 ready")
