#!/usr/bin/env python3
"""v8.59: Molnár Balázs profilkép eltávolítása"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. IMGS dict: profile_balazs.jpg eltávolítása ────────────────────────────
import re
old_entry = re.search(r"\n  'profile_balazs\.jpg': 'data:image/jpeg;base64,[^']*',", content)
assert old_entry, "profile_balazs.jpg entry not found"
content = content.replace(old_entry.group(0), '', 1)
print("✓ profile_balazs.jpg eltávolítva az IMGS-ből")

# ── 2. PRESET_PLAYERS: imgKey eltávolítása Balázsról ─────────────────────────
OLD_BALAZS = """    { id:'preset_balazs', name:'Molnár Balázs',     nickname:'Balázs', color:'#818CF8', imgKey:'profile_balazs.jpg' },"""
NEW_BALAZS = """    { id:'preset_balazs', name:'Molnár Balázs',     nickname:'Balázs', color:'#818CF8' },"""

assert OLD_BALAZS in content, "Balázs preset not found"
content = content.replace(OLD_BALAZS, NEW_BALAZS, 1)
print("✓ Balázs imgKey eltávolítva")

# ── 3. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.58';"
NEW_VER = "const APP_VERSION = 'v8.59';"
assert OLD_VER in content, "version not found"
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.59 saved")
