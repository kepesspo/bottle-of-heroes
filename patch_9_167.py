#!/usr/bin/env python3
"""patch_9_167.py — Emoji kvíz: nincs Sikerült/Nem sikerült CTA, Eltalálta/Nem találta hívja a bannert"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.166';" in content
content = content.replace("const APP_VERSION = 'v9.166';", "const APP_VERSION = 'v9.167';")

# 1. Add emojikv to SCENARIOS with cta:[]
OLD = "  mitval:    { prompt:'', cta:[] },"
NEW = "  mitval:    { prompt:'', cta:[] },\n  emojikv:   { prompt:'', cta:[] },"
assert OLD in content, "SCENARIOS mitval not found"
content = content.replace(OLD, NEW, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.167 ready")
