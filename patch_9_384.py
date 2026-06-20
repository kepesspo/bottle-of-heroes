#!/usr/bin/env python3
"""v9.384 — Splash: sima t.bg háttér (nincs radial gradient), seamless átmenet az appba"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Eltávolítjuk a radial gradient-et az init script-ből ───────────────────
old_bg_js = """  // Theme colors
  var bg = document.getElementById('splash-bg');
  splash.style.background = t.bg;
  if (bg) bg.style.background = 'radial-gradient(ellipse at 50% 45%, ' + t.deep + ' 0%, ' + t.bg + ' 70%)';"""

new_bg_js = """  // Theme colors — sima flat szín, mint az app (nincs gradient = nincs ugrás)
  splash.style.background = t.bg;"""

assert old_bg_js in html, "FAIL: bg js"
html = html.replace(old_bg_js, new_bg_js, 1)

# ── 2. #splash-bg div-et eltávolítjuk a HTML-ből (felesleges lett) ─────────────
old_bg_html = '  <div id="splash-bg"></div>\n'
assert old_bg_html in html, "FAIL: bg html"
html = html.replace(old_bg_html, '', 1)

# ── 3. CSS-ből töröljük a #splash-bg rule-t ────────────────────────────────────
old_bg_css = "    #splash-bg { position:absolute; inset:0; }\n"
assert old_bg_css in html, "FAIL: bg css"
html = html.replace(old_bg_css, '', 1)

# ── 4. Splash transition gyorsabb: 600ms → 250ms (kevesebb ideig látszik az app mögötte) ──
old_transition = "      transition: opacity 0.6s ease; overflow: hidden;"
new_transition  = "      transition: opacity 0.25s ease; overflow: hidden;"

assert old_transition in html, "FAIL: transition"
html = html.replace(old_transition, new_transition, 1)

# ── 5. DOM remove delay: 600ms → 300ms ────────────────────────────────────────
html = html.replace(
    "setTimeout(() => { if (splash.parentNode) splash.parentNode.removeChild(splash); }, 600);",
    "setTimeout(() => { if (splash.parentNode) splash.parentNode.removeChild(splash); }, 300);",
    1
)

html = html.replace("const APP_VERSION = 'v9.383';", "const APP_VERSION = 'v9.384';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.384 — Splash flat háttér, gyors kimenet, seamless átmenet")
