#!/usr/bin/env python3
"""v9.369 — Sync splash screen theme colors with current 8 themes (add slate+jade, remove old)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_themes = """    warm:       { bg:'#F4C57E', deep:'#E8B260', ring:'rgba(180,100,20,0.35)',  glow:'rgba(180,100,20,0.7)' },
    dark:       { bg:'#2C3554', deep:'#1E2640', ring:'rgba(80,110,220,0.35)',  glow:'rgba(80,110,220,0.7)' },
    candy:      { bg:'#FFE8F4', deep:'#FFD0EC', ring:'rgba(180,0,100,0.35)',   glow:'rgba(220,40,120,0.7)' },
    lavender:   { bg:'#EEE8FF', deep:'#DDD0FF', ring:'rgba(100,50,220,0.35)', glow:'rgba(120,60,240,0.7)' },
    ocean:      { bg:'#E0F4F8', deep:'#C8EAF2', ring:'rgba(0,100,160,0.35)',  glow:'rgba(0,130,190,0.7)' },
    peach:      { bg:'#FFE8D8', deep:'#FFD8C0', ring:'rgba(180,70,0,0.35)',   glow:'rgba(210,80,20,0.7)' },
    lemon:      { bg:'#F8F8D8', deep:'#F0F0B8', ring:'rgba(100,100,0,0.35)',  glow:'rgba(130,130,0,0.7)' },
    coraltheme: { bg:'#FFE8E0', deep:'#FFD8CC', ring:'rgba(180,50,20,0.35)',  glow:'rgba(210,60,30,0.7)' },
    berry:      { bg:'#F0E8F8', deep:'#E0D0F0', ring:'rgba(120,0,180,0.35)', glow:'rgba(150,20,200,0.7)' },
    ice:        { bg:'#E8F4FF', deep:'#D0E8FF', ring:'rgba(0,60,160,0.35)',   glow:'rgba(20,90,200,0.7)' },
    sky:        { bg:'#E4EEF8', deep:'#C8D8EE', ring:'rgba(60,120,200,0.3)',  glow:'rgba(60,120,200,0.65)' },"""

new_themes = """    warm:  { bg:'#F4C57E', deep:'#E8B260', ring:'rgba(180,100,20,0.35)',  glow:'rgba(180,100,20,0.7)' },
    dark:  { bg:'#2C3554', deep:'#1E2640', ring:'rgba(80,110,220,0.35)',  glow:'rgba(80,110,220,0.7)' },
    peach: { bg:'#FFE8D8', deep:'#FFD8C0', ring:'rgba(180,70,0,0.35)',   glow:'rgba(210,80,20,0.7)' },
    lemon: { bg:'#F8F8D8', deep:'#F0F0B8', ring:'rgba(100,100,0,0.35)',  glow:'rgba(130,130,0,0.7)' },
    berry: { bg:'#F0E8F8', deep:'#E0D0F0', ring:'rgba(120,0,180,0.35)', glow:'rgba(150,20,200,0.7)' },
    ice:   { bg:'#E8F4FF', deep:'#D0E8FF', ring:'rgba(0,60,160,0.35)',   glow:'rgba(20,90,200,0.7)' },
    slate: { bg:'#E8EBF0', deep:'#D4D9E4', ring:'rgba(80,100,130,0.35)', glow:'rgba(90,110,150,0.7)' },
    jade:  { bg:'#E8F5EE', deep:'#D0EBD8', ring:'rgba(30,120,70,0.35)',  glow:'rgba(40,140,80,0.7)' },"""

assert old_themes in html, "FAIL: splash themes object"
html = html.replace(old_themes, new_themes, 1)

html = html.replace("const APP_VERSION = 'v9.368';", "const APP_VERSION = 'v9.369';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.369 — splash themes synced (slate+jade added, old themes removed)")
