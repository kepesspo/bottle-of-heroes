#!/usr/bin/env python3
"""patch_9_166.py — Tabu: nincs Ki rontott szekció, a gombok intézik az eredményt"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.165';" in content
content = content.replace("const APP_VERSION = 'v9.165';", "const APP_VERSION = 'v9.166';")

OLD = "currentGameId !== 'powerhour' && currentGameId !== 'ovfj' && ("
NEW = "currentGameId !== 'powerhour' && currentGameId !== 'ovfj' && currentGameId !== 'tabu' && ("

assert OLD in content, "Csapat exclusion not found"
content = content.replace(OLD, NEW, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.166 ready")
