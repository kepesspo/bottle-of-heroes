#!/usr/bin/env python3
"""v9.338 — Fix white strip: scroll area gets transparent bg so outer div gradient shows through"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Scroll area: add background:'transparent' so browser doesn't default to white
old_scroll = "flex:'1 1 0', minHeight:0, overflowY:'scroll', WebkitOverflowScrolling:'touch'"
new_scroll = "flex:'1 1 0', minHeight:0, overflowY:'scroll', WebkitOverflowScrolling:'touch', background:'transparent'"
assert old_scroll in html, "FAIL: scroll area"
html = html.replace(old_scroll, new_scroll, 1)

html = html.replace("const APP_VERSION = 'v9.337';", "const APP_VERSION = 'v9.338';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.338 — scroll area transparent, outer div gradient visible below pill")
