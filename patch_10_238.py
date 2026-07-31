#!/usr/bin/env python3
# v10.238
#
# 1) Nem ugrál többé a profilkép játék közben.
#    A footer "Ki játszik" piruláján a kihívó avatarja `avatarNudge 3.4s …
#    infinite` animációval forgott meg 3,4 másodpercenként — végtelen ciklusban,
#    az egész parti alatt. Egy figyelemfelhívó mozdulatnak indult, de mivel
#    sosem áll le, csak zavaró. Két helyen volt (Egyéni és Páros pirula), a
#    keyframe-mel együtt kikerül.
#
# 2) A "Két játékos összehasonlítása" felkerül a szűrősor jobb szélére.
#    Eddig egy teljes szélességű gomb volt a lista tetején — egy egész sort
#    vitt el, ráadásul elgörgött. Most ikon-gomb a pirulák sorának jobb szélén,
#    ugyanott, ahol a fülsorban a MÚLT. Csak a Profil fülön és csak akkor
#    látszik, ha legalább 2 összehasonlítható profil van.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1/a. a végtelen avatar-animáció a Páros pirulán ──
sub(""", zIndex:2, overflow:'hidden', animation:'avatarNudge 3.4s 1.2s ease-in-out infinite' }}>{currentPlayer.img""",
    """, zIndex:2, overflow:'hidden' }}>{currentPlayer.img""",
    'avatarNudge paros')

# ── 1/b. ugyanez az Egyéni pirulán ──
sub("""transition:'box-shadow .3s', flexShrink:0, overflow:'hidden', animation:'avatarNudge 3.4s 1.2s ease-in-out infinite' }}>{currentPlayer.img""",
    """transition:'box-shadow .3s', flexShrink:0, overflow:'hidden' }}>{currentPlayer.img""",
    'avatarNudge egyeni')

# ── 1/c. a keyframe is kikerül, hogy ne éledjen újra ──
sub("""    @keyframes avatarNudge{0%,86%,100%{transform:rotate(0deg)}89%{transform:rotate(-8deg)}92%{transform:rotate(7deg)}95%{transform:rotate(-4deg)}98%{transform:rotate(2deg)}}
""",
    """""",
    'avatarNudge keyframe')

# ── 2/a. hány profil hasonlítható össze — a szűrősornak is kell ──
sub("""  const buszRows = [...profiles].filter(p => (pStats[p.id]?.busz_played || 0) > 0).sort((a, b) => {""",
    """  // Az összehasonlító gomb a szűrősorban ül, tehát a lista renderelése ELŐTT
  // kell tudni, van-e mit összehasonlítani. Ugyanaz a feltétel, mint a
  // profilRows-nál lejjebb.
  const comparableCount = profiles.filter(p => {
    const s = pStats[p.id] || {};
    return (s.totalSessions||0) > 0 || (s.totalPoints||0) > 0 || (s.totalDrinks||0) > 0 || (s.totalRounds||0) > 0;
  }).length;

  const buszRows = [...profiles].filter(p => (pStats[p.id]?.busz_played || 0) > 0).sort((a, b) => {""",
    'comparableCount')

# ── 2/b. a pirula-sor kap egy jobb szélre igazított összehasonlító gombot ──
sub("""          <div style={{ display:'flex', flexWrap:'wrap', gap:6, alignItems:'center' }}>
            {STATS_PERIODS.map(pr => {""",
    """          <div style={{ display:'flex', alignItems:'flex-start', gap:6 }}>
          <div style={{ flex:1, minWidth:0, display:'flex', flexWrap:'wrap', gap:6, alignItems:'center' }}>
            {STATS_PERIODS.map(pr => {""",
    'pirula-sor nyitas')

sub("""              );
            })()}
          </div>
          {view === 'season' && (() => {""",
    """              );
            })()}
          </div>
          {/* Összehasonlítás — a fülsorban a MÚLT-tal egy vonalban, jobb szélen.
              Korábban teljes szélességű gomb volt a lista tetején: egy egész
              sort vitt el, és elgörgött a listával. */}
          {tab === 'profil' && comparableCount >= 2 && (
            <button onClick={() => setShowCompare(true)} title="Két játékos összehasonlítása" aria-label="Két játékos összehasonlítása" style={{
              flexShrink:0, width:34, height:34, borderRadius:999, border:'none', background:T.surface,
              boxShadow:pfShadow, cursor:'pointer', display:'grid', placeItems:'center', padding:0,
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={T.mint} strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="M16 3h5v5M8 21H3v-5M21 3l-7 7M3 21l7-7"/></svg>
            </button>
          )}
          </div>
          {view === 'season' && (() => {""",
    'osszehasonlito gomb')

# ── 2/c. a régi, teljes szélességű gomb kikerül a listából ──
sub("""              {profilRows.length >= 2 && (
                <button onClick={() => setShowCompare(true)} style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:8, width:'100%', padding:'9px', borderRadius:14, border:'none', background:T.surface, boxShadow:pfShadow, color:T.ink, fontFamily:T.font, fontWeight:800, fontSize:13.5, cursor:'pointer', marginBottom:2 }}>
                  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke={T.mint} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 3h5v5M8 21H3v-5M21 3l-7 7M3 21l7-7"/></svg>
                  Két játékos összehasonlítása
                </button>
              )}
""",
    """""",
    'regi osszehasonlito gomb torlese')

sub("const APP_VERSION = 'v10.237';", "const APP_VERSION = 'v10.238';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — nincs tobbe ugralo avatar; az osszehasonlitas a szurosorban')
