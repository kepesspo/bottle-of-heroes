#!/usr/bin/env python3
# v10.242 — 3. rész: a TELEFONOS nézet (biztosítás, több kéz, Split) + beállítások
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── A: a telefon is kéz-alapon számol ──
sub("""  const me = players.find(p => p.id === playerId);
  const inRound = (bj.participants || []).includes(playerId);
  const myHand = (bj.hands || {})[playerId] || [];
  const myScore = bjScore(myHand);
  const myBet = (bj.bets || {})[playerId] || 1;
  const isMyTurn = bj.phase === 'playing' && bj.currentTurn === playerId;""",
"""  const me = players.find(p => p.id === playerId);
  const inRound = (bj.participants || []).includes(playerId);
  // Split ota tobb kezem is lehet — a soros egyseg a KEZ kulcsa.
  const myKeys = bjHandsOf(bj, playerId);
  const myHand = (bj.hands || {})[playerId] || [];
  const myScore = bjScore(myHand);
  const myBet = (bj.bets || {})[playerId] || 1;
  const myTurnKey = (bj.phase === 'playing' && bj.currentTurn && bjPidOfHand(bj.currentTurn) === playerId) ? bj.currentTurn : null;
  const isMyTurn = !!myTurnKey;""",
    'telefon kez-alap')

# ── B: a saját kéz kártya → több kéz + Split ──
sub("""            {/* Saját kéz */}
            <div style={{ background:T.surface, borderRadius:18, padding:'14px 16px', boxShadow:T.shadow, border: isMyTurn ? `2px solid ${T.mint}` : '2px solid transparent', marginBottom:12 }}>
              <div style={{ display:'flex', alignItems:'center', marginBottom:8 }}>
                <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em' }}>A lapjaid</span>
                {isMyTurn && <span style={{ marginLeft:8, fontFamily:T.font, fontWeight:900, fontSize:10, color:'#fff', background:T.mint, borderRadius:999, padding:'3px 8px', letterSpacing:'0.06em' }}>TE JÖSSZ!</span>}
                <span style={{ marginLeft:'auto', fontFamily:T.font, fontWeight:900, fontSize:20, color: bj.bust[playerId] ? T.coral : bjIsBlackjack(myHand) ? T.mint : T.ink }}>
                  {bj.bust[playerId] ? `${myScore} 💀` : bjIsBlackjack(myHand) ? '21 🂡' : myScore}
                </span>
              </div>
              <div style={{ display:'flex', gap:6, flexWrap:'wrap' }}>
                {myHand.map((c, i) => <BJCardEl key={i} card={c} big />)}
              </div>
              {isMyTurn && (
                <div style={{ display:'flex', gap:8, marginTop:14 }}>
                  <button onClick={() => bjWrite(code, bjDoHit(bj, playerId))} style={{ flex:1, padding:'14px 6px', borderRadius:14, background:T.mint, border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer' }}>Hit 🃏</button>
                  <button onClick={() => bjWrite(code, bjDoStand(bj, playerId))} style={{ flex:1, padding:'14px 6px', borderRadius:14, background:'#555', border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer' }}>Stand ✋</button>
                  {myHand.length === 2 && !bj.doubled[playerId] && (
                    <button onClick={() => bjWrite(code, bjDoDouble(bj, playerId))} style={{ flex:1, padding:'14px 6px', borderRadius:14, background:'#c07a10', border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer' }}>2×</button>
                  )}
                </div>
              )}
              {bj.phase === 'playing' && !isMyTurn && !bj.stood[playerId] && !bj.bust[playerId] && (
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:8, textAlign:'center' }}>Várj a körödre… ({players.find(p => p.id === bj.currentTurn)?.name || '?'} jön)</div>
              )}""",
"""            {/* Saját kéz (split után több is) */}
            <div style={{ background:T.surface, borderRadius:18, padding:'14px 16px', boxShadow:T.shadow, border: isMyTurn ? `2px solid ${T.mint}` : '2px solid transparent', marginBottom:12 }}>
              <div style={{ display:'flex', alignItems:'center', marginBottom:8 }}>
                <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em' }}>{myKeys.length > 1 ? 'A kezeid' : 'A lapjaid'}</span>
                {isMyTurn && <span style={{ marginLeft:8, fontFamily:T.font, fontWeight:900, fontSize:10, color:'#fff', background:T.mint, borderRadius:999, padding:'3px 8px', letterSpacing:'0.06em' }}>TE JÖSSZ!</span>}
              </div>
              {myKeys.map((hk, hi) => {
                const hand = (bj.hands || {})[hk] || [];
                const sc = bjScore(hand);
                const active = myTurnKey === hk;
                const isBJ = bjIsHandBJ(bj, hk);
                return (
                  <div key={hk} style={{ marginBottom: hi < myKeys.length - 1 ? 10 : 0,
                    padding: myKeys.length > 1 ? '9px 10px' : 0,
                    borderRadius:14, background: myKeys.length > 1 ? (active ? `${T.mint}14` : T.surfaceMuted) : 'transparent',
                    border: myKeys.length > 1 ? `1.5px solid ${active ? T.mint : 'transparent'}` : 'none' }}>
                    <div style={{ display:'flex', alignItems:'center', marginBottom:6 }}>
                      {myKeys.length > 1 && (
                        <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:T.inkSoft, letterSpacing:'0.06em' }}>
                          {hi + 1}. KÉZ · TÉT {(bj.bets || {})[hk] || 1}
                        </span>
                      )}
                      <span style={{ marginLeft:'auto', fontFamily:T.font, fontWeight:900, fontSize: myKeys.length > 1 ? 17 : 20,
                        color: bj.bust[hk] ? T.coral : isBJ ? T.mint : T.ink }}>
                        {bj.bust[hk] ? `${sc} 💀` : isBJ ? '21 🂡' : sc}{bj.stood[hk] && !bj.bust[hk] && !active ? ' ✋' : ''}
                      </span>
                    </div>
                    <div style={{ display:'flex', gap:6, flexWrap:'wrap' }}>
                      {hand.map((c, i) => <BJCardEl key={i} card={c} big={myKeys.length === 1} />)}
                    </div>
                  </div>
                );
              })}
              {isMyTurn && (() => {
                const hand = (bj.hands || {})[myTurnKey] || [];
                const canD = bjCanDouble(bj, myTurnKey, myChips);
                const canS = bjCanSplit(bj, myTurnKey, myChips);
                return (
                  <div style={{ display:'flex', gap:8, marginTop:14 }}>
                    <button onClick={() => bjWrite(code, bjDoHit(bj, myTurnKey))} style={{ flex:1, padding:'14px 6px', borderRadius:14, background:T.mint, border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer' }}>Hit 🃏</button>
                    <button onClick={() => bjWrite(code, bjDoStand(bj, myTurnKey))} style={{ flex:1, padding:'14px 6px', borderRadius:14, background:'#555', border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer' }}>Stand ✋</button>
                    {canD && (
                      <button onClick={() => bjWrite(code, bjDoDouble(bj, myTurnKey))} style={{ flex:1, padding:'14px 6px', borderRadius:14, background:'#c07a10', border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer' }}>2×</button>
                    )}
                    {canS && (
                      <button onClick={() => bjWrite(code, bjDoSplit(bj, myTurnKey))} style={{ flex:1, padding:'14px 6px', borderRadius:14, background:'#3b6fb5', border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', cursor:'pointer' }}>✂️</button>
                    )}
                  </div>
                );
              })()}
              {bj.phase === 'playing' && !isMyTurn && myKeys.some(k => !bj.stood[k] && !bj.bust[k]) && (
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:8, textAlign:'center' }}>Várj a körödre… ({players.find(p => p.id === bjPidOfHand(bj.currentTurn || ''))?.name || '?'} jön)</div>
              )}""",
    'telefon sajat kez')

# ── C: a telefonos eredmény-doboz a teljes kör-egyenleget mutassa ──
sub("""              {bj.phase === 'results' && (() => {
                const res = bjResultFor(bj, playerId);""",
"""              {bj.phase === 'results' && (() => {
                // Tobb kez + biztositas: a cimke felsorol, a delta az egesz kore
                const insR = bjInsuranceResult(bj, playerId);
                const labels = myKeys.map((k, i) => (myKeys.length > 1 ? `${i + 1}. ` : '') + bjResultFor(bj, k).label);
                if (insR.ins > 0) labels.push(`🛡 biztosítás ${insR.delta > 0 ? '+' : ''}${insR.delta}`);
                const res = { label: labels.join(' · '), delta: bjPlayerDelta(bj, playerId) };""",
    'telefon eredmeny')

# ── D: a többiek mini-táblája split-tel is jó legyen ──
sub("""                  const p = players.find(pp => pp.id === pid);
                  const hand = (bj.hands || {})[pid] || [];
                  const score = bjScore(hand);
                  const isTurn = bj.phase === 'playing' && bj.currentTurn === pid;
                  const status = bj.phase === 'results'
                    ? { t:`Lapok: ${bj.bust[pid] ? '💀' : bjIsBlackjack(hand) ? 'BJ 🂡' : score} · Zseton: ${(bj.chips || {})[pid] !== undefined ? bj.chips[pid] : stackOf(pid)} 🍺`, c:'#fff' }
                    : bj.bust[pid] ? { t:'💀', c:'#FF9C86' }
                    : bjIsBlackjack(hand) ? { t:'BJ! 🂡', c:'#7CF0BF' }
                    : bj.stood[pid] ? { t:`${score} ✋`, c:'#F4D46B' }
                    : { t:`${hand.length} LAP`, c:'#F4D46B' };""",
"""                  const p = players.find(pp => pp.id === pid);
                  const keys = bjHandsOf(bj, pid);
                  const hand = (bj.hands || {})[pid] || [];
                  const score = bjScore(hand);
                  const isTurn = bj.phase === 'playing' && bj.currentTurn && bjPidOfHand(bj.currentTurn) === pid;
                  // Split utan tobb kez — kezenkent egy rovid jelzes
                  const per = keys.map(k => {
                    const h = (bj.hands || {})[k] || [], s = bjScore(h);
                    if (bj.bust[k]) return '💀';
                    if (bjIsHandBJ(bj, k)) return 'BJ';
                    return bj.stood[k] ? `${s}✋` : String(s);
                  }).join(' / ');
                  const status = bj.phase === 'results'
                    ? { t:`Lapok: ${per} · Zseton: ${(bj.chips || {})[pid] !== undefined ? bj.chips[pid] : stackOf(pid)} 🍺`, c:'#fff' }
                    : keys.length > 1 ? { t: per, c:'#F4D46B' }
                    : bj.bust[pid] ? { t:'💀', c:'#FF9C86' }
                    : bjIsHandBJ(bj, pid) ? { t:'BJ! 🂡', c:'#7CF0BF' }
                    : bj.stood[pid] ? { t:`${score} ✋`, c:'#F4D46B' }
                    : { t:`${hand.length} LAP`, c:'#F4D46B' };""",
    'telefon mini-asztal')

# ── E: a telefonos biztosítás-lap ──
sub("""        {(bj.phase === 'playing' || bj.phase === 'dealer' || bj.phase === 'results') && inRound && (""",
"""        {bj.phase === 'insurance' && inRound && (() => {
          const amt = bjInsuranceAmount(bj, playerId);
          const done = !!(bj.insDone || {})[playerId];
          const took = ((bj.insurance || {})[playerId] || 0) > 0;
          const decide = (take) => bjWrite(code, { ...bj,
            insurance: { ...(bj.insurance || {}), [playerId]: take ? amt : 0 },
            insDone: { ...(bj.insDone || {}), [playerId]: true } });
          return (
            <div style={{ padding:'0 16px 16px' }}>
              <div style={{ background:T.surface, borderRadius:18, padding:'16px', boxShadow:T.shadow, textAlign:'center' }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink }}>Az osztó Ászt mutat 🂡</div>
                <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:6, lineHeight:1.5 }}>
                  Kérsz biztosítást? Ha az osztónak Blackjackje van, 2:1-et fizet — ha nincs, elúszik.
                </div>
                <div style={{ display:'flex', gap:5, justifyContent:'center', marginTop:12 }}>
                  {(bj.dealerHand || []).map((c, i) => <BJCardEl key={i} card={c} faceDown={i === 1} />)}
                </div>
                {done ? (
                  <div style={{ marginTop:16, fontFamily:T.font, fontWeight:900, fontSize:15, color: took ? T.mintDeep : T.inkSoft }}>
                    {took ? `🛡 Biztosítottál — ${bj.insurance[playerId]} zseton` : 'Nem kértél biztosítást'}
                    <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, marginTop:6 }}>Várj a többiekre…</div>
                  </div>
                ) : (
                  <div style={{ display:'flex', gap:10, marginTop:16 }}>
                    <button disabled={amt <= 0} onClick={() => decide(true)} style={{ flex:1, padding:'14px 6px', borderRadius:14, border:'none', background: amt > 0 ? '#3b6fb5' : T.inkMute+'33', color: amt > 0 ? '#fff' : T.inkMute, fontFamily:T.font, fontWeight:900, fontSize:15, cursor: amt > 0 ? 'pointer' : 'default' }}>
                      {amt > 0 ? `🛡 Kérek (${amt})` : 'Nincs elég zseton'}
                    </button>
                    <button onClick={() => decide(false)} style={{ flex:1, padding:'14px 6px', borderRadius:14, border:'none', background:'#555', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>Nem kérek</button>
                  </div>
                )}
              </div>
            </div>
          );
        })()}
        {(bj.phase === 'playing' || bj.phase === 'dealer' || bj.phase === 'results') && inRound && (""",
    'telefon biztositas')

# ── F: beállító lap — két kapcsoló ──
sub("""      <div style={{ padding:'0 18px 8px', display:'flex', flexDirection:'column' }}>
        <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, padding:'13px 0', lineHeight:1.5 }}>🎮 A host a játék elején dönti el, hogy játszik-e — a "Ki a host?" képernyőn.</div>
      </div>""",
"""      <div style={{ padding:'0 18px 8px', display:'flex', flexDirection:'column' }}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'13px 0' }}>
          <div style={{ paddingRight:12 }}>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>Biztosítás</div>
            <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:2, lineHeight:1.45 }}>Ha az osztó Ászt mutat, a tét feléig lehet fogadni arra, hogy Blackjackje van. 2:1-et fizet.</div>
          </div>
          <Toggle on={config.insurance !== false} onToggle={() => setConfig(c => ({ ...c, insurance: c.insurance === false }))} />
        </div>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'13px 0' }}>
          <div style={{ paddingRight:12 }}>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>Lapok szétválasztása</div>
            <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:2, lineHeight:1.45 }}>Azonos értékű első két lapból két kéz, újabb ugyanakkora téttel. Legfeljebb 4 kézig. Ász-párnál kezenként egy lap.</div>
          </div>
          <Toggle on={config.split !== false} onToggle={() => setConfig(c => ({ ...c, split: c.split === false }))} />
        </div>
        <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, padding:'13px 0', lineHeight:1.5 }}>🎮 A host a játék elején dönti el, hogy játszik-e — a "Ki a host?" képernyőn.</div>
      </div>""",
    'beallito lap')

open(P, 'w', encoding='utf-8').write(src)
print('OK — 3. resz: telefon + beallitasok')
