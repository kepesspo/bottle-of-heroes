#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Pub PWA safe-area javítás: iOS standalone módban a fixed rétegek a status bar
# alatt kezdődnek és a home-indicator fölött végződnek — az app bevett mintája
# (top: -safe-top + paddingTop, ld. Events részletnézet) kerül a Pub overlay-ekre,
# és a görgető listák alsó paddingje is safe-area-kompenzált lesz.
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:80])
    src = src.replace(old, new)

# ── 1) Ital-sheet backdrop: teljes képernyős sötétítés a safe area-kkal együtt ──
rep("""          <div onClick={() => setSheetId(null)} style={{ position:'fixed', inset:0, background:'rgba(14,14,24,0.72)', zIndex:70, display:'flex', alignItems:'center', justifyContent:'center', padding:20, animation:'fadeIn .2s' }}>""",
"""          <div onClick={() => setSheetId(null)} style={{ position:'fixed', top:'calc(-1 * env(safe-area-inset-top))', left:0, right:0, bottom:'calc(-1 * env(safe-area-inset-bottom))', background:'rgba(14,14,24,0.72)', zIndex:70, display:'flex', alignItems:'center', justifyContent:'center', padding:'calc(env(safe-area-inset-top) + 20px) 20px calc(env(safe-area-inset-bottom) + 20px)', boxSizing:'border-box', animation:'fadeIn .2s' }}>""")

# ── 2) Keverés-űrlap: teljes képernyős réteg az app mintájára ──
rep("""    <div style={{ position:'fixed', inset:0, zIndex:80, background:T.bg, display:'flex', flexDirection:'column' }}>""",
"""    <div style={{ position:'fixed', top:'calc(-1 * env(safe-area-inset-top))', left:0, right:0, bottom:0, paddingTop:'env(safe-area-inset-top)', boxSizing:'border-box', zIndex:80, background:T.bg, display:'flex', flexDirection:'column' }}>""")

# ── 3) Űrlap görgető: alsó safe-area padding ──
rep("""      <div style={{ flex:1, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'16px 16px 32px', maxWidth:680, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>""",
"""      <div style={{ flex:1, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'16px 16px max(32px, calc(env(safe-area-inset-bottom) + 16px))', maxWidth:680, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>""")

# ── 4) Saját + receptek lista görgetők: alsó safe-area padding (2 előfordulás) ──
rep("""overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'14px 16px 40px', maxWidth:680""",
"""overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'14px 16px max(40px, calc(env(safe-area-inset-bottom) + 24px))', maxWidth:680""", count=2)

# ── 5) Verziobump ──
rep("const APP_VERSION = 'v9.987';", "const APP_VERSION = 'v9.988';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — Pub safe-area applied')
