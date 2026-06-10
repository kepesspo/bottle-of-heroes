#!/usr/bin/env python3
"""v8.65: FavTile — szaggatott keret ha szerkeszthető (onLongPress)"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD_BORDER = """        border: selected ? `2px solid ${T.mint}` : '2px solid transparent',"""
NEW_BORDER = """        border: selected ? `2px solid ${T.mint}` : onLongPress ? `2px dashed ${T.inkMute}` : '2px solid transparent',"""

assert OLD_BORDER in content, "FavTile border not found"
content = content.replace(OLD_BORDER, NEW_BORDER, 1)
print("✓ FavTile: szaggatott keret ha szerkeszthető")

OLD_VER = "const APP_VERSION = 'v8.64';"
NEW_VER = "const APP_VERSION = 'v8.65';"
assert OLD_VER in content
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.65 saved")
