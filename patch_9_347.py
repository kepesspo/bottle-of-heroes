#!/usr/bin/env python3
"""v9.347 — Smoother overlay gradient: longer transition with intermediate stops"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extend gradient over 40% of screen with 3 stops for smooth easing
# T.bg (top, matches status bar) → semi-dark (20%) → T.bgOverlay (40% onward)
old_grad = "background:`linear-gradient(to bottom, ${T.bg} 0%, ${T.bgOverlay} 90px)`"
new_grad = "background:`linear-gradient(to bottom, ${T.bg} 0%, ${T.bgOverlay}88 20%, ${T.bgOverlay} 42%)`"
count = html.count(old_grad)
assert count == 2, f"FAIL: expected 2 gradient occurrences, found {count}"
html = html.replace(old_grad, new_grad)

html = html.replace("const APP_VERSION = 'v9.346';", "const APP_VERSION = 'v9.347';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.347 — gradient over 42% screen height, intermediate stop for smooth easing")
