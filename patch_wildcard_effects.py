#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Wildcard mechanikai hatások: double (×2), lucky (véletlen +1 pont), reverse
# (vesztes pontoz / nyertes iszik). Admin jelölés + result banner követés.
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:80])
    src = src.replace(old, new)

# ── 1) WC_EFFECTS metaadat + effect a defaultokba ──
rep("""const WILDCARDS_DEFAULT = [
  { emoji:'🤚', text:'Bal kézzel kell inni ezen a körön!' },
  { emoji:'🤫', text:'Csend kör — aki hangosan nevet, iszik egyet!' },
  { emoji:'👆', text:'Mindenki mutasson valakire — a legtöbb ujj irányába eső játékos iszik!' },
  { emoji:'🔄', text:'Fordított kör — a vesztes kap pontot, a nyertes iszik!' },
  { emoji:'🤜', text:'Bumm kör — mindenki ökölbe szorítja a kezét, aki elfelejti, iszik!' },
  { emoji:'👅', text:'Csak szavak nélkül lehet kommunikálni ezen a körön!' },
  { emoji:'🎭', text:'Karakterkör — mindenki felvesz egy karaktert, aki kilép belőle, iszik!' },
  { emoji:'🥂', text:'Dupla kör — az összes ital és pont duplán számít!' },""",
"""// Wildcard mechanikai hatások: a "double/lucky/reverse" ténylegesen beavatkozik a
// pontozásba; a többi (effect nélküli) csak szöveges szabály.
const WC_EFFECTS = {
  double:  { badge:'DUPLA ×2',      color:'#E8604C' },
  lucky:   { badge:'SZERENCSE +1',  color:'#3DA888' },
  reverse: { badge:'FORDÍTOTT ⇄',   color:'#7C5CC4' },
};
const WILDCARDS_DEFAULT = [
  { emoji:'🤚', text:'Bal kézzel kell inni ezen a körön!' },
  { emoji:'🤫', text:'Csend kör — aki hangosan nevet, iszik egyet!' },
  { emoji:'👆', text:'Mindenki mutasson valakire — a legtöbb ujj irányába eső játékos iszik!' },
  { emoji:'🔄', text:'Fordított kör — a vesztes kap pontot, a nyertes iszik!', effect:'reverse' },
  { emoji:'🤜', text:'Bumm kör — mindenki ökölbe szorítja a kezét, aki elfelejti, iszik!' },
  { emoji:'👅', text:'Csak szavak nélkül lehet kommunikálni ezen a körön!' },
  { emoji:'🎭', text:'Karakterkör — mindenki felvesz egy karaktert, aki kilép belőle, iszik!' },
  { emoji:'🥂', text:'Dupla kör — az összes ital és pont duplán számít!', effect:'double' },""")
rep("  { emoji:'🍀', text:'Szerencsekör — véletlenszerű játékos kap egy extra pontot!' },",
    "  { emoji:'🍀', text:'Szerencsekör — véletlenszerű játékos kap egy extra pontot!', effect:'lucky' },")

# ── 2) Admin: load/save/reset megőrzi az effect-et ──
rep("      setList(src.map(w => ({ emoji: w.emoji || '', text: w.text || '' })));",
    "      setList(src.map(w => ({ emoji: w.emoji || '', text: w.text || '', effect: w.effect || null })));")
rep("    }).catch(() => setList(WILDCARDS_DEFAULT.map(w => ({ emoji: w.emoji, text: w.text }))));",
    "    }).catch(() => setList(WILDCARDS_DEFAULT.map(w => ({ emoji: w.emoji, text: w.text, effect: w.effect || null }))));")
rep("  const add = () => { setList(l => [...l, { emoji:'🃏', text:'' }]); setDirty(true); setSaved(false); };",
    "  const add = () => { setList(l => [...l, { emoji:'🃏', text:'', effect:null }]); setDirty(true); setSaved(false); };")
rep("    const clean = (list || []).map(w => ({ emoji: (w.emoji || '').trim() || '🃏', text: (w.text || '').trim() })).filter(w => w.text);",
    "    const clean = (list || []).map(w => ({ emoji: (w.emoji || '').trim() || '🃏', text: (w.text || '').trim(), ...(w.effect ? { effect: w.effect } : {}) })).filter(w => w.text);")
rep("  const reset = () => persist(WILDCARDS_DEFAULT.map(w => ({ emoji: w.emoji, text: w.text })));",
    "  const reset = () => persist(WILDCARDS_DEFAULT.map(w => ({ emoji: w.emoji, text: w.text, ...(w.effect ? { effect: w.effect } : {}) })));")

# ── 3) Admin: sorkártya effect-jelöléssel + hatás-választó ──
rep("""        {list.map((w, i) => (
          <div key={i} style={{ background:T.surface, borderRadius:14, padding:'10px 12px', boxShadow:T.shadow, display:'flex', gap:8, alignItems:'flex-start' }}>
            <input value={w.emoji} onChange={e => upd(i, 'emoji', e.target.value)} placeholder="🃏" style={{ width:52, boxSizing:'border-box', padding:'9px 4px', borderRadius:10, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:18, textAlign:'center', color:T.ink, outline:'none', flexShrink:0 }} />
            <textarea value={w.text} onChange={e => upd(i, 'text', e.target.value)} placeholder="Wildcard szöveg…" rows={2} style={{ flex:1, boxSizing:'border-box', padding:'9px 10px', borderRadius:10, border:`1.5px solid ${(w.text||'').trim() ? T.border : T.coral}`, background:T.bg, fontFamily:T.font, fontSize:13, color:T.ink, outline:'none', resize:'vertical', minWidth:0 }} />
            <button onClick={() => { if (confirmDel === i) del(i); else setConfirmDel(i); }} style={{ padding:'8px 10px', borderRadius:10, border:'none', background: confirmDel === i ? T.coral : T.coralSoft, color: confirmDel === i ? '#fff' : T.coral, fontFamily:T.font, fontWeight:700, fontSize:12, cursor:'pointer', flexShrink:0, alignSelf:'center', display:'flex', alignItems:'center' }}>{confirmDel === i ? 'Biztos?' : <BohIcon name="trash" size={14} />}</button>
          </div>
        ))}""",
"""        {list.map((w, i) => {
          const eff = w.effect && WC_EFFECTS[w.effect] ? WC_EFFECTS[w.effect] : null;
          return (
          <div key={i} style={{ background:T.surface, borderRadius:14, padding:'10px 12px', boxShadow:T.shadow, borderLeft: eff ? `4px solid ${eff.color}` : 'none', display:'flex', flexDirection:'column', gap:8 }}>
            <div style={{ display:'flex', gap:8, alignItems:'flex-start' }}>
              <input value={w.emoji} onChange={e => upd(i, 'emoji', e.target.value)} placeholder="🃏" style={{ width:52, boxSizing:'border-box', padding:'9px 4px', borderRadius:10, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:18, textAlign:'center', color:T.ink, outline:'none', flexShrink:0 }} />
              <textarea value={w.text} onChange={e => upd(i, 'text', e.target.value)} placeholder="Wildcard szöveg…" rows={2} style={{ flex:1, boxSizing:'border-box', padding:'9px 10px', borderRadius:10, border:`1.5px solid ${(w.text||'').trim() ? T.border : T.coral}`, background:T.bg, fontFamily:T.font, fontSize:13, color:T.ink, outline:'none', resize:'vertical', minWidth:0 }} />
              <button onClick={() => { if (confirmDel === i) del(i); else setConfirmDel(i); }} style={{ padding:'8px 10px', borderRadius:10, border:'none', background: confirmDel === i ? T.coral : T.coralSoft, color: confirmDel === i ? '#fff' : T.coral, fontFamily:T.font, fontWeight:700, fontSize:12, cursor:'pointer', flexShrink:0, alignSelf:'center', display:'flex', alignItems:'center' }}>{confirmDel === i ? 'Biztos?' : <BohIcon name="trash" size={14} />}</button>
            </div>
            <div style={{ display:'flex', gap:6, alignItems:'center', flexWrap:'wrap' }}>
              <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkMute, marginRight:2 }}>Játékbeli hatás:</span>
              {[['', 'Nincs (szöveges)'], ['double','×2 Dupla'], ['lucky','🍀 +1 pont'], ['reverse','🔄 Fordított']].map(([val, lbl]) => {
                const sel = (w.effect || '') === val;
                const c = val && WC_EFFECTS[val] ? WC_EFFECTS[val].color : T.mint;
                return <button key={val||'none'} onClick={() => upd(i, 'effect', val || null)} style={{ padding:'5px 10px', borderRadius:999, border: sel ? `1.5px solid ${c}` : `1.5px solid ${T.border}`, cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:11, background: sel ? (val ? `${c}1f` : T.surfaceMuted) : 'transparent', color: sel ? (val ? c : T.ink) : T.inkMute }}>{lbl}</button>;
              })}
            </div>
          </div>
          );
        })}""")
rep("""      <div style={{ fontFamily:T.font, fontSize:12.5, color:T.sub, marginBottom:12 }}>Ezek jelennek meg a wildcard körökben. Mentés után a többi készüléken az app következő indításakor töltődik be a friss lista.</div>""",
"""      <div style={{ fontFamily:T.font, fontSize:12.5, color:T.sub, marginBottom:12 }}>Ezek jelennek meg a wildcard körökben. A színes szegéllyel jelölt kártyák nem csak szövegesek — ténylegesen beavatkoznak a pontozásba. Mentés után a friss lista a többi készüléken az app következő indításakor töltődik be.</div>""")

# ── 4) PlayScreen: wcEffect / wcMult ──
rep("  const diffDrinks = gameMeta?.difficulty === 'extreme' ? 5 : gameMeta?.difficulty === 'hard' ? 3 : gameMeta?.difficulty === 'mid' ? 2 : 1;",
"""  const diffDrinks = gameMeta?.difficulty === 'extreme' ? 5 : gameMeta?.difficulty === 'hard' ? 3 : gameMeta?.difficulty === 'mid' ? 2 : 1;
  // Aktív wildcard mechanikai hatása (double = ×2 minden pont/korty; reverse = vesztes pontoz / nyertes iszik)
  const wcEffect = activeWildcard?.effect || null;
  const wcMult = wcEffect === 'double' ? 2 : 1;""")

# ── 5) onResult: dupla kijelzés + fordított csere + effect badge ──
rep("""  const onResult = (res) => {
    if (!res) { setGameResult(null); return; }
    const d = res.drinks ?? 0;
    const scaled = d > 0 ? d * diffDrinks : 0;
    const subtitle = (d === 1 && diffDrinks > 1) ? null : res.subtitle;
    const ts = Date.now();
    setGameResult({ ...res, drinks: scaled, subtitle, ts });""",
"""  const onResult = (res) => {
    if (!res) { setGameResult(null); return; }
    let r = res;
    // Fordított kör: nyertes ↔ vesztes csere a bannerben (a nyertes iszik, a vesztes pontoz)
    if (wcEffect === 'reverse' && ((res.winners||[]).length || (res.losers||[]).length)) {
      const swappedDrinks = (res.drinks ?? 0) || ((res.winners||[]).length ? 1 : 0);
      r = { ...res, winners: res.losers || [], losers: res.winners || [], drinks: swappedDrinks, winNote: '+1 pont', loseNote: '', subtitle: null, correct: undefined };
    }
    const d = r.drinks ?? 0;
    const scaled = d > 0 ? d * diffDrinks * wcMult : 0;
    const subtitle = (d === 1 && diffDrinks * wcMult > 1) ? null : r.subtitle;
    const ts = Date.now();
    setGameResult({ ...r, drinks: scaled, subtitle, ts, effect: wcEffect });""")

# ── 6) advance (Egyéni) ──
rep("""  const advance = success => {
    if (transitioning) return;
    const newPlayers = trackScores
      ? players.map(p => p.id===currentPlayer?.id ? {...p, [success?'points':'drinks']: p[success?'points':'drinks']+(success?1:diffDrinks)} : p)
      : players;
    setPendingCommit({ newPlayers, fb:success?'win':'lose', newTurn:(turn+1)%Math.max(activePlayers.length,1), newGameIdx:gameIdx+1, newRound:round+1 });
  };""",
"""  const advance = success => {
    if (transitioning) return;
    const won = wcEffect === 'reverse' ? !success : success;
    const newPlayers = trackScores
      ? players.map(p => p.id===currentPlayer?.id ? {...p, ...(won ? {points: p.points + 1*wcMult} : {drinks: p.drinks + diffDrinks*wcMult})} : p)
      : players;
    setPendingCommit({ newPlayers, fb:won?'win':'lose', newTurn:(turn+1)%Math.max(activePlayers.length,1), newGameIdx:gameIdx+1, newRound:round+1 });
  };""")

# ── 7) advanceTeam (Csapat) ──
rep("""  const advanceTeam = winnerIdx => {
    if (transitioning) return;
    const newPlayers = trackScores
      ? players.map((p,i) => i===winnerIdx ? {...p,points:p.points+1} : {...p,drinks:p.drinks+1})
      : players;
    commitRound(newPlayers, 'win', (turn+1)%Math.max(activePlayers.length,1), gameIdx+1, round+1);
  };""",
"""  const advanceTeam = winnerIdx => {
    if (transitioning) return;
    const rev = wcEffect === 'reverse';
    const newPlayers = trackScores
      ? players.map((p,i) => {
          const scores = rev ? i!==winnerIdx : i===winnerIdx;
          return scores ? {...p, points:p.points + 1*wcMult} : {...p, drinks:p.drinks + 1*wcMult};
        })
      : players;
    commitRound(newPlayers, 'win', (turn+1)%Math.max(activePlayers.length,1), gameIdx+1, round+1);
  };""")

# ── 8) advancePaired (Páros) ──
rep("""    const newPlayers = trackScores
      ? players.map(p => {
          if (p.id===currentPlayer?.id) return {...p, ...(currentPlayerWon ? {points:p.points+1} : {drinks:p.drinks+diffDrinks})};
          if (p.id===selectedOpponent.id) return {...p, ...(currentPlayerWon ? {drinks:p.drinks+diffDrinks} : {points:p.points+1})};
          return p;
        })
      : players;
    setSelectedOpponent(null);
    setPendingCommit({ newPlayers, fb:currentPlayerWon?'win':'lose', newTurn:(turn+1)%Math.max(activePlayers.length,1), newGameIdx:gameIdx+1, newRound:round+1 });""",
"""    const won = wcEffect === 'reverse' ? !currentPlayerWon : currentPlayerWon;
    const newPlayers = trackScores
      ? players.map(p => {
          if (p.id===currentPlayer?.id) return {...p, ...(won ? {points:p.points+1*wcMult} : {drinks:p.drinks+diffDrinks*wcMult})};
          if (p.id===selectedOpponent.id) return {...p, ...(won ? {drinks:p.drinks+diffDrinks*wcMult} : {points:p.points+1*wcMult})};
          return p;
        })
      : players;
    setSelectedOpponent(null);
    setPendingCommit({ newPlayers, fb:won?'win':'lose', newTurn:(turn+1)%Math.max(activePlayers.length,1), newGameIdx:gameIdx+1, newRound:round+1 });""")

# ── 9) advanceLoverseny (általános dm/pm út) ──
rep("""    const scale = (opts?.raw || currentGameId === 'loverseny') ? 1 : diffDrinks;
    const latestPlayers = playersRef.current;
    const newPlayers = trackScores
      ? latestPlayers.map(p => ({ ...p, drinks: p.drinks + (dm[p.id] || 0) * scale, points: p.points + (pm[p.id] || 0) }))
      : latestPlayers;""",
"""    const scale = (opts?.raw || currentGameId === 'loverseny') ? 1 : diffDrinks;
    const latestPlayers = playersRef.current;
    const newPlayers = trackScores
      ? (wcEffect === 'reverse'
          ? latestPlayers.map(p => {
              const wasDrink = (dm[p.id] || 0) > 0, wasPoint = (pm[p.id] || 0) > 0;
              return { ...p, points: p.points + (wasDrink ? 1 : 0), drinks: p.drinks + (wasPoint ? diffDrinks : 0) };
            })
          : latestPlayers.map(p => ({ ...p, drinks: p.drinks + (dm[p.id] || 0) * scale * wcMult, points: p.points + (pm[p.id] || 0) * wcMult })))
      : latestPlayers;""")

# ── 10) lucky: aktiváláskor véletlen +1 pont + banner bejelentés ──
rep("""        if (isWildcardRound && wc) {
          setActiveWildcard({ ...wc, round: newRound });
          if (typeof window.bohSound === 'function') window.bohSound('wildcard');
          if (typeof window.bohHaptic === 'function') window.bohHaptic('success');
        }""",
"""        if (isWildcardRound && wc) {
          setActiveWildcard({ ...wc, round: newRound });
          if (typeof window.bohSound === 'function') window.bohSound('wildcard');
          if (typeof window.bohHaptic === 'function') window.bohHaptic('success');
          // Szerencsekör: véletlen aktív játékos kap +1 pontot, és a banner kiírja, ki
          if (wc.effect === 'lucky') {
            const activePl = newPlayers.filter(p => p.active !== false);
            if (activePl.length) {
              const lucky = activePl[Math.floor(Math.random() * activePl.length)];
              setPlayers(prev => prev.map(p => p.id === lucky.id ? { ...p, points: (p.points||0) + 1 } : p));
              setTimeout(() => setGameResult({ winners:[lucky], winNote:'+1 pont', subtitle:`${lucky.name} — Szerencsekör!`, drinks:0, effect:'lucky', ts:Date.now() }), 500);
            }
          }
        }""")

# ── 11) Result banner: effect badge felül ──
rep("""              <button onClick={e => { e.stopPropagation(); setResultMinimized(true); }} aria-label="Kicsinyítés" style={{ position:'absolute', top:10, right:10, width:30, height:30, borderRadius:'50%', border:'none', background:'rgba(255,255,255,0.22)', color:'#fff', fontSize:16, lineHeight:1, cursor:'pointer', display:'grid', placeItems:'center', zIndex:5 }}>✕</button>""",
"""              <button onClick={e => { e.stopPropagation(); setResultMinimized(true); }} aria-label="Kicsinyítés" style={{ position:'absolute', top:10, right:10, width:30, height:30, borderRadius:'50%', border:'none', background:'rgba(255,255,255,0.22)', color:'#fff', fontSize:16, lineHeight:1, cursor:'pointer', display:'grid', placeItems:'center', zIndex:5 }}>✕</button>
              {gameResult.effect && WC_EFFECTS[gameResult.effect] && (
                <div style={{ position:'absolute', top:13, left:'50%', transform:'translateX(-50%)', zIndex:5, background:'rgba(0,0,0,0.34)', color:'#fff', borderRadius:999, padding:'4px 12px', fontFamily:T.font, fontWeight:900, fontSize:10.5, letterSpacing:'0.08em', whiteSpace:'nowrap', pointerEvents:'none' }}>{WC_EFFECTS[gameResult.effect].badge}</div>
              )}""")

# ── 12) Verziobump ──
rep("const APP_VERSION = 'v9.974';", "const APP_VERSION = 'v9.975';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — wildcard effects applied')
