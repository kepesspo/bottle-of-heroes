#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Keyframe — pill undo animáció
old_kf = "    @keyframes floatBob   {"
new_kf = """    @keyframes pillRewind  { 0%{transform:translateX(0) scaleX(1)} 25%{transform:translateX(12px) scaleX(0.95)} 55%{transform:translateX(-6px) scaleX(1.02)} 80%{transform:translateX(3px) scaleX(0.99)} 100%{transform:translateX(0) scaleX(1)} }
    @keyframes floatBob   {"""
assert old_kf in html, "FAIL: keyframe anchor"
html = html.replace(old_kf, new_kf, 1)

# ── 2. undoAnimating state hozzáadása
old_canundo = "  const [canUndo, setCanUndo] = useState(false);"
new_canundo = """  const [canUndo, setCanUndo] = useState(false);
  const [undoAnimating, setUndoAnimating] = React.useState(false);"""
assert old_canundo in html, "FAIL: canUndo state"
html = html.replace(old_canundo, new_canundo, 1)

# ── 3. undoLast — animáció előbb, akció utána
old_undo = """  const undoLast = () => {
    if (!undoRef.current) return;
    const { players: p, turn: t, gameIdx: g, round: r } = undoRef.current;
    undoRef.current = null;
    setCanUndo(false);
    setPlayers(p); setTurn(t); setGameIdx(g); setRound(r);
    setPendingCommit(null); setTransitioning(false); transRef.current = false;
    // Revert localStorage so refresh also shows old scores
    try { localStorage.setItem('boh_session', JSON.stringify({ players: p, turn: t, gameIdx: g, round: r, selectedGames, gameMeta })); } catch(e) {}
    // Revert Firestore so polling doesn't snap back to new scores
    if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { players: p, turn: t, gameIdx: g, round: r });
  };"""
new_undo = """  const undoLast = () => {
    if (!undoRef.current) return;
    setUndoAnimating(true);
    const snap = undoRef.current;
    setTimeout(() => {
      setUndoAnimating(false);
      const { players: p, turn: t, gameIdx: g, round: r } = snap;
      undoRef.current = null;
      setCanUndo(false);
      setPlayers(p); setTurn(t); setGameIdx(g); setRound(r);
      setPendingCommit(null); setTransitioning(false); transRef.current = false;
      try { localStorage.setItem('boh_session', JSON.stringify({ players: p, turn: t, gameIdx: g, round: r, selectedGames, gameMeta })); } catch(e) {}
      if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { players: p, turn: t, gameIdx: g, round: r });
    }, 480);
  };"""
assert old_undo in html, "FAIL: undoLast"
html = html.replace(old_undo, new_undo, 1)

# ── 4. Pill wrapper — animáció alkalmazása undoAnimating esetén
old_pill_wrap = "        {/* Player pill — flex:3 */}\n        <div style={{ flex:3, minWidth:0, overflow:'hidden', display:'flex', alignItems:'stretch' }}>"
new_pill_wrap = "        {/* Player pill — flex:3 */}\n        <div style={{ flex:3, minWidth:0, overflow:'hidden', display:'flex', alignItems:'stretch', animation: undoAnimating ? 'pillRewind .48s cubic-bezier(.2,.9,.3,1)' : undefined }}>"
assert old_pill_wrap in html, "FAIL: pill wrapper"
html = html.replace(old_pill_wrap, new_pill_wrap, 1)

# ── 5. Share kártya — shareCard funkció az EndScreen-ben
old_endscreen_fn = "function EndScreen({ players, go, resetGame, lastRound, scoreHistory }) {\n  const sorted = [...players].sort((a,b) => (b.points-a.points)||(a.drinks-b.drinks));"
new_endscreen_fn = """function EndScreen({ players, go, resetGame, lastRound, scoreHistory }) {
  const sorted = [...players].sort((a,b) => (b.points-a.points)||(a.drinks-b.drinks));
  const shareCard = () => {
    const W = 800, H = Math.max(400, 140 + Math.min(sorted.length, 6) * 72 + 40);
    const canvas = document.createElement('canvas');
    canvas.width = W; canvas.height = H;
    const ctx = canvas.getContext('2d');
    // Background
    const grad = ctx.createLinearGradient(0, 0, W, H);
    grad.addColorStop(0, '#0F172A'); grad.addColorStop(1, '#1E3A5F');
    ctx.fillStyle = grad; ctx.fillRect(0, 0, W, H);
    // Decorative top bar
    const topGrad = ctx.createLinearGradient(0, 0, W, 0);
    topGrad.addColorStop(0, '#4FC2A0'); topGrad.addColorStop(1, '#6366F1');
    ctx.fillStyle = topGrad; ctx.fillRect(0, 0, W, 6);
    // Title
    ctx.fillStyle = '#FFFFFF'; ctx.font = 'bold 32px system-ui,sans-serif'; ctx.textAlign = 'center';
    ctx.fillText('🍺 Bottle of Heroes', W/2, 56);
    ctx.fillStyle = '#94A3B8'; ctx.font = '16px system-ui,sans-serif';
    ctx.fillText(`${sorted.length} játékos · ${lastRound || '?'} kör`, W/2, 84);
    ctx.strokeStyle = 'rgba(255,255,255,0.1)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(40, 104); ctx.lineTo(W-40, 104); ctx.stroke();
    // Players
    const topN = sorted.slice(0, Math.min(6, sorted.length));
    const cols = topN.length > 3 ? 2 : 1;
    const colW = (W - 80) / cols;
    topN.forEach((p, i) => {
      const col = cols === 2 ? i % 2 : 0;
      const row = cols === 2 ? Math.floor(i / 2) : i;
      const x = 40 + col * colW, y = 120 + row * 72;
      const rank = i + 1;
      const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : `${rank}.`;
      // Avatar
      ctx.beginPath(); ctx.arc(x+26, y+26, 22, 0, Math.PI*2);
      ctx.fillStyle = p.color; ctx.fill();
      ctx.fillStyle = '#FFF'; ctx.font = 'bold 18px system-ui,sans-serif'; ctx.textAlign = 'center';
      ctx.fillText(p.name.charAt(0).toUpperCase(), x+26, y+33);
      // Medal & name
      ctx.textAlign = 'left';
      ctx.font = '20px system-ui,sans-serif'; ctx.fillText(medal, x+58, y+20);
      ctx.fillStyle = '#F1F5F9'; ctx.font = 'bold 18px system-ui,sans-serif';
      ctx.fillText(p.name.length > 18 ? p.name.slice(0,17)+'…' : p.name, x+58, y+42);
      ctx.fillStyle = '#64748B'; ctx.font = '14px system-ui,sans-serif';
      ctx.fillText(`⭐ ${p.points} pont   🍺 ${p.drinks} korty`, x+58, y+60);
    });
    // Footer URL
    ctx.fillStyle = 'rgba(255,255,255,0.25)'; ctx.font = '13px system-ui,sans-serif'; ctx.textAlign = 'center';
    ctx.fillText('kepesspo.github.io/bottle-of-heroes', W/2, H-16);
    // Share / download
    canvas.toBlob(async (blob) => {
      const file = new File([blob], 'bottle-of-heroes.png', { type:'image/png' });
      if (navigator.share && navigator.canShare && navigator.canShare({ files:[file] })) {
        try { await navigator.share({ files:[file], title:'Bottle of Heroes — Végeredmény' }); return; } catch(e) {}
      }
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href=url; a.download='bottle-of-heroes.png'; a.click();
      setTimeout(()=>URL.revokeObjectURL(url),1000);
    });
  };"""
assert old_endscreen_fn in html, "FAIL: EndScreen fn"
html = html.replace(old_endscreen_fn, new_endscreen_fn, 1)

# ── 6. Share gomb a BottomBar-ba
old_bottombar = """      <BottomBar>
        <div style={{ display:'flex', gap:10 }}>
          <button onClick={resetGame} style={{ flex:1, minHeight:56, border:`2px solid ${T.inkMute}`, background:'transparent', color:T.ink, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, borderRadius:999, cursor:'pointer' }}>Új meccs</button>
          <button onClick={() => go('home')} style={{ flex:1, minHeight:56, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, borderRadius:999, cursor:'pointer', boxShadow:T.shadow }}>Főmenü</button>
        </div>
      </BottomBar>"""
new_bottombar = """      <BottomBar>
        <div style={{ display:'flex', gap:10 }}>
          <button onClick={resetGame} style={{ flex:1, minHeight:56, border:`2px solid ${T.inkMute}`, background:'transparent', color:T.ink, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, borderRadius:999, cursor:'pointer' }}>Új meccs</button>
          <button onClick={shareCard} style={{ width:56, minHeight:56, border:'none', background:T.surface, color:T.ink, borderRadius:999, cursor:'pointer', display:'grid', placeItems:'center', boxShadow:T.shadow, flexShrink:0 }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
          </button>
          <button onClick={() => go('home')} style={{ flex:1, minHeight:56, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, borderRadius:999, cursor:'pointer', boxShadow:T.shadow }}>Főmenü</button>
        </div>
      </BottomBar>"""
assert old_bottombar in html, "FAIL: BottomBar"
html = html.replace(old_bottombar, new_bottombar, 1)

html = html.replace("const APP_VERSION = 'v9.312';", "const APP_VERSION = 'v9.313';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.313 — Share kártya (Canvas), Undo pill animáció")
