#!/usr/bin/env python3
# v10.227 — az alsó holt-zóna megszüntetése PWA-ban
#
# Kimérve a küldött készülék-képernyőképen: a "Tovább a játékokhoz" gomb alatt
# 96pt üres hely van. Ebből 34pt a jogos safe-area-bottom padding, a maradék
# 62pt felesleg — és az pont az env(safe-area-inset-top) értéke azon a
# készüléken (Dynamic Island).
#
# Ez a kódban MÁR DOKUMENTÁLT jelenség (lásd "Alsó festősáv" komment):
# black-translucent PWA-ban a 100dvh ~env-top-tal RÖVIDEBB a fizikai
# kijelzőnél, alul holt-zóna marad. Eddig ezt csak ELFEDTÜK (a holt-zónát egy
# fix csík festette az app háttérszínével) — a tartalom viszont a rövidebb
# területhez igazodott, ezért lógott a gomb ilyen magasan.
#
# Javítás: a teljes képernyős elemek magassága calc(100dvh + var(--app-vh-fix)),
# ahol a korrekció CSAK telepített (standalone) módban env(safe-area-inset-top),
# egyébként 0px. Böngészőben és opaque PWA-ban tehát semmi nem változik.
#
# Érintett: a képernyő-konténer, a SheetOverlay (a lapok alatti üres sáv is
# ugyanez a hiba volt), és az alsó festősáv (azt is lejjebb kell tolni,
# különben a most már lejjebb érő tartalomra festene).
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─── 1) standalone jelzés a <html>-en, a lehető legkorábban ───
sub("""  <script>(function(){var q=location.search;var bar=q.indexOf('screen=bar')!==-1;document.write('<meta name="apple-mobile-web-app-status-bar-style" content="'+(bar?'default':'black-translucent')+'"/>');})();</script>""",
    """  <script>(function(){var q=location.search;var bar=q.indexOf('screen=bar')!==-1;document.write('<meta name="apple-mobile-web-app-status-bar-style" content="'+(bar?'default':'black-translucent')+'"/>');})();</script>
  <!-- Telepitett (standalone) mod jelzese a <html>-en: ettol fugg a --app-vh-fix
       korrekcio, ami a black-translucent PWA alsó holt-zonajat szunteti meg. -->
  <script>(function(){try{var s=window.navigator.standalone===true||(window.matchMedia&&window.matchMedia('(display-mode: standalone)').matches);if(s)document.documentElement.classList.add('pwa-standalone');}catch(e){}})();</script>""",
    'standalone class')

# ─── 2) a korrekciós CSS-változó ───
sub("""    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
    html, body {""",
    """    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
    /* iOS black-translucent PWA: a 100dvh ~env-top-tal RÖVIDEBB a fizikai
       kijelzőnél, alul holt-zóna marad (lásd "Alsó festősáv" komment). Ezzel a
       korrekcióval a teljes képernyős elemek a kijelző aljáig érnek.
       Böngészőben / opaque PWA-ban a .pwa-standalone class nincs kitéve,
       tehát 0px — ott semmi nem változik. */
    :root { --app-vh-fix: 0px; }
    html.pwa-standalone { --app-vh-fix: env(safe-area-inset-top); }
    html, body {""",
    'app-vh-fix valtozo')

# ─── 3) a képernyő-konténer érjen a kijelző aljáig ───
sub("""      <div key={creatingRoom ? 'creating' : screen} style={{ height:'100dvh', width:'100%',""",
    """      <div key={creatingRoom ? 'creating' : screen} style={{ height:'calc(100dvh + var(--app-vh-fix))', width:'100%',""",
    'kepernyo-kontener magassaga')

# ─── 4) a SheetOverlay is (a lapok alatti üres sáv ugyanez a hiba) ───
sub("""      position:'fixed', inset:0, height:'100dvh',""",
    """      position:'fixed', inset:0, height:'calc(100dvh + var(--app-vh-fix))',""",
    'SheetOverlay magassaga')

# ─── 5) az alsó festősáv a megnövelt terület ALÁ kerüljön ───
sub("""        <div style={{ position:'fixed', left:0, right:0, top:'calc(100dvh - 1px)', height:'160px', background:T.bg, zIndex:1, pointerEvents:'none' }} />,""",
    """        <div style={{ position:'fixed', left:0, right:0, top:'calc(100dvh + var(--app-vh-fix) - 1px)', height:'160px', background:T.bg, zIndex:1, pointerEvents:'none' }} />,""",
    'also festosav pozicioja')

sub("const APP_VERSION = 'v10.226';", "const APP_VERSION = 'v10.227';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — also holt-zona megszuntetve (--app-vh-fix, csak standalone modban)')
