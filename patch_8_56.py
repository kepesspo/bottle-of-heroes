#!/usr/bin/env python3
"""v8.56: Balázs profilkép csere (új fotó)"""

with open('/tmp/balazs_photo_new.b64', 'r') as f:
    b64 = f.read().strip()

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Régi profilkép cseréje az IMGS dict-ben ───────────────────────────────
import re
old_entry = re.search(r"  'profile_balazs\.jpg': 'data:image/jpeg;base64,[^']*',", content)
assert old_entry, "profile_balazs.jpg entry not found"
old_str = old_entry.group(0)
new_str = f"  'profile_balazs.jpg': 'data:image/jpeg;base64,{b64}',"
content = content.replace(old_str, new_str, 1)
print("✓ Balázs profilkép cserélve")

# ── 2. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.55';"
NEW_VER = "const APP_VERSION = 'v8.56';"
assert OLD_VER in content, "version not found"
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.56 saved")
