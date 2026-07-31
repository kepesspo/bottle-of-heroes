#!/usr/bin/env python3
# v10.229 — a teljes képernyős magasság MÉRT abszolút érték, ne 100dvh-ból számolt
#
# A készülékről végre pontos adatok jöttek (Beállítások > diagnosztika):
#     screen=874  inner=812  envTop=62
#
# A 100dvh viszont NEM viselkedik következetesen: a v10.227-ben a
# calc(100dvh + 62px) képlet a gombot ~901pt-ra tolta (a kijelző 874pt),
# vagyis ott a 100dvh nem 812, hanem 874 körül volt — miközben a v10.226-ban
# ugyanez a 100dvh 812-ként viselkedett. Ezt a bizonytalanságot nem lehet
# képlettel kikerülni.
#
# Ezért a 100dvh-t kivesszük a képletből: a teljes képernyős elemek magassága
# egy MÉRT, abszolút pixelérték lesz — telepített módban pontosan a fizikai
# kijelző magassága (screen.height). Nincs több feltételezés arról, hogy az
# iOS mit ért "viewport magasság" alatt.
#
# Böngészőben a változó nincs beállítva, így a 100dvh tartalék lép életbe —
# ott a dinamikus böngésző-sávok miatt épp az a helyes.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─── 1) a fejléc-szkript: --app-h (abszolút magasság) ───
sub("""        var d = 0;
        if(st && window.screen && window.screen.height)
          d = Math.round(window.screen.height - window.innerHeight);
        if(!(d > 0) || d > 200) d = 0;   // csak pozitiv, ertelmes hiany
        document.documentElement.style.setProperty('--app-vh-fix', d + 'px');
        window.__bohVh = { standalone: !!st, screenH: (window.screen||{}).height,
                           innerH: window.innerHeight, fix: d };""",
    """        // Telepitett modban a teljes kepernyos magassag = a FIZIKAI kijelzo
        // magassaga. Abszolut, mert ertek: nem fugg attol, hogy az iOS mit ert
        // 100dvh alatt (az verziorol verziora mast adott). Bongeszoben nem
        // allitjuk be -> a CSS 100dvh tartalek lep eletbe, ott az a helyes.
        var sh = (window.screen && window.screen.height) || 0;
        var ok = st && sh > 0 && sh >= window.innerHeight && sh - window.innerHeight <= 200;
        if(ok) document.documentElement.style.setProperty('--app-h', sh + 'px');
        else   document.documentElement.style.removeProperty('--app-h');
        window.__bohVh = { standalone: !!st, screenH: sh, innerH: window.innerHeight,
                           appH: ok ? sh : null };""",
    'app-h szamitas')

# ─── 2) CSS: --app-vh-fix helyett nincs alapértelmezés (a fallback a 100dvh) ───
sub("""    :root { --app-vh-fix: 0px; }   /* erteket a fejlecben futo szkript meri es allitja be */""",
    """    /* --app-h: a teljes kepernyos elemek magassaga. Telepitett PWA-ban a
       fejlecben futo szkript meri be (a fizikai kijelzo magassaga); bongeszoben
       nincs beallitva, ilyenkor a 100dvh tartalek ervenyes. */""",
    'css komment')

# ─── 3) a három felhasználási hely ───
sub("""      <div key={creatingRoom ? 'creating' : screen} style={{ height:'calc(100dvh + var(--app-vh-fix))', width:'100%',""",
    """      <div key={creatingRoom ? 'creating' : screen} style={{ height:'var(--app-h, 100dvh)', width:'100%',""",
    'kepernyo-kontener')

sub("""      position:'fixed', inset:0, height:'calc(100dvh + var(--app-vh-fix))',""",
    """      position:'fixed', inset:0, height:'var(--app-h, 100dvh)',""",
    'SheetOverlay')

sub("""        <div style={{ position:'fixed', left:0, right:0, top:'calc(100dvh + var(--app-vh-fix) - 1px)', height:'160px', background:T.bg, zIndex:1, pointerEvents:'none' }} />,""",
    """        <div style={{ position:'fixed', left:0, right:0, top:'calc(var(--app-h, 100dvh) - 1px)', height:'160px', background:T.bg, zIndex:1, pointerEvents:'none' }} />,""",
    'also festosav')

# ─── 4) diagnosztika: mutassa a tényleges 100dvh-t is ───
sub("""                const v = (typeof window !== 'undefined' && window.__bohVh) || {};
                const envTop = (() => { try {
                  const p = document.createElement('div');
                  p.style.cssText = 'position:fixed;top:0;height:env(safe-area-inset-top);visibility:hidden';
                  document.body.appendChild(p);
                  const h = Math.round(p.getBoundingClientRect().height);
                  p.remove(); return h;
                } catch (e) { return '?'; } })();""",
    """                const v = (typeof window !== 'undefined' && window.__bohVh) || {};
                const probe = (css) => { try {
                  const p = document.createElement('div');
                  p.style.cssText = 'position:fixed;top:0;visibility:hidden;height:' + css;
                  document.body.appendChild(p);
                  const h = Math.round(p.getBoundingClientRect().height);
                  p.remove(); return h;
                } catch (e) { return '?'; } };
                const envTop = probe('env(safe-area-inset-top)');
                const envBot = probe('env(safe-area-inset-bottom)');
                const dvh = probe('100dvh');""",
    'diagnosztika probe')

sub("""                    {APP_VERSION} · {v.standalone ? 'PWA' : 'böngésző'}<br/>
                    screen={String(v.screenH)} inner={String(v.innerH)} fix={String(v.fix)}px envTop={String(envTop)}px""",
    """                    {APP_VERSION} · {v.standalone ? 'PWA' : 'böngésző'}<br/>
                    screen={String(v.screenH)} inner={String(v.innerH)} 100dvh={String(dvh)}<br/>
                    appH={String(v.appH)} envTop={String(envTop)} envBot={String(envBot)}""",
    'diagnosztika szoveg')

sub("const APP_VERSION = 'v10.228';", "const APP_VERSION = 'v10.229';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — --app-h abszolut mert magassag, 100dvh csak bongeszo-tartalek')
