#!/usr/bin/env python3
"""v9.380 — Defer React render by 1s so logo drop + impact animation runs smoothly"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Wrap the render call in setTimeout(fn, 1000) so the main thread
# is free during the logo drop (0-0.7s) and impact moment (0.7-1.0s)
old_render = "ReactDOM.createRoot(document.getElementById('root')).render(<Root />);"
new_render  = "setTimeout(function() { ReactDOM.createRoot(document.getElementById('root')).render(<Root />); }, 1000);"

assert old_render in html, "FAIL: render call"
html = html.replace(old_render, new_render, 1)

# Minimum display time: 3.2s → 3.5s (delayed render means React ready comes later)
html = html.replace('}, 3200);', '}, 3500);', 1)

html = html.replace("const APP_VERSION = 'v9.379';", "const APP_VERSION = 'v9.380';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.380 — React render deferred 1s, splash animations unblocked")
