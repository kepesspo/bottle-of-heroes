#!/usr/bin/env python3
# v10.212 — Büntetés sheet: fix magassag + gorgetheto nevek + fix gomb, es
# a kiosztas utan a szokasos result banner jon fel (nem kis toast)
#
# 1) Sok jatekosnal (10+) a "Büntetés — ki igyon?" lap eddig a DrinkDistributor
#    EGESZET (sorok + zaro gomb egyutt) a sheet gorgetheto tartalmaba tette —
#    a gomb igy a lista VEGEN allt, oda kellett gorgetni. Uj PenaltySheet
#    komponens: a SheetOverlay mar eleve tamogatja ezt (maxHeight:82vh +
#    footer prop, lasd pl. "Ki adja fel?" v.mas beallitas-lapok) — csak eddig
#    nem hasznaltuk ki. A sorok a gorgetheto children-be kerulnek, a gomb a
#    fix footer-be.
#
# 2) A kiosztas eddig egy kis toastot dobott ("Büntetés: Sere 2 · Kecsi 1").
#    Most a szokasos NAGY result bannert hasznaljuk (onResult), ugyanugy,
#    ahogy pl. a Sohanem vagy Fingerit jatek is teszi eltero adagoknal:
#    losers=[akik ittak], loseNote="Sere 2🍺, Kecsi 1🍺" — a bannerban nincs
#    egyetlen kozos "N korty" szam, mert fejenkent mas az osszeg.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─── 1) Uj PenaltySheet komponens, kozvetlenul a DrinkDistributor utan ───
sub("""      <button onClick={()=>onFinish(drinks)} style={{ width:'100%', padding:'12px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:15, borderRadius:14, border:'none', cursor:'pointer', boxShadow:T.shadow, marginTop:2, animation:'popIn .2s' }}>
        {total>0 ? `${total} korty kiosztva ✔` : 'Senki sem iszik ✔'}
      </button>
    </div>
  );
}""",
    """      <button onClick={()=>onFinish(drinks)} style={{ width:'100%', padding:'12px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:15, borderRadius:14, border:'none', cursor:'pointer', boxShadow:T.shadow, marginTop:2, animation:'popIn .2s' }}>
        {total>0 ? `${total} korty kiosztva ✔` : 'Senki sem iszik ✔'}
      </button>
    </div>
  );
}

// Büntetés lap — mint a DrinkDistributor, de a zaro gomb a SheetOverlay
// FIX footer-jebe kerul, a nevek pedig kulon gorgetheto reszben vannak.
// Igy sok jatekosnal sem kell a lista vegere gorgetni a gombhoz.
function PenaltySheet({ players, onClose, onFinish }) {
  const [drinks, setDrinks] = React.useState({});
  const add = (pid) => setDrinks(d => ({ ...d, [pid]: (d[pid]||0)+1 }));
  const remove = (pid) => setDrinks(d => {
    const cur = d[pid]||0; if (cur<=0) return d;
    const n = {...d}; if (cur===1) delete n[pid]; else n[pid]=cur-1; return n;
  });
  const total = Object.values(drinks).reduce((s,v)=>s+v,0);
  return (
    <SheetOverlay onClose={onClose} title="Büntetés — ki igyon?" footer={
      <button onClick={()=>onFinish(drinks)} style={{ width:'100%', padding:'12px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:15, borderRadius:14, border:'none', cursor:'pointer', boxShadow:T.shadow }}>
        {total>0 ? `${total} korty kiosztva ✔` : 'Senki sem iszik ✔'}
      </button>
    }>
      <div style={{ padding:'0 16px', display:'flex', flexDirection:'column', gap:12 }}>
        <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, lineHeight:1.5 }}>
          Játékon kívüli korty — wildcard megszegése, fogadás, bármi.
          A kiosztott korty a játékban szerzettel együtt számít.
        </div>
        <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8 }}>
          {players.map(p => {
            const cnt = drinks[p.id]||0;
            return (
              <div key={p.id} style={{ display:'flex', alignItems:'center', gap:8, padding:'7px 10px', background:T.surface, borderRadius:12, boxShadow:T.shadow }}>
                <PlayerAvatar player={p} size={30} />
                <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
                <div style={{ display:'flex', alignItems:'center', gap:5, flexShrink:0 }}>
                  <button onClick={()=>remove(p.id)} disabled={cnt===0}
                    style={{ width:26, height:26, borderRadius:7, border:'none', background:cnt>0?T.surfaceMuted:T.surfaceMuted, color:cnt>0?T.inkSoft:T.inkMute, fontFamily:T.font, fontSize:16, fontWeight:700, cursor:cnt>0?'pointer':'default' }}>−</button>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:cnt>0?T.coral:T.inkMute, minWidth:26, textAlign:'center' }}>{cnt>0?<React.Fragment>{cnt} <BohIcon name="beer" size={12} /></React.Fragment>:'–'}</span>
                  <button onClick={(e)=>{ add(p.id); if (window.bohFloat) window.bohFloat(e.currentTarget, `+${(drinks[p.id]||0)+1} 🍺`, T.coral); }}
                    style={{ width:26, height:26, borderRadius:7, border:'none', background:T.coral+'22', color:T.coral, fontFamily:T.font, fontSize:16, fontWeight:700, cursor:'pointer' }}>+</button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </SheetOverlay>
  );
}""",
    'PenaltySheet komponens')

# ─── 2) applyPenalty: toast helyett a nagy result banner (onResult) ───
sub("""  const [penaltyOpen, setPenaltyOpen] = useState(false);
  const applyPenalty = (assigned) => {
    setPenaltyOpen(false);
    const map = assigned || {};
    const total = Object.values(map).reduce((s, v) => s + v, 0);
    if (!total) return;
    const upd = playersRef.current.map(p => (map[p.id] || 0) > 0 ? { ...p, drinks: (p.drinks || 0) + map[p.id] } : p);
    setPlayers(upd);
    if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { players: upd, turn, gameIdx, round });
    const names = upd.filter(p => (map[p.id] || 0) > 0).map(p => `${p.name} ${map[p.id]}`).join(' · ');
    setWcToast({ name: names, penalty: true });
    setTimeout(() => setWcToast(null), 2600);
    try { if (typeof window.bohSound === 'function') window.bohSound('lose'); } catch (e) {}
  };""",
    """  const [penaltyOpen, setPenaltyOpen] = useState(false);
  const applyPenalty = (assigned) => {
    setPenaltyOpen(false);
    const map = assigned || {};
    const total = Object.values(map).reduce((s, v) => s + v, 0);
    if (!total) return;
    const upd = playersRef.current.map(p => (map[p.id] || 0) > 0 ? { ...p, drinks: (p.drinks || 0) + map[p.id] } : p);
    setPlayers(upd);
    if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { players: upd, turn, gameIdx, round });
    // Fejenkent mas az osszeg, ezert nincs egyetlen kozos "drinks" szam —
    // a loseNote sorolja fel nevenkent, ugyanugy mint pl. a Sohanem/Fingerit.
    const drinkers = upd.filter(p => (map[p.id] || 0) > 0);
    onResult({ losers: drinkers, loseNote: drinkers.map(p => `${p.name} ${map[p.id]}🍺`).join(', ') });
  };""",
    'applyPenalty')

# ─── 3) a penaltyOpen SheetOverlay+DrinkDistributor helyett PenaltySheet ───
sub("""      {penaltyOpen && (
        <SheetOverlay onClose={() => setPenaltyOpen(false)} title="Büntetés — ki igyon?">
          <div style={{ padding:'0 16px 20px', display:'flex', flexDirection:'column', gap:12 }}>
            <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, lineHeight:1.5 }}>
              Játékon kívüli korty — wildcard megszegése, fogadás, bármi.
              A kiosztott korty a játékban szerzettel együtt számít.
            </div>
            <DrinkDistributor players={players || []} onFinish={applyPenalty} />
          </div>
        </SheetOverlay>
      )}""",
    """      {penaltyOpen && (
        <PenaltySheet players={players || []} onClose={() => setPenaltyOpen(false)} onFinish={applyPenalty} />
      )}""",
    'penaltyOpen JSX')

# ─── 4) a penalty-toast agat mar senki nem allitja be — vissza az eredeti, egyszeru Toast-ra ───
sub("""      {wcToast && (
        <Toast>
          {wcToast.penalty
            ? <React.Fragment>Büntetés: {wcToast.name} <BohIcon name="beer" size={16} /></React.Fragment>
            : <React.Fragment>{wcToast.name} iszik 1-et! <BohIcon name="beer" size={16} /></React.Fragment>}
        </Toast>
      )}""",
    """      {wcToast && (
        <Toast>{wcToast.name} iszik 1-et! <BohIcon name="beer" size={16} /></Toast>
      )}""",
    'wcToast render')

sub("const APP_VERSION = 'v10.211';", "const APP_VERSION = 'v10.212';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — Buntetes lap: fix magassag + gorgetheto nevek + fix gomb + result banner')
