#!/usr/bin/env python3
"""v9.388 — Splash: jade+slate bg szín szinkronizálva a THEMES objektummal"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Splash init themes — jade és slate elavult értékek
old_themes = """    slate: { bg:'#E8EBF0', deep:'#D4D9E4', ring:'rgba(80,100,130,0.35)', glow:'rgba(90,110,150,0.7)',  ink:'#1A2030', inkSoft:'#404858' },
    jade:  { bg:'#E8F5EE', deep:'#D0EBD8', ring:'rgba(30,120,70,0.35)',  glow:'rgba(40,140,80,0.7)',   ink:'#001A0A', inkSoft:'#1A4A28' },"""

new_themes = """    slate: { bg:'#1E2A38', deep:'#121C28', ring:'rgba(80,110,150,0.35)', glow:'rgba(100,140,200,0.7)', ink:'#E8EEF8', inkSoft:'#9AA8C8' },
    jade:  { bg:'#B8E8C8', deep:'#98D8AC', ring:'rgba(30,120,70,0.35)',  glow:'rgba(40,140,80,0.7)',   ink:'#001A0A', inkSoft:'#1A4A28' },"""

assert old_themes in html, "FAIL: splash themes"
html = html.replace(old_themes, new_themes, 1)

html = html.replace("const APP_VERSION = 'v9.387';", "const APP_VERSION = 'v9.388';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.388 — Splash jade+slate téma szín szinkronizálva")
