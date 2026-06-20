#!/usr/bin/env python3
"""v9.387 — Splash: logó pozíció igazítva a főképernyőhöz (padding-top/bottom)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# #splash: padding-top 56px (appbar) + padding-bottom 80px (bottombar) → logó ugyanott van mint a főképernyőn
old_splash_css = """    #splash {
      position: fixed; inset: 0; z-index: 99999;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      background: #F4C57E;
      transition: opacity 0.25s ease; overflow: hidden;
    }"""

new_splash_css = """    #splash {
      position: fixed; inset: 0; z-index: 99999;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      background: #F4C57E;
      padding-top: 56px; padding-bottom: 80px;
      transition: opacity 0.25s ease; overflow: hidden;
    }"""

assert old_splash_css in html, "FAIL: splash css"
html = html.replace(old_splash_css, new_splash_css, 1)

html = html.replace("const APP_VERSION = 'v9.386';", "const APP_VERSION = 'v9.387';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.387 — Splash logó pozíció igazítva a főképernyőhöz")
