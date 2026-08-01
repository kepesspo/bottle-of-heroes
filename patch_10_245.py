#!/usr/bin/env python3
# v10.245
#
# ── 1. A result banner profilképe nem villog/ugrál többé ─────────────────────
# MÉRVE: a bannerben lévő <img> elemet lekövettük 3 másodpercig — a csomópont
# ELTŰNT a DOM-ból (isConnected=false), 40 mintavételből 19-szer volt épp
# lecserélve. A helye nem változott (74.3, 245.6, 52), tehát nem elmozdult:
# ÚJRA ÉS ÚJRA ÚJRAÉPÜLT, és a kép minden alkalommal újra dekódolódott.
#
# Az ok: a Pile / WinZone / LoseZone / NeutralZone / MiniHalf / MiniNeutral
# komponensek a render FÜGGVÉNYÉN BELÜL vannak deklarálva, és JSX-ként
# (<WinZone />) használjuk őket. Így a PlayScreen minden újrarajzolásakor ÚJ
# függvény-azonosságot kapnak, a React pedig más komponens-típusnak látja őket
# → leszedi és újramountolja az egész részfát. A PlayScreen pedig sokszor
# rajzol újra (időzítők, korty/pont pulzus, szoba-események).
#
# Javítás: nem komponensként, hanem sima FÜGGVÉNYHÍVÁSKÉNT ágyazzuk be őket
# (WinZone() a <WinZone /> helyett). Így nincs komponens-határ, a visszaadott
# elemek a szülő gyerekeként reconciliálódnak, és az <img> a helyén marad.
# (Hookot egyik sem használ, ezért a közvetlen hívás rendben van.)
#
# ── 2. A Blackjack host-választó teteje a státuszsáv alá lógott ──────────────
# MÉRVE (szimulált env(safe-area-inset-top)=62px):
#     a réteg teteje: -62 px, a banner teteje: 28 px  →  34 px-szel a sáv alatt
#
# A HostPickScreen PORTÁLBAN, a body alá renderel, tehát a position:fixed a
# VIEWPORT-hoz igazodik — nincs mit kompenzálni. A `top: calc(-1 * env(...))`
# viszont felhúzta a réteget a kijelző fizikai teteje FÖLÉ, és a fejléc
# paddingje csak részben adta vissza. A negatív eltolás kikerül; a
# `paddingTop: calc(28px + env(safe-area-inset-top))` már eddig is ott volt,
# az végzi a dolgát.
#
# FIGYELEM: a többi ilyen mintájú réteg NEM portál (a gyökér konténerben ül,
# aminek van paddingTop-ja) — azokhoz nem nyúlunk. Lásd docs/safe-area.md.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what, count=1):
    global src
    assert src.count(old) == count, '%s: %d talalat (vart %d)' % (what, src.count(old), count)
    src = src.replace(old, new)

# ═══════════ 1. result banner — komponens helyett függvényhívás ═══════════
sub("""        const Pile = ({ list, size, overlap, borderW, emptyEmoji }) => {""",
    """        // FONTOS: ezek a "komponensek" a renderen BELUL keletkeznek, tehat minden
        // ujrarajzolaskor uj fuggveny-azonossagot kapnanak. Ha JSX-kent
        // hasznalnank oket (<Pile />), a React mas tipusnak latna es
        // ujramountolna a reszfat — a profilkep <img>-je minden korben
        // ujraepulne es ujra dekodolodna, ami villogasnak/ugralasnak latszik.
        // Ezert mindenhol SIMA FUGGVENYHIVASSAL agyazzuk be oket.
        const Pile = ({ list, size, overlap, borderW, emptyEmoji }) => {""",
    'Pile komment')

sub("""              <Pile list={list} size={28} overlap={9} borderW={2} emptyEmoji={kind==='win'?'🌟':'🍺'} />""",
    """              {Pile({ list, size:28, overlap:9, borderW:2, emptyEmoji: kind==='win'?'🌟':'🍺' })}""",
    'Pile mini')

sub("""            <Pile list={winners} size={split?52:60} overlap={16} borderW={3} emptyEmoji="🌟" />""",
    """            {Pile({ list: winners, size: split?52:60, overlap:16, borderW:3, emptyEmoji:'🌟' })}""",
    'Pile win')

sub("""            <Pile list={losers} size={split?52:60} overlap={16} borderW={3} emptyEmoji="🍺" />""",
    """            {Pile({ list: losers, size: split?52:60, overlap:16, borderW:3, emptyEmoji:'🍺' })}""",
    'Pile lose')

sub("""<MiniNeutral />""", """MiniNeutral()""", 'MiniNeutral', count=2)
sub("""<MiniHalf list={winners} kind="win" />""", """MiniHalf({ list: winners, kind:'win' })""", 'MiniHalf win', count=2)
sub("""<MiniHalf list={losers} kind="lose" />""", """MiniHalf({ list: losers, kind:'lose' })""", 'MiniHalf lose', count=2)

sub("""              {neutral && <NeutralZone />}""",
    """              {neutral && NeutralZone()}""",
    'NeutralZone')

sub("""                  <div style={{ flex:'1 1 0', minWidth:0, display:'flex' }}><WinZone /></div>
                  <div style={{ flex:'1 1 0', minWidth:0, display:'flex' }}><LoseZone /></div>""",
    """                  <div style={{ flex:'1 1 0', minWidth:0, display:'flex' }}>{WinZone()}</div>
                  <div style={{ flex:'1 1 0', minWidth:0, display:'flex' }}>{LoseZone()}</div>""",
    'split zonak')

sub("""                  {hasWin && <WinZone />}
                  {hasLose && <LoseZone />}""",
    """                  {hasWin && WinZone()}
                  {hasLose && LoseZone()}""",
    'egyszeres zonak')

# ═══════════ 2. HostPickScreen — ne lógjon a státuszsáv alá ═══════════
sub("""    <div style={{ position:'fixed', top:'calc(-1 * env(safe-area-inset-top))', left:0, right:0, bottom:0, zIndex:1400, background:T.bg, display:'flex', flexDirection:'column' }}>""",
    """    {/* PORTAL a body ala: a position:fixed a VIEWPORT-hoz igazodik, tehat nincs
        mit kompenzalni. A korabbi negativ top a kijelzo fizikai teteje FOLE
        huzta a reteget, es a banner 34 px-szel a statuszsav ala kerult.
        A safe area-t a lenti paddingTop intezi. Lasd docs/safe-area.md. */}
    <div style={{ position:'fixed', top:0, left:0, right:0, bottom:0, zIndex:1400, background:T.bg, display:'flex', flexDirection:'column' }}>""",
    'HostPickScreen top')

sub("const APP_VERSION = 'v10.244';", "const APP_VERSION = 'v10.245';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — banner img stabil; host-valaszto nem log a statuszsav ala')
