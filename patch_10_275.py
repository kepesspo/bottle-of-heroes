#!/usr/bin/env python3
# v10.275 — a MÓDOK leirasai a valosagot mondjak, es surubb wildcard-tartomanyok
#
# HAROM LEIRAS PONTATLAN VOLT
#
#   1. Pontgyujtes — "A jatekosok minden gyoztes kornel csillagot kapnak."
#      Igaz, de elhallgatja a lenyeget: ez a `trackScores` kapcsolo, es
#      kikapcsolva NEM CSAK a pont marad el, hanem a KORTY sem kerul senkire,
#      es eltunik a tet-korong a fejlecbol. Vagyis kikapcsolva egy konyveles
#      nelkuli "Fun mode" jon letre. Ezt most kiirjuk.
#
#   2. Csoportos ivas — "Vesztes eseten az egesz csapat iszik egyet."
#      Ez EGYSZERUEN NEM IGAZ: a kodban semmi nem koti a veszteshez. Egy
#      veletlen 5-10 perces idozito, ami a kovetkezo kor/jatek kezdete utan
#      dob fel egy "Mindenki iszik" kepernyot, es a mennyiseg a FUTO JATEK
#      sajat nehezsegebol jon (konnyu 1, kozepes 2, nehez 3).
#      Figyelem: ez NEM a parti-nehezseg (Konnyu…Extrem, ×1…×5) — az a tethez
#      kell. Ket kulon fogalom ugyanazon a neven.
#
#   3. Wildcard korok — "Megadott korönként megjelenik…"
#      A "Milyen gyakran?" ertekek PERCEK, nem korok. Az idozito
#      `(lo + random*(hi-lo)) * 60000` ms-ra all be.
#
# A TARTOMANYOK SURUBBEK LESZNEK
#   4–8 / 8–15 / 15–25 / 25–40  ->  3–6 / 6–9 / 9–12 / 12–15
#   Az alapertelmezes 8–15 -> 6–9. Az alapertek HAROM helyen szerepelt
#   (a kivalasztott gomb, es a timer lo/hi erteke) — mindharom egyutt megy,
#   kulonben a felulet mast mutatna, mint amit a timer hasznal.
#
#   A "Milyen gyakran?" cimke is megkapja a mertekegyseget, mert a puszta
#   szamokrol nem derult ki, hogy percek.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─────────────────────────────────────────────────────────────────────────────
# 1-3. A harom leiras
# ─────────────────────────────────────────────────────────────────────────────
sub("""    modePointsInfo: 'A játékosok minden győztes körnél csillagot kapnak. A legtöbb csillaggal rendelkező játékos nyeri a meccset.',""",
    """    modePointsInfo: 'Bekapcsolva: a győztes körökért csillag jár, és a vesztesekre rákerül a korty — a parti végén ebből lesz az eredmény. Kikapcsolva „Fun mode”: se pontot, se kortyot nem könyvelünk, a fejlécből is eltűnik a korty-szám. Csak a játékok mennek, tét nélkül.',""",
    'points info')

sub("""    modeGroupInfo: 'Vesztes esetén az egész csapat iszik egyet, nem csak a vesztes játékos.',""",
    """    modeGroupInfo: 'Időnként, 5–10 percenként mindenki iszik egyszerre. Nem játék közben szakít félbe: a következő kör kezdete után jön elő. A mennyiség az éppen futó játék nehézségétől függ (könnyű 1, közepes 2, nehéz 3 korty) — ez a játék saját címkéje, nem a partira beállított nehézség.',""",
    'group info')

sub("""    modeWildcardInfo: 'Megadott körönként megjelenik egy random különleges szabály (pl. bal kézzel inni, pókerpofa kör). A szabály a következő wildcard körig érvényben marad, és a szabályszegőnek egy koppintással kortyot oszthatsz.',""",
    """    modeWildcardInfo: 'Néhány percenként (lásd „Milyen gyakran?”) megjelenik egy véletlen különleges szabály — pl. bal kézzel inni, pókerpofa kör. A szabály a következő wildcardig érvényben marad, és sávként ott marad a fejléc alatt; a sávra koppintva újra elolvashatod. A „Szabályszegő?” gombbal bárkinek oszthatsz kortyot. Három lapnak tényleges hatása is van: Dupla kör (minden pont és korty ×2), Fordított kör (a vesztes pontoz, a nyertes iszik) és Szerencsekör (+1 pont egy véletlen játékosnak).',""",
    'wildcard info')

# ─────────────────────────────────────────────────────────────────────────────
# 4. Surubb tartomanyok + uj alapertelmezes (6–9)
# ─────────────────────────────────────────────────────────────────────────────
sub("""const WILDCARD_RANGES = [
  { lo: 4,  hi: 8,  label: '4–8' },
  { lo: 8,  hi: 15, label: '8–15' },
  { lo: 15, hi: 25, label: '15–25' },
  { lo: 25, hi: 40, label: '25–40' },
];""",
    """// PERCEK, nem korok: az idozito (lo + random*(hi-lo)) * 60000 ms-ra all.
// Az alapertelmezes a 6–9 — ha ez valtozik, a HAROM `|| 6` / `|| 9` fallbacket
// is vinni kell vele (a kivalasztott gomb es a timer lo/hi erteke), kulonben a
// felulet mast mutatna, mint amit a timer hasznal.
const WILDCARD_RANGES = [
  { lo: 3,  hi: 6,  label: '3–6' },
  { lo: 6,  hi: 9,  label: '6–9' },
  { lo: 9,  hi: 12, label: '9–12' },
  { lo: 12, hi: 15, label: '12–15' },
];""",
    'ranges')

sub("""                        const sel = (meta.wildcardMin || 8) === n.lo;""",
    """                        const sel = (meta.wildcardMin || 6) === n.lo;""",
    'kivalasztott gomb')

sub("""    const lo = Math.max(1, gameMeta?.wildcardMin || 8);
    const hi = Math.max(lo, gameMeta?.wildcardMax || 15);""",
    """    const lo = Math.max(1, gameMeta?.wildcardMin || 6);
    const hi = Math.max(lo, gameMeta?.wildcardMax || 9);""",
    'timer alapertek')

# a puszta szamokrol nem derult ki, hogy percek
sub("""<span style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft, flex:1 }}>Milyen gyakran?</span>""",
    """<span style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft, flex:1 }}>Milyen gyakran?<br /><span style={{ fontWeight:700, fontSize:11, color:T.inkMute }}>percenként</span></span>""",
    'mertekegyseg')

sub("const APP_VERSION = 'v10.274';", "const APP_VERSION = 'v10.275';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — helyes leirasok, surubb wildcard-tartomanyok (alap: 6–9)')
