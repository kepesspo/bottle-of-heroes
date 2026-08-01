#!/usr/bin/env python3
# v10.266 — három javítás: becsúszó kicsi sáv, fejjel lefelé álló nevek, levágott árnyék
#
# 1. A KICSI SÁV OLDALRÓL CSÚSZOTT BE
# A sávot `left:50% + transform:translateX(-50%)` igazítja középre, az animációja
# viszont `transform: translateY(12px)` → az animáció ELSŐ képkockájától kezdve a
# saját transform-ja FELÜLÍRJA a középre igazítást, tehát a sáv a fél
# szélességével jobbra ugrik, majd a végén visszaugrik. Ez látszott
# oldalról-becsúszásnak.
# Javítás: az animáció csak az átlátszóságot mozgatja (bohFadeIn) — semmi
# transform, tehát nincs mit felülírnia. Ahogy kérted: elég, ha megjelenik.
#
# 2. FEJJEL LEFELÉ ÁLLÓ NEVEK ÉS AVATAROK
# A címkék a forgó kerék GYEREKEI, saját forgatás nélkül — tehát pontosan
# annyival dőlnek, amennyivel a kerék áll. A kerék nyugalmi szöge nem 360
# többszöröse (a nyertes cikkelyre áll be), ezért a nevek tetszőleges szögben
# állnak meg, sokszor fejjel lefelé.
# Javítás: minden címke ELLENFORGATJA magát a kerék szögével, ugyanazzal az
# átmenettel. Így pörgés közben KERINGENEK, de végig állva maradnak.
#
# 3. FURA ÁRNYÉK A KERÉK MÖGÖTT
# A v10.264-ben tett `overflow:hidden` levágta a kerék saját vetett árnyékát a
# konténer szélénél — innen a szögletes árnyék-perem. Az árnyéknak nem volt hová
# esnie, mert a kerék pontosan olyan széles volt, mint a konténer.
# Javítás: a kerék 24 px-szel keskenyebb (12 px hely marad kétoldalt), a konténer
# 20 px-szel magasabb, az árnyék pedig szorosabb (12 px elmosás) — így elfér a
# levágáson belül. A vízszintes görgetés elleni védelem marad.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. a kicsi sáv csak megjelenik ──
sub("""    @keyframes miniBarIn { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }""",
    """    @keyframes miniBarIn { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
    /* Csak megjelenes, SEMMI transform: a kicsi sav kozepre igazitasa maga is
       transform (translateX(-50%)), amit egy transform-os animacio felulirna —
       attol csuszott be oldalrol. Lasd patch_10_266.py */
    @keyframes bohFadeIn { from{opacity:0} to{opacity:1} }""",
    'bohFadeIn keyframe')

sub("""zIndex:45, animation:'miniBarIn .25s ease-out', cursor:'pointer' }}>""",
    """zIndex:45, animation:'bohFadeIn .18s ease-out', cursor:'pointer' }}>""",
    'kicsi sav animacio')

# ── 2. a cimkek ellenforgatnak, hogy allva maradjanak ──
sub("""              <div key={p.id} style={{ position:'absolute', left:cx, top:cy, transform:'translate(-50%,-50%)',
                                       display:'flex', flexDirection:'column', alignItems:'center', gap:3, pointerEvents:'none' }}>""",
    """              // A cimke ELLENFORGATJA magat a kerek szogevel, ugyanazzal az
              // atmenettel — igy porges kozben keringenek, de vegig ALLVA maradnak.
              // Enelkul pontosan annyival dolnek, amennyivel a kerek all, es a
              // nyugalmi szog nem 360 tobbszorose → fejjel lefele allnak meg.
              <div key={p.id} style={{ position:'absolute', left:cx, top:cy,
                                       transform:`translate(-50%,-50%) rotate(${-rotation}deg)`,
                                       transition: phase === 'spinning' ? `transform ${SPIN_MS}ms cubic-bezier(.16,.84,.28,1)` : 'none',
                                       display:'flex', flexDirection:'column', alignItems:'center', gap:3, pointerEvents:'none' }}>""",
    'cimke ellenforgatas')

# ── 3. az arnyeknak legyen helye a levagason belul ──
sub("""  const SIZE = Math.max(240, Math.min(wheelW || 288, 520));""",
    """  // 24 px-szel keskenyebb a konteneral: igy a kerek vetett arnyekanak marad
  // 12-12 px helye a levagason belul (lasd patch_10_266.py).
  const SIZE = Math.max(240, Math.min((wheelW || 288) - 24, 520));""",
    'kerek merete')

sub("""      <div ref={wheelWrapRef} style={{ position:'relative', width:'100%', height:SIZE + 26 * k, overflow:'hidden' }}>""",
    """      <div ref={wheelWrapRef} style={{ position:'relative', width:'100%', height:SIZE + 26 * k + 20, overflow:'hidden' }}>""",
    'kontener magassag')

sub("""          <svg width={SIZE} height={SIZE} style={{ display:'block', filter:'drop-shadow(0 6px 16px rgba(20,30,50,0.16))' }}>""",
    """          <svg width={SIZE} height={SIZE} style={{ display:'block', filter:'drop-shadow(0 5px 12px rgba(20,30,50,0.16))' }}>""",
    'szorosabb arnyek')

sub("const APP_VERSION = 'v10.265';", "const APP_VERSION = 'v10.266';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — sav csak megjelenik, nevek allva, arnyek nincs levagva')
