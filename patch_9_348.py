#!/usr/bin/env python3
"""v9.348 — Fix broken gradient: 2-stop over 45% (rgba suffix was invalid)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_grad = "background:`linear-gradient(to bottom, ${T.bg} 0%, ${T.bgOverlay}88 20%, ${T.bgOverlay} 42%)`"
new_grad = "background:`linear-gradient(to bottom, ${T.bg} 0%, ${T.bgOverlay} 45%)`"
count = html.count(old_grad)
assert count == 2, f"FAIL: expected 2, found {count}"
html = html.replace(old_grad, new_grad)

html = html.replace("const APP_VERSION = 'v9.347';", "const APP_VERSION = 'v9.348';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.348 — clean 2-stop gradient over 45% screen height")
