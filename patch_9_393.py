#!/usr/bin/env python3
"""v9.393 — PrimaryButton disabled: fg T.inkMute (sötét témán is látható)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_btn = """  const fg = disabled ? 'rgba(26,42,74,0.4)' : '#fff';"""
new_btn = """  const fg = disabled ? T.inkMute : '#fff';"""

assert old_btn in html, "FAIL: button fg"
html = html.replace(old_btn, new_btn, 1)

html = html.replace("const APP_VERSION = 'v9.392';", "const APP_VERSION = 'v9.393';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.393 — PrimaryButton disabled szöveg látható sötét témán is")
