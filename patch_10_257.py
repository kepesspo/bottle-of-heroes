#!/usr/bin/env python3
# v10.257 — Korty-számláló a fejlécben („A1" — sebességtábla)
#
# MIT CSINÁL
# A KÖR gyűrűről lelóg egy kapszula: hány kortyot ér egy vesztes kör ebben a
# játékban, alatta pedig a nehézségi szint teli szélességű színes talpon.
# Így a nagy szám mellett ott van az indoklás is.
#
# 1. A TÉT FORRÁSA — új `stake` mező minden játék-definícióban
# Eddig az alap korty CSAK a játékok kódjában létezett (drinks: 1, drink-map…),
# tehát a fejléc nem tudhatta, mennyi a tét. Mostantól minden játék DEKLARÁLJA:
#     stake: [min, max]   — hány kortyot kap egy vesztes kör alapból
#     stake: null         — a játék maga osztja (tétek, zsetonok, percek)
# A számokat a játékok tényleges onAdvance-hívásaiból olvastam ki. Ahol a
# játék null-t deklarál, ott NEM jelenik meg kapszula — nem írunk ki olyan
# számot, amit nem tudunk. Inkább semmit, mint hamisat.
#
# 2. EGY FORRÁS A SZORZÓRA
# A `diffDrinks` eddig egy külön ternary volt (extreme?5:hard?3:mid?2:1), a
# DIFFICULTY_INFO-ban meg ugyanez `mult`-ként. Két hely, ugyanaz a szám —
# mostantól a DIFFICULTY_INFO az egyetlen forrás, onnan jön a szorzó, a név és
# a szín is.
#
# 3. WILDCARD
# A „dupla” wildcard alatt a talp sárgára vált, és a TELJES szorzót mutatja
# (Nehéz + dupla = ×6), nem két külön számot. Így a hirtelen megugró
# korty-szám azonnal indokolt.
#
# 4. AMIHEZ HOZZÁ KELLETT NYÚLNI
#   - A QR-gomb eddig a gyűrű JOBB ALSÓ sarkán ült — pont oda, ahová most a
#     korty-szám kerül. Átkerült a jobb FELSŐ sarokba.
#   - A kapszula kilóg a fejléc alól. A wildcard-sáv a jobb szélén ezért kap
#     helyet, különben a „Szabályszegő?” gomb alá lógna.
#   - Ha nincs pontozás (kikapcsolt korty-követés), nincs kapszula.
import sys, re

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. stake mező minden játékhoz ───────────────────────────────────────────
# A szamok a jatekok TENYLEGES onAdvance-hivasaibol jonnek. null = a jatek
# maga osztja a kortyot (tet/zseton/perc alapon), ott nincs ertelmes elore
# kiirhato szam.
STAKE = {
    'blackjack': None,        # zsetonos tetek, elo kiosztas
    'busz':      None,        # sajat gazdasag
    'beerpong':  None,        # raw: a nehezseg nem is szorozza
    'loverseny': None,        # raw: fogadasok
    'ringfire':  None,        # a huzott lap szabalya oszt, nem kovetjuk
    'ovfj':      None,        # nincs korty az onAdvance-ben
    'farkasos':  None,        # nincs korty
    'powerhour': None,        # a lejatszott percek szerint

    'imposztor': (2, 3),      # imposztor 3, tobbiek 2
    'kezcsere':  (1, 3),      # hibankent 1
    'hajime':    (1, 3),      # hibankent 1
    'kisebb':    (1, 4),      # maxFailPot — a pot +1 vagy ×2 lepesekben no
    'fingerit':  (1, 3),      # koronkenti kiosztas
    'collect':   (1, 3),      # bombDrinks
    'kopapir':   (1, 3),      # koronkent halmozodik
    'ritmus':    (1, 3),      # a kulonbseg szerint
    'meduza':    (1, 3),      # koronkenti kiosztas
    'cardbattle':(1, 3),      # koronkent halmozodik
}
# A jatek-definiciok sorai: "  { id:'x', roundTime:... difficulty:..." — a
# difficulty jelenlete zarja ki a hasonlo alaku, de mas celu objektumokat
# (pl. a busz sajat allapotai).
_lines = src.split('\n')
added = []
for i, ln in enumerate(_lines):
    g = re.match(r"^  \{ id:'([^']+)',", ln)
    if not g or 'difficulty:' not in ln or 'stake:' in ln:
        continue
    gid = g.group(1)
    v = STAKE.get(gid, (1, 1))
    txt = 'null' if v is None else '[%d,%d]' % v
    _lines[i] = ln.replace("{ id:'%s'," % gid, "{ id:'%s', stake:%s," % (gid, txt), 1)
    added.append(gid)
src = '\n'.join(_lines)
assert len(added) >= 44, 'kevés játék kapott stake mezőt: %d' % len(added)
for gid in STAKE:
    assert gid in added, 'nem kapott stake mezot: %s' % gid
print('stake mezo hozzaadva: %d jatekhoz' % len(added))

# ── 2. a szorzónak EGY forrása legyen ───────────────────────────────────────
sub("""  const diffDrinks = gameMeta?.difficulty === 'extreme' ? 5 : gameMeta?.difficulty === 'hard' ? 3 : gameMeta?.difficulty === 'mid' ? 2 : 1;""",
    """  // A nehezsegi szorzo EGY helyrol jon: a DIFFICULTY_INFO-bol. Eddig itt egy
  // kulon ternary allt ugyanazokkal a szamokkal — ket forras, elobb-utobb
  // szetcsuszik. Innen jon a nev es a szin is a korty-szamlalohoz.
  const diffMeta = DIFFICULTY_INFO.find(d => d.id === (gameMeta?.difficulty || 'easy')) || DIFFICULTY_INFO[0];
  const diffDrinks = diffMeta.mult;""",
    'diffDrinks egy forrasbol')

# ── 3. a tét kiszámolása ────────────────────────────────────────────────────
sub("""  const wcEffect = activeWildcard?.effect || null;
  const wcMult = wcEffect === 'double' ? 2 : 1;""",
    """  const wcEffect = activeWildcard?.effect || null;
  const wcMult = wcEffect === 'double' ? 2 : 1;

  // ── A TÉT: alap korty × nehezseg × wildcard ──
  // Csak akkor mutatjuk, ha a jatek deklaral alap tetet (stake) ES van
  // korty-kovetes. Amit nem tudunk, azt nem talaljuk ki.
  const stakeMult = diffDrinks * wcMult;
  const stakeBase = trackScores ? (currentGame?.stake || null) : null;
  const stakeLo = stakeBase ? stakeBase[0] * stakeMult : 0;
  const stakeHi = stakeBase ? stakeBase[1] * stakeMult : 0;
  const stakeText = !stakeBase ? null : (stakeLo === stakeHi ? String(stakeLo) : stakeLo + '–' + stakeHi);
  const [stakeInfo, setStakeInfo] = useState(false);""",
    'tet szamitas')

# ── 4. a kapszula a KÖR gyűrű alatt ─────────────────────────────────────────
sub("""          return (
            <div style={{ position:'relative', width:54, height:54, flexShrink:0 }}>
              <svg viewBox="0 0 54 54" style={{ position:'absolute', inset:0, width:'100%', height:'100%', transform:'rotate(-90deg)' }}>""",
    """          // A kapszula LELOG a fejlec ala: a sorban csak 54 px magas helyet
          // foglal, a tobbi tulnyulik. Ezert kell a pozicionalt kontener.
          const capW = stakeText ? 60 : 54;
          return (
            <div style={{ position:'relative', width:capW, height:54, flexShrink:0, zIndex:6 }}>
            <div onClick={stakeText ? () => setStakeInfo(true) : undefined}
                 style={{ position:'absolute', top:0, left:'50%', transform:'translateX(-50%)', width:capW,
                          display:'flex', flexDirection:'column', alignItems:'center',
                          ...(stakeText ? { background:T.surface, borderRadius:'30px 30px 14px 14px',
                                            boxShadow:'0 2px 10px rgba(20,30,50,0.16)', paddingTop:3,
                                            overflow:'hidden', cursor:'pointer' } : {}) }}>
            <div style={{ position:'relative', width:54, height:54, flexShrink:0 }}>
              <svg viewBox="0 0 54 54" style={{ position:'absolute', inset:0, width:'100%', height:'100%', transform:'rotate(-90deg)' }}>""",
    'kapszula nyitas')

sub("""              {roomCode && (
                <button onClick={() => setShowRoomQR(true)} title="QR kód — csatlakozás" style={{ position:'absolute', right:-3, bottom:-3, width:22, height:22, borderRadius:'50%', border:`2px solid ${T.surface}`, background:T.mint, color:'#fff', cursor:'pointer', display:'grid', placeItems:'center', boxShadow:'0 2px 6px rgba(0,0,0,0.25)', padding:0, zIndex:3 }}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h6v6H3V3zm2 2v2h2V5H5zm8-2h6v6h-6V3zm2 2v2h2V5h-2zM3 15h6v6H3v-6zm2 2v2h2v-2H5zm10-2h2v2h-2v-2zm4 0h2v2h-2v-2zm-4 4h2v2h-2v-2zm2 2h2v2h-2v-2zm2-2h2v2h-2v-2z"/></svg>
                </button>
              )}
            </div>
          );
        })()}
      </div>""",
    """              {/* A QR-gomb a jobb FELSO sarokba kerult: a jobb also sarkot most a
                  korty-szam foglalja. */}
              {roomCode && (
                <button onClick={(e) => { e.stopPropagation(); setShowRoomQR(true); }} title="QR kód — csatlakozás" style={{ position:'absolute', right:-3, top: stakeText ? -3 : undefined, bottom: stakeText ? undefined : -3, width:22, height:22, borderRadius:'50%', border:`2px solid ${T.surface}`, background:T.mint, color:'#fff', cursor:'pointer', display:'grid', placeItems:'center', boxShadow:'0 2px 6px rgba(0,0,0,0.25)', padding:0, zIndex:3 }}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h6v6H3V3zm2 2v2h2V5H5zm8-2h6v6h-6V3zm2 2v2h2V5h-2zM3 15h6v6H3v-6zm2 2v2h2v-2H5zm10-2h2v2h-2v-2zm4 0h2v2h-2v-2zm-4 4h2v2h-2v-2zm2 2h2v2h-2v-2zm2-2h2v2h-2v-2z"/></svg>
                </button>
              )}
            </div>
            {/* ── a TÉT: korty-szam + a nehezseg szines talpon ── */}
            {stakeText && (
              <React.Fragment>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, lineHeight:1.1, letterSpacing:'-0.03em',
                               color: wcMult > 1 ? '#8A6A08' : T.ink, fontVariantNumeric:'tabular-nums' }}>{stakeText}</span>
                <span style={{ fontFamily:T.font, fontWeight:800, fontSize:7.5, letterSpacing:'0.1em',
                               textTransform:'uppercase', color:T.inkMute, lineHeight:1 }}>korty</span>
                <span style={{ width:'100%', textAlign:'center', marginTop:3, padding:'4px 2px 4.5px',
                               background: wcMult > 1 ? T.yellow : diffMeta.tone, color:'#12233C',
                               fontFamily:T.font, fontWeight:900, fontSize:7.5, letterSpacing:'0.02em',
                               textTransform:'uppercase', lineHeight:1, fontVariantNumeric:'tabular-nums' }}>
                  {diffMeta.label} ×{stakeMult}
                </span>
              </React.Fragment>
            )}
            </div>
            </div>
          );
        })()}
      </div>
      {stakeInfo && (
        <DifficultyInfoSheet current={diffMeta.id} onClose={() => setStakeInfo(false)}
          note={`${tg(currentGame,'name')}: alap ${stakeBase[0] === stakeBase[1] ? stakeBase[0] : stakeBase[0] + '–' + stakeBase[1]} korty × ${diffMeta.label.toLowerCase()} (${diffMeta.mult})${wcMult > 1 ? ' × dupla (2)' : ''} = ${stakeText} korty`} />
      )}""",
    'kapszula tartalom')

# ── 5. a magyarázó lap kapjon konkrét bontást ───────────────────────────────
sub("""function DifficultyInfoSheet({ current, onClose }) {""",
    """function DifficultyInfoSheet({ current, onClose, note }) {""",
    'DifficultyInfoSheet szignatura')

sub("""      <div style={{ padding:'0 18px 18px' }}>
        <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, lineHeight:1.6, marginBottom:14 }}>""",
    """      <div style={{ padding:'0 18px 18px' }}>
        {/* A fejleci korty-szamlalobol nyitva ide jon a KONKRET bontas — a szam
            mellett ott az indoklas is. */}
        {note && (
          <div style={{ background:T.surfaceMuted, borderRadius:14, padding:'11px 13px', marginBottom:14,
                        fontFamily:T.font, fontWeight:800, fontSize:13, color:T.ink, lineHeight:1.5 }}>{note}</div>
        )}
        <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, lineHeight:1.6, marginBottom:14 }}>""",
    'DifficultyInfoSheet note')

# ── 6. a wildcard-sáv ne kerüljön a kapszula alá ────────────────────────────
sub("""        <div style={{ flexShrink:0, maxWidth:960, width:'100%', margin:'0 auto', boxSizing:'border-box', padding:'2px 16px 6px' }}>""",
    """        <div style={{ flexShrink:0, maxWidth:960, width:'100%', margin:'0 auto', boxSizing:'border-box',
                      /* a korty-kapszula a jobb szelen lelog ide — hagyjunk neki helyet,
                         kulonben a "Szabalyszego?" gomb ala kerulne */
                      padding: stakeText ? '2px 76px 6px 16px' : '2px 16px 6px' }}>""",
    'wildcard sav helye')

sub("const APP_VERSION = 'v10.256';", "const APP_VERSION = 'v10.257';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — korty-szamlalo a fejlecben')
