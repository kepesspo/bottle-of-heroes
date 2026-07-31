#!/usr/bin/env python3
# v10.237 — a Kvíz nyertese tényleg megkapja a pontot
#
# A játék végképernyője kiírta, hogy "+1 pont", a leírás is ezt ígéri
# ("Helyes válasz után pontot vehetsz"), de a pont SOHA nem került rá a
# játékosra: a QuizGame minden ágon csak korty-térképet adott át az
# onAdvance-nek, a pont-térképet (2. paraméter) egyszer sem. Így a bankolás
# csak kortyokat osztott ki, a nyertes 0 ponttal jött ki.
#
# Az onAdvance szignatúrája: onAdvance(drinkMap, pointsMap, opts) — lásd
# advanceLoverseny a PlayScreen-ben. A többi játék ugyanígy ad 1 pontot a
# nyertesnek (pl. IgazHamis, Számsor), ezért itt is 1 pont jár.
#
# Érintett ágak (mind = "a kihívó helyesen válaszolt és bankolt"):
#   - bankIt nulla-korty ága
#   - a kiosztó lap "Mentés ✓" (confirmGifts) és "Kihagyom" (skipGifts) gombja
#   - a jelenleg nem hívott confirmGift / distribute segédek — hogy ha
#     valaha visszakerülnek a felületre, ne térjenek el a többitől
#
# A rossz válasz ága változatlan: ott a kihívó iszik, és nem jár pont.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── bankIt: nincs összegyűjtött korty (elvben nem fordul elő, de legyen jó) ──
sub("""    } else {
      if (onAdvance) onAdvance({});
      if (onResult) onResult({ correct: true, playerName: challenger?.name, drinks: 0, subtitle: '+1 pont!' });
      setPhase('done');
    }""",
    """    } else {
      if (onAdvance) onAdvance({}, { [challenger?.id]: 1 });
      if (onResult) onResult({ correct: true, playerName: challenger?.name, drinks: 0, subtitle: '+1 pont!' });
      setPhase('done');
    }""",
    'bankIt nulla-korty ag')

# ── confirmGift (jelenleg nem hívott segéd) ──
sub("""    Object.entries(giftPool.assigned).forEach(([pid,n]) => { if(n>0) drinkMap[pid]=n; });
    if (onAdvance) onAdvance(drinkMap);""",
    """    Object.entries(giftPool.assigned).forEach(([pid,n]) => { if(n>0) drinkMap[pid]=n; });
    if (onAdvance) onAdvance(drinkMap, { [challenger?.id]: 1 });""",
    'confirmGift')

# ── distribute (jelenleg nem hívott segéd) ──
sub("""  const distribute = (pid) => {
    if (onAdvance) onAdvance({[pid]: kortyok});""",
    """  const distribute = (pid) => {
    if (onAdvance) onAdvance({[pid]: kortyok}, { [challenger?.id]: 1 });""",
    'distribute')

# ── confirmGifts: a kiosztó lap "Mentés ✓" gombja (ez a fő ág) ──
sub("""      Object.entries(gifts).forEach(([pid,n]) => { if(n>0) drinkMap[pid]=n; });
      if (onAdvance) onAdvance(drinkMap);
      const names = Object.entries(gifts).filter(([,n])=>n>0)
        .map(([pid,n]) => { const p=players.find(x=>x.id===pid); return `${p?.name||'?'} iszik ${n} kortyt`; });
      if (onResult) onResult({ correct: true, playerName: challenger?.name, drinks: 0,
        subtitle: names.length > 0 ? names.join(' · ') : `${pName} kiosztotta a kortyokat` });""",
    """      Object.entries(gifts).forEach(([pid,n]) => { if(n>0) drinkMap[pid]=n; });
      if (onAdvance) onAdvance(drinkMap, { [challenger?.id]: 1 });
      const names = Object.entries(gifts).filter(([,n])=>n>0)
        .map(([pid,n]) => { const p=players.find(x=>x.id===pid); return `${p?.name||'?'} iszik ${n} kortyt`; });
      if (onResult) onResult({ correct: true, playerName: challenger?.name, drinks: 0,
        subtitle: names.length > 0 ? `+1 pont · ${names.join(' · ')}` : `+1 pont · ${pName} kiosztotta a kortyokat` });""",
    'confirmGifts')

# ── skipGifts: "Kihagyom" — nem oszt kortyot, de a pont akkor is jár ──
sub("""    const skipGifts = () => {
      if (onAdvance) onAdvance({});
      if (onResult) onResult({ correct: true, playerName: challenger?.name, drinks: 0, subtitle: `${pName} bankolt — ${kortyok} korty!` });""",
    """    const skipGifts = () => {
      if (onAdvance) onAdvance({}, { [challenger?.id]: 1 });
      if (onResult) onResult({ correct: true, playerName: challenger?.name, drinks: 0, subtitle: `+1 pont · ${pName} nem osztott ki kortyot` });""",
    'skipGifts')

sub("const APP_VERSION = 'v10.236';", "const APP_VERSION = 'v10.237';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — a Kviz nyertese megkapja a pontot')
