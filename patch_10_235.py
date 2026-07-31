#!/usr/bin/env python3
# v10.235 — kompaktabb Statisztika-fejléc
#
# Eddig négy vezérlősor ült egymás alatt, mire az első adat látszott:
#   1. fülek (Profil/Játékok/Beerpong/Busz) + MÚLT
#   2. "Összes ↔ Szezon" kapcsoló          ← idősáv
#   3. szezon-pirulák (ha szezon-nézet)     ← idősáv
#   4. Mind / Ma / 7 nap / Egyedi pirulák   ← idősáv
#   5. magyarázó sor ("Csak az adott időszakban…")
#
# A 2–4. ugyanazt csinálja: időszakot választ. A szezon is csak egy időszak,
# ezért egyetlen pirula-sorba került:
#
#   [Mind] [Ma] [7 nap] [Egyedi] [Nyári liga ▾]
#
# A szezon-pirula magát a szezon nevét mutatja; ha több szezon van, a nyílra
# koppintva nyílik le a választó (alapból zárva). A magyarázó sor csak az
# "Egyedi" időszaknál marad, ahol tényleg mond valamit.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. új state: le van-e nyitva a szezon-választó ──
sub("""  const [seasonId, setSeasonId] = React.useState(null);
""",
    """  const [seasonId, setSeasonId] = React.useState(null);
  const [seasonPick, setSeasonPick] = React.useState(false); // le van-e nyitva a szezon-valaszto
""",
    'seasonPick state')

# ── 2. az "Összes ↔ Szezon" kapcsoló helyére az egyesített idősáv-sor ──
sub("""          {/* Összes ↔ Szezon */}
          <div style={{ display:'flex', background:T.surface, padding:4, borderRadius:14, gap:4, boxShadow:pfShadow, marginBottom:10 }}>
            {[{ k:'all', l:'Összes' }, { k:'season', l:'Szezon' }].map(v => {
              const off = v.k === 'season' && seasons.length === 0;
              return (
                <button key={v.k} disabled={off} onClick={() => setView(v.k)} style={{
                  flex:1, minWidth:0, minHeight:40, borderRadius:11, border:'none', cursor: off ? 'default' : 'pointer',
                  fontFamily:T.font, fontWeight:900, fontSize:12.5, transition:'all .18s',
                  background: view === v.k ? T.mint : 'transparent', color: view === v.k ? '#fff' : (off ? T.inkMute : T.inkSoft), opacity: off ? 0.5 : 1,
                }}>{v.l}</button>
              );
            })}
          </div>
""",
    """          {/* Egyetlen idősáv-sor. Korábban két külön sor csinálta ugyanazt:
              egy "Összes ↔ Szezon" kapcsoló, alatta a Mind/Ma/7 nap/Egyedi
              pirulák. Mindkettő időszakot választ — a szezon is csak egy
              időszak —, ezért egy sorba kerültek. */}
          <div style={{ display:'flex', flexWrap:'wrap', gap:6, alignItems:'center' }}>
            {STATS_PERIODS.map(pr => {
              const on = view === 'all' && period === pr.key;
              return (
                <button key={pr.key} onClick={() => { setView('all'); setPeriod(pr.key); setSeasonPick(false); }} style={{
                  padding:'7px 14px', borderRadius:999, border:'none', flexShrink:0, cursor:'pointer', whiteSpace:'nowrap',
                  background: on ? T.mint : T.surface, color: on ? '#fff' : T.inkSoft,
                  fontFamily:T.font, fontWeight:800, fontSize:12.5, boxShadow:pfShadow, transition:'all .16s',
                }}>{pr.label}</button>
              );
            })}
            {seasons.length > 0 && (() => {
              const on = view === 'season';
              return (
                <button onClick={() => {
                  if (!on) {
                    setView('season');
                    if (!seasonId) setSeasonId(seasons[0].id);
                    setSeasonPick(seasons.length > 1);
                  } else setSeasonPick(v => !v);
                }} style={{
                  padding:'7px 12px 7px 14px', borderRadius:999, border:'none', minWidth:0, cursor:'pointer',
                  display:'flex', alignItems:'center', gap:5, maxWidth:'100%',
                  background: on ? T.mint : T.surface, color: on ? '#fff' : T.inkSoft,
                  fontFamily:T.font, fontWeight:800, fontSize:12.5, boxShadow:pfShadow, transition:'all .16s',
                }}>
                  <span style={{ overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{on && curSeason ? curSeason.name : 'Szezon'}</span>
                  {seasons.length > 1 && (
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink:0, transform: (on && seasonPick) ? 'rotate(180deg)' : 'none', transition:'transform .18s' }}><path d="M6 9l6 6 6-6"/></svg>
                  )}
                </button>
              );
            })()}
          </div>
""",
    'egyesitett idosav-sor')

# ── 3. a szezon-pirulák csak lenyitva látszanak (és csak több szezonnál) ──
sub("""                <div style={{ display:'flex', flexWrap:'wrap', gap:8 }}>
                  {seasons.map(se => (
                    <button key={se.id} onClick={() => setSeasonId(se.id)} style={{
                      padding:'8px 16px', borderRadius:999, border:'none', flexShrink:0, cursor:'pointer', whiteSpace:'nowrap',
                      background: seasonId === se.id ? T.mint : T.surface, color: seasonId === se.id ? '#fff' : T.inkSoft,
                      fontFamily:T.font, fontWeight:800, fontSize:12.5, boxShadow:pfShadow, transition:'all .16s',
                    }}>{se.name}</button>
                  ))}
                </div>
""",
    """                {/* Csak lenyitva — a kiválasztott szezon neve a fenti pirulán látszik. */}
                {seasonPick && seasons.length > 1 && (
                  <div style={{ display:'flex', flexWrap:'wrap', gap:6, marginTop:8 }}>
                    {seasons.map(se => (
                      <button key={se.id} onClick={() => { setSeasonId(se.id); setSeasonPick(false); }} style={{
                        padding:'7px 14px', borderRadius:999, border:'none', flexShrink:0, cursor:'pointer', whiteSpace:'nowrap',
                        background: seasonId === se.id ? T.mintDeep : T.surface, color: seasonId === se.id ? '#fff' : T.inkSoft,
                        fontFamily:T.font, fontWeight:800, fontSize:12.5, boxShadow:pfShadow, transition:'all .16s',
                      }}>{se.name}</button>
                    ))}
                  </div>
                )}
""",
    'szezon-valaszto lenyithato')

# ── 4. a régi pirula-sor törlése; a magyarázó sor csak "Egyedi"-nél marad ──
sub("""          {view === 'all' && (
          <React.Fragment>
          <div style={{ display:'flex', flexWrap:'wrap', gap:8 }}>
            {STATS_PERIODS.map(pr => (
              <button key={pr.key} onClick={() => setPeriod(pr.key)} style={{
                padding:'8px 16px', borderRadius:999, border:'none', flexShrink:0, cursor:'pointer', whiteSpace:'nowrap',
                background: period === pr.key ? T.mint : T.surface, color: period === pr.key ? '#fff' : T.inkSoft,
                fontFamily:T.font, fontWeight:800, fontSize:12.5, boxShadow:pfShadow, transition:'all .16s',
              }}>{pr.label}</button>
            ))}
          </div>
          {period === 'custom' && (""",
    """          {view === 'all' && period === 'custom' && (""",
    'regi pirula-sor torlese')

sub("""          {period !== 'all' && (
            <div style={{ fontFamily:T.font, fontSize:11.5, color:T.inkMute, marginTop:10, paddingLeft:2, display:'flex', alignItems:'center', gap:6 }}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke={T.inkMute} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink:0 }}><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
              {period === 'custom' ? 'A megadott időszakban lejátszott partik számítanak bele.' : 'Csak az adott időszakban lejátszott partik számítanak bele.'}
            </div>
          )}
          </React.Fragment>
          )}
""",
    """          {view === 'all' && period === 'custom' && (
            <div style={{ fontFamily:T.font, fontSize:11.5, color:T.inkMute, marginTop:8, paddingLeft:2, display:'flex', alignItems:'center', gap:6 }}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke={T.inkMute} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink:0 }}><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
              A megadott időszakban lejátszott partik számítanak bele.
            </div>
          )}
""",
    'magyarazo sor csak Egyedi-nel')

# a "Kezdés / Vége" kártya záró )} után már nincs Fragment — a lezárás rendben,
# mert a 4. csere a nyitó feltételt írta át egyetlen kifejezésre.

# ── 5. apró térnyerés: szűkebb padding a szűrősor és a lista körül ──
sub("""      {tab !== 'history' && (
        <div style={{ padding:'12px 16px 0', maxWidth:1180, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>""",
    """      {tab !== 'history' && (
        <div style={{ padding:'10px 16px 0', maxWidth:1180, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>""",
    'szurosor padding')

sub("""        <div style={{ position:'absolute', inset:0, overflowY:'auto', padding:'12px 16px 40px' }}><div style={{ maxWidth:1180, width:'100%', margin:'0 auto' }}>""",
    """        <div style={{ position:'absolute', inset:0, overflowY:'auto', padding:'10px 16px 40px' }}><div style={{ maxWidth:1180, width:'100%', margin:'0 auto' }}>""",
    'lista padding')

sub("""                <button onClick={() => setShowCompare(true)} style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:8, width:'100%', padding:'11px', borderRadius:14,""",
    """                <button onClick={() => setShowCompare(true)} style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:8, width:'100%', padding:'9px', borderRadius:14,""",
    'osszehasonlitas gomb')

sub("const APP_VERSION = 'v10.234';", "const APP_VERSION = 'v10.235';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — statisztika fejlec kompaktabb')
