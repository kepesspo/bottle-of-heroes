#!/usr/bin/env python3
"""v8.62: Beer Pong — manuális sorsolásszerkesztő (csak host / offline)"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. BeerPongGame: manualEdit state + buildSEBracket no-shuffle variant ─────
OLD_RESHUFFLE_FUNC = """  const handleReshuffle = () => {"""

NEW_RESHUFFLE_FUNC = """  const [manualEdit, setManualEdit] = React.useState(false);
  const [manualOrder, setManualOrder] = React.useState(null); // null = auto

  // Build bracket from a specific player order (no internal shuffle)
  const buildSEBracketOrdered = (parts) => {
    const n = parts.length;
    if (n < 2) return [];
    const base = Math.pow(2, Math.floor(Math.log2(n)));
    const extra = n - base;
    if (extra === 0) return [buildSERound(parts)];
    const direct = parts.slice(0, base - extra);
    const prelim = parts.slice(base - extra);
    const round0 = buildSERound(prelim);
    const round1 = [];
    for (let i = 0; i < extra; i++) {
      round1.push({ p1: direct[i], p2: null, winner: null, loser: null, score: null, tbd: true });
    }
    for (let i = extra; i < direct.length; i += 2) {
      const p1 = direct[i], p2 = direct[i+1] || null;
      round1.push({ p1, p2, winner: p2 ? null : p1, loser: null, score: null });
    }
    return [round0, round1];
  };

  const handleReshuffle = () => {"""

assert OLD_RESHUFFLE_FUNC in content, "handleReshuffle not found"
content = content.replace(OLD_RESHUFFLE_FUNC, NEW_RESHUFFLE_FUNC, 1)
print("✓ manualEdit state + buildSEBracketOrdered hozzáadva")

# ── 2. canReshuffle után: manuális bracket alkalmazása ────────────────────────
OLD_CAN_RESHUFFLE_END = """  // ── Render match card ─────────────────────────────────────────────────────"""

NEW_CAN_RESHUFFLE_END = """  const applyManualOrder = (orderedPlayers) => {
    setManualOrder(orderedPlayers);
    setManualEdit(false);
    doneRef.current = false;
    setCups1(MAX_CUPS); setCups2(MAX_CUPS);
    setDrinkMap({}); setChampion(null); setExpandedRounds({});
    resetTimer();
    if (TOURNAMENT === 'se') {
      const br = buildSEBracketOrdered(orderedPlayers);
      setSeRounds(br); setSeCurRound(0);
      const fp = br.length > 0 ? br[0].findIndex(m => m.winner === null) : -1;
      setSeCurMatch(fp >= 0 ? fp : 0);
    } else if (TOURNAMENT === 'rr') {
      const ms = buildRRMatches(orderedPlayers);
      setRrMatches(ms); setRrIdx(0); setRrDone(false);
    }
  };

  // ── Render match card ─────────────────────────────────────────────────────"""

assert OLD_CAN_RESHUFFLE_END in content, "Render match card comment not found"
content = content.replace(OLD_CAN_RESHUFFLE_END, NEW_CAN_RESHUFFLE_END, 1)
print("✓ applyManualOrder hozzáadva")

# ── 3. Reshuffle gomb mellé: manuális szerkesztő gomb ─────────────────────────
OLD_RESHUFFLE_BTN = """          {canReshuffle && (
            <button onClick={handleReshuffle} title="Újra sorsol" style={{ position:'absolute', right:0, width:28, height:28, borderRadius:8, border:'none', cursor:'pointer', background:'rgba(20,30,50,0.07)', display:'grid', placeItems:'center', fontSize:14 }}>🔀</button>
          )}"""

NEW_RESHUFFLE_BTN = """          {canReshuffle && (
            <div style={{ position:'absolute', right:0, display:'flex', gap:4 }}>
              {mode !== 'Online' && (
                <button onClick={() => {
                  const ep = (MODE === 'csapat' && teamsReady && teamPlayersRef.current) ? teamPlayersRef.current : players;
                  setManualEdit(ep);
                }} title="Manuális sorsolás" style={{ width:28, height:28, borderRadius:8, border:'none', cursor:'pointer', background:'rgba(20,30,50,0.07)', display:'grid', placeItems:'center', fontSize:14 }}>✏️</button>
              )}
              <button onClick={handleReshuffle} title="Újra sorsol" style={{ width:28, height:28, borderRadius:8, border:'none', cursor:'pointer', background:'rgba(20,30,50,0.07)', display:'grid', placeItems:'center', fontSize:14 }}>🔀</button>
            </div>
          )}"""

assert OLD_RESHUFFLE_BTN in content, "reshuffle button not found"
content = content.replace(OLD_RESHUFFLE_BTN, NEW_RESHUFFLE_BTN, 1)
print("✓ Manuális szerkesztő gomb hozzáadva")

# ── 4. ManualBracketEditor overlay a BeerPongGame return-jében ───────────────
# Find the return of BeerPongGame — look for the outer wrapper div
OLD_BP_RETURN_START = """  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:14, width:'100%' }}>
      {/* Phase switcher for two-stage */}"""

NEW_BP_RETURN_START = """  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:14, width:'100%' }}>
      {manualEdit && (
        <ManualBracketEditor
          players={manualEdit}
          tournament={TOURNAMENT}
          onApply={applyManualOrder}
          onClose={() => setManualEdit(false)}
        />
      )}
      {/* Phase switcher for two-stage */}"""

assert OLD_BP_RETURN_START in content, "BeerPongGame return div not found"
content = content.replace(OLD_BP_RETURN_START, NEW_BP_RETURN_START, 1)
print("✓ ManualBracketEditor overlay hozzáadva")

# ── 5. ManualBracketEditor komponens ─────────────────────────────────────────
OLD_BPCONFETTI = """function BeerPongConfetti() {"""

NEW_BPCONFETTI = """function ManualBracketEditor({ players, tournament, onApply, onClose }) {
  const [order, setOrder] = React.useState([...players]);
  const move = (i, dir) => {
    const j = i + dir;
    if (j < 0 || j >= order.length) return;
    const next = [...order];
    [next[i], next[j]] = [next[j], next[i]];
    setOrder(next);
  };
  const isSE = tournament === 'se' || tournament.startsWith('grp_');
  return (
    <SheetOverlay onClose={onClose}>
      <div style={{ padding:'0 18px 18px', maxHeight:'80vh', overflowY:'auto' }}>
        <div style={{ textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, padding:'14px 0 4px', textTransform:'uppercase', letterSpacing:'-0.01em' }}>Sorsolás szerkesztése</div>
        <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, textAlign:'center', marginBottom:14 }}>
          {isSE ? 'Az 1. játszik a 2.-kel, a 3. a 4.-kel, stb.' : 'A sorrend határozza meg a körmérkőzés párosítását.'}
        </div>
        <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
          {order.map((p, i) => (
            <div key={p.id} style={{ display:'flex', alignItems:'center', gap:10, background:T.surface, borderRadius:14, padding:'10px 12px', boxShadow:T.shadow }}>
              <div style={{ fontFamily:'monospace', fontWeight:900, fontSize:15, color:T.inkMute, minWidth:20, textAlign:'center' }}>{i+1}</div>
              <div style={{ width:34, height:34, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', flexShrink:0 }}>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff' }}>{p.name.charAt(0).toUpperCase()}</span>
              </div>
              <div style={{ flex:1, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }}>{p.name}</div>
              <div style={{ display:'flex', flexDirection:'column', gap:3 }}>
                <button onClick={() => move(i, -1)} disabled={i===0} style={{ width:28, height:24, borderRadius:7, border:'none', cursor: i===0?'not-allowed':'pointer', background:T.surfaceMuted, fontSize:13, color:T.inkSoft, display:'grid', placeItems:'center', opacity:i===0?0.3:1 }}>▲</button>
                <button onClick={() => move(i, 1)} disabled={i===order.length-1} style={{ width:28, height:24, borderRadius:7, border:'none', cursor:i===order.length-1?'not-allowed':'pointer', background:T.surfaceMuted, fontSize:13, color:T.inkSoft, display:'grid', placeItems:'center', opacity:i===order.length-1?0.3:1 }}>▼</button>
              </div>
            </div>
          ))}
        </div>
        {isSE && order.length >= 2 && (
          <div style={{ marginTop:12, padding:'10px 14px', background:T.mintSoft, borderRadius:12 }}>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:T.mintDeep, marginBottom:6 }}>ELŐNÉZET</div>
            {Array.from({ length: Math.floor(order.length / 2) }, (_, i) => (
              <div key={i} style={{ fontFamily:T.font, fontSize:12, color:T.ink, padding:'2px 0' }}>
                {order[i*2]?.name} <span style={{ color:T.inkSoft }}>vs</span> {order[i*2+1]?.name || '—'}
              </div>
            ))}
          </div>
        )}
        <button onClick={() => onApply(order)} style={{ width:'100%', padding:'14px', borderRadius:14, background:T.mint, border:'none', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:16, cursor:'pointer', boxShadow:'0 5px 16px -5px rgba(79,194,160,0.6)', marginTop:16 }}>Alkalmaz</button>
      </div>
    </SheetOverlay>
  );
}

function BeerPongConfetti() {"""

assert OLD_BPCONFETTI in content, "BeerPongConfetti not found"
content = content.replace(OLD_BPCONFETTI, NEW_BPCONFETTI, 1)
print("✓ ManualBracketEditor komponens hozzáadva")

# ── 6. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.61';"
NEW_VER = "const APP_VERSION = 'v8.62';"
assert OLD_VER in content, "version not found"
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.62 saved")
