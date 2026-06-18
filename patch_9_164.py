#!/usr/bin/env python3
"""patch_9_164.py — Mit Választanál: cta:[] — nincs Sikerült/Nem sikerült gomb"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.163';" in content
content = content.replace("const APP_VERSION = 'v9.163';", "const APP_VERSION = 'v9.164';")

OLD = "  szamsor:   { prompt:'', cta:[] },\n  reakcio:   { prompt:'', cta:[] },\n  ritmus:    { prompt:'', cta:[] },"
NEW = "  szamsor:   { prompt:'', cta:[] },\n  reakcio:   { prompt:'', cta:[] },\n  ritmus:    { prompt:'', cta:[] },\n  mitval:    { prompt:'', cta:[] },"

assert OLD in content, "SCENARIOS not found"
content = content.replace(OLD, NEW, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.164 ready")
