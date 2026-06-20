#!/usr/bin/env python3
"""v9.390 — Splash: tökéletes középre igazítás (padding eltávolítva)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_splash_css = """      padding-top: 20px; padding-bottom: 140px;"""
new_splash_css = """"""

assert old_splash_css in html, "FAIL: splash padding"
html = html.replace(old_splash_css, new_splash_css, 1)

html = html.replace("const APP_VERSION = 'v9.389';", "const APP_VERSION = 'v9.390';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.390 — Splash tökéletes középre igazítva")
