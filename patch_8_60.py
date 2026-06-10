#!/usr/bin/env python3
"""v8.60: Németh Gyula és Bacsinszki Dániel hozzáadása a profile listához"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Két új preset játékos ──────────────────────────────────────────────────
OLD_BALAZS = """    { id:'preset_balazs', name:'Molnár Balázs',     nickname:'Balázs', color:'#818CF8' },
  ];"""

NEW_BALAZS = """    { id:'preset_balazs', name:'Molnár Balázs',     nickname:'Balázs', color:'#818CF8' },
    { id:'preset_gyula',  name:'Németh Gyula',       nickname:'Gyula',  color:'#EF4444' },
    { id:'preset_bacsi',  name:'Bacsinszki Dániel',  nickname:'Bacsi',  color:'#F97316' },
  ];"""

assert OLD_BALAZS in content, "Balázs / PRESET_PLAYERS end not found"
content = content.replace(OLD_BALAZS, NEW_BALAZS, 1)
print("✓ Gyula és Bacsi hozzáadva")

# ── 2. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.59';"
NEW_VER = "const APP_VERSION = 'v8.60';"
assert OLD_VER in content, "version not found"
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.60 saved")
