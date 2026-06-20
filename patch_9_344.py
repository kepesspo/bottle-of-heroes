#!/usr/bin/env python3
"""v9.344 — Revert v9.343: back to black status bar, remove paddingTop from screen container"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Revert status bar style back to black
old_meta = '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>'
new_meta = '<meta name="apple-mobile-web-app-status-bar-style" content="black"/>'
assert old_meta in html, "FAIL: status bar meta"
html = html.replace(old_meta, new_meta, 1)

# 2. Remove paddingTop from screen container
old_container = "paddingTop:'env(safe-area-inset-top)', animation:`slide${dir>0?'In':'Back'} .35s cubic-bezier(.2,.85,.3,1.05)`"
new_container = "animation:`slide${dir>0?'In':'Back'} .35s cubic-bezier(.2,.85,.3,1.05)`"
assert old_container in html, "FAIL: screen container paddingTop"
html = html.replace(old_container, new_container, 1)

html = html.replace("const APP_VERSION = 'v9.343';", "const APP_VERSION = 'v9.344';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.344 — reverted to black status bar, layout restored")
