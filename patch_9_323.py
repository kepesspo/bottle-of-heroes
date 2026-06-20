#!/usr/bin/env python3
"""v9.323 — Revert status-bar to default: fixes adaptive text color + excessive bottom padding"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Revert black-translucent → default
# With black-translucent: env(safe-area-inset-bottom) ≈ 34px → BottomBar paddingBottom = 42px (too much)
# With default: iOS handles home indicator offset; env(safe-area-inset-bottom) ≈ 0 → 20px (normal)
# Also fixes: status bar text forced white on light backgrounds
old_status = '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>'
new_status = '<meta name="apple-mobile-web-app-status-bar-style" content="default"/>'
assert old_status in html, "FAIL: status bar"
html = html.replace(old_status, new_status, 1)

html = html.replace("const APP_VERSION = 'v9.322';", "const APP_VERSION = 'v9.323';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.323 — status-bar reverted to default (adaptive text + normal bottom padding)")
