#!/usr/bin/env python3
# v10.242 — 2. rész: a HOST felülete (biztosítás-lap, kezenkénti asztal, Split gomb)
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── A: PlayingView feje — a soros KÉZ, nem a soros játékos ──
sub("""    const curPid = bjState.phase === 'playing' ? bjState.currentTurn : null;
    const curP = curPid ? getPlayer(curPid) : null;
    const curHand = curPid ? (bjState.hands[curPid] || []) : [];
    const canDouble = curPid && curHand.length === 2 && !bjState.doubled[curPid];""",
"""    // A soros egyseg mostantol a KEZ (kulcs), nem a jatekos.
    const curKey = bjState.phase === 'playing' ? bjState.currentTurn : null;
    const curPid = curKey ? bjPidOfHand(curKey) : null;
    const curP = curPid ? getPlayer(curPid) : null;
    const curHand = curKey ? (bjState.hands[curKey] || []) : [];
    const curChips = curPid ? bjChipsOf(bjState, curPid, stackOf(curPid)) : 0;
    const curHandCount = curPid ? bjHandsOf(bjState, curPid).length : 1;
    const curHandNo = curKey ? bjHandsOf(bjState, curPid).indexOf(curKey) + 1 : 0;
    const canDouble = !!curKey && bjCanDouble(bjState, curKey, curChips);
    const canSplit = !!curKey && bjCanSplit(bjState, curKey, curChips);""",
    'PlayingView fej')

# ── B: az asztal kezenként rajzol ──
sub("""            {(bjState.participants || []).map(pid => {
              const p = getPlayer(pid);
              const hand = bjState.hands[pid] || [];
              const score = bjScore(hand);
              const isTurn = bjState.currentTurn === pid && bjState.phase === 'playing';
              const isStood = bjState.stood[pid];
              const isBust = bjState.bust[pid];
              const isBJ = bjIsBlackjack(hand);
              const rowChips = (bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : stackOf(pid);""",
"""            {(bjState.participants || []).map(pid => bjHandsOf(bjState, pid).map((hk, hi, hArr) => {
              const p = getPlayer(pid);
              const hand = bjState.hands[hk] || [];
              const score = bjScore(hand);
              const isTurn = bjState.currentTurn === hk && bjState.phase === 'playing';
              const isStood = bjState.stood[hk];
              const isBust = bjState.bust[hk];
              const isBJ = bjIsHandBJ(bjState, hk);
              const rowChips = (bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : stackOf(pid);
              const handLabel = hArr.length > 1 ? ` ${hi + 1}/${hArr.length}` : '';""",
    'asztal kezenkent — fej')

sub("""                <div key={pid} style={{ flex:'0 0 calc(33.33% - 8px)', minWidth:0, boxSizing:'border-box', display:'flex', flexDirection:'column', alignItems:'center', gap:4, background:'rgba(255,255,255,0.08)', border:`1.5px solid ${isTurn ? '#F4D46B' : 'rgba(255,255,255,0.18)'}`, borderRadius:14, padding:'6px 4px', boxShadow: isTurn ? '0 0 0 2px #F4D46B66' : 'none' }}>
                  <BJAvatar p={p} size={28} />
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff', maxWidth:'100%', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p?.name || pid}</span>
                  <div style={{ display:'flex', gap:3, flexWrap:'wrap', justifyContent:'center', minHeight:52 }}>
                    {hand.map((c, i) => <BJCardEl key={i} card={c} small />)}
                  </div>
                  <div style={{ display:'flex', alignItems:'flex-start', gap:8 }}>
                    <div style={{ display:'flex', flexDirection:'column', alignItems:'center' }}>
                      <span style={{ width:20, height:20, borderRadius:'50%', background:T.coral, border:'1.5px dashed rgba(255,255,255,0.9)', display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:10, color:'#fff', boxSizing:'border-box' }}>{bjState.bets[pid] || 1}</span>
                      <span style={lblS}>TÉT</span>
                    </div>""",
"""                <div key={hk} style={{ flex:'0 0 calc(33.33% - 8px)', minWidth:0, boxSizing:'border-box', display:'flex', flexDirection:'column', alignItems:'center', gap:4, background:'rgba(255,255,255,0.08)', border:`1.5px solid ${isTurn ? '#F4D46B' : 'rgba(255,255,255,0.18)'}`, borderRadius:14, padding:'6px 4px', boxShadow: isTurn ? '0 0 0 2px #F4D46B66' : 'none' }}>
                  <BJAvatar p={p} size={28} />
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff', maxWidth:'100%', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p?.name || pid}{handLabel}</span>
                  <div style={{ display:'flex', gap:3, flexWrap:'wrap', justifyContent:'center', minHeight:52 }}>
                    {hand.map((c, i) => <BJCardEl key={i} card={c} small />)}
                  </div>
                  <div style={{ display:'flex', alignItems:'flex-start', gap:8 }}>
                    <div style={{ display:'flex', flexDirection:'column', alignItems:'center' }}>
                      <span style={{ width:20, height:20, borderRadius:'50%', background:T.coral, border:'1.5px dashed rgba(255,255,255,0.9)', display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:10, color:'#fff', boxSizing:'border-box' }}>{bjState.bets[hk] || 1}</span>
                      <span style={lblS}>TÉT</span>
                    </div>""",
    'asztal kezenkent — kartya')

sub("""                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:9, color:status.c, letterSpacing:'0.04em' }}>{status.t}</span>
                </div>
              );
            })}
          </div>
        </div>
        {bjState.phase === 'playing' && curPid && (""",
"""                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:9, color:status.c, letterSpacing:'0.04em' }}>{status.t}</span>
                  {((bjState.insurance || {})[pid] || 0) > 0 && hi === 0 && (
                    <span style={{ fontFamily:T.font, fontWeight:900, fontSize:8, color:'#9FD8FF', letterSpacing:'0.04em' }}>🛡 {bjState.insurance[pid]}</span>
                  )}
                </div>
              );
            }))}
          </div>
        </div>
        {bjState.phase === 'playing' && curKey && (""",
    'asztal kezenkent — zaras')

# ── C: a gombsor a soros KÉZRE hat, és megjelenik a Split ──
sub("""            <div style={{ fontFamily:T.font, fontSize:12, fontWeight:T.weightTitle, color:T.inkSoft, textAlign:'center', marginBottom:8 }}>{curP?.name || '?'} jön</div>
            <div style={{ display:'flex', gap:8 }}>
              <button onClick={() => update(bjDoHit(bjState, curPid))} style={{ flex:1, padding:'10px', borderRadius:12, background:T.mint, border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>Hit 🃏</button>
              <button onClick={() => update(bjDoStand(bjState, curPid))} style={{ flex:1, padding:'10px', borderRadius:12, background:'#555', border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>Stand ✋</button>
              {canDouble && <button onClick={() => update(bjDoDouble(bjState, curPid))} style={{ flex:1, padding:'10px', borderRadius:12, background:'#c07a10', border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>Double 2×</button>}
            </div>""",
"""            <div style={{ fontFamily:T.font, fontSize:12, fontWeight:T.weightTitle, color:T.inkSoft, textAlign:'center', marginBottom:8 }}>
              {curP?.name || '?'} jön{curHandCount > 1 ? ` — ${curHandNo}. keze` : ''}
            </div>
            <div style={{ display:'flex', gap:8 }}>
              <button onClick={() => update(bjDoHit(bjState, curKey))} style={{ flex:1, padding:'10px', borderRadius:12, background:T.mint, border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>Hit 🃏</button>
              <button onClick={() => update(bjDoStand(bjState, curKey))} style={{ flex:1, padding:'10px', borderRadius:12, background:'#555', border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>Stand ✋</button>
              {canDouble && <button onClick={() => update(bjDoDouble(bjState, curKey))} style={{ flex:1, padding:'10px', borderRadius:12, background:'#c07a10', border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>Double 2×</button>}
              {canSplit && <button onClick={() => update(bjDoSplit(bjState, curKey))} style={{ flex:1, padding:'10px', borderRadius:12, background:'#3b6fb5', border:'none', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', cursor:'pointer' }}>Split ✂️</button>}
            </div>""",
    'gombsor + split')

# ── D: az eredmény-asztal is kezenként ──
sub("""            {(bjState.participants || []).map(pid => {
              const p = getPlayer(pid);
              const hand = bjState.hands[pid] || [];
              const res = bjResultFor(bjState, pid);
              const rowChips = (bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : stackOf(pid);
              const out = !!(bjState.cashedOut || {})[pid];
              const status = res.delta > 0 ? { t:`+${res.delta} 🍺`, c:'#7CF0BF' } : res.delta < 0 ? { t:`−${-res.delta} 🍺`, c:'#FF9C86' } : { t:'=', c:'#F4D46B' };""",
"""            {(bjState.participants || []).map(pid => bjHandsOf(bjState, pid).map((hk, hi, hArr) => {
              const p = getPlayer(pid);
              const hand = bjState.hands[hk] || [];
              const res = bjResultFor(bjState, hk);
              const rowChips = (bjState.chips || {})[pid] !== undefined ? bjState.chips[pid] : stackOf(pid);
              const out = !!(bjState.cashedOut || {})[pid];
              const handLabel = hArr.length > 1 ? ` ${hi + 1}/${hArr.length}` : '';
              const insR = hi === 0 ? bjInsuranceResult(bjState, pid) : { ins:0, delta:0 };
              const status = res.delta > 0 ? { t:`+${res.delta} 🍺`, c:'#7CF0BF' } : res.delta < 0 ? { t:`−${-res.delta} 🍺`, c:'#FF9C86' } : { t:'=', c:'#F4D46B' };""",
    'eredmeny-asztal fej')

sub("""                <div key={pid} style={{ flex:'0 0 calc(33.33% - 8px)', minWidth:0, boxSizing:'border-box', display:'flex', flexDirection:'column', alignItems:'center', gap:4, background:'rgba(255,255,255,0.08)', border:'1.5px solid rgba(255,255,255,0.18)', borderRadius:14, padding:'6px 4px', opacity: out ? 0.6 : 1 }}>
                  <BJAvatar p={p} size={28} />
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff', maxWidth:'100%', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p?.name || pid}{out ? ' 🚪' : ''}</span>""",
"""                <div key={hk} style={{ flex:'0 0 calc(33.33% - 8px)', minWidth:0, boxSizing:'border-box', display:'flex', flexDirection:'column', alignItems:'center', gap:4, background:'rgba(255,255,255,0.08)', border:'1.5px solid rgba(255,255,255,0.18)', borderRadius:14, padding:'6px 4px', opacity: out ? 0.6 : 1 }}>
                  <BJAvatar p={p} size={28} />
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff', maxWidth:'100%', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p?.name || pid}{handLabel}{out ? ' 🚪' : ''}</span>""",
    'eredmeny-asztal kartya')

sub("""                      <span style={{ width:20, height:20, borderRadius:'50%', background:T.coral, border:'1.5px dashed rgba(255,255,255,0.9)', display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:10, color:'#fff', boxSizing:'border-box' }}>{bjState.bets[pid] || 1}</span>
                      <span style={lblS}>TÉT</span>""",
"""                      <span style={{ width:20, height:20, borderRadius:'50%', background:T.coral, border:'1.5px dashed rgba(255,255,255,0.9)', display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:10, color:'#fff', boxSizing:'border-box' }}>{bjState.bets[hk] || 1}</span>
                      <span style={lblS}>TÉT</span>""",
    'eredmeny-asztal tet')

sub("""                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:9, color:status.c, letterSpacing:'0.04em' }}>{status.t}</span>
                </div>
              );
            })}
          </div>
        </div>
        <button onClick={hostNewRound}""",
"""                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:9, color:status.c, letterSpacing:'0.04em' }}>{status.t}</span>
                  {insR.ins > 0 && (
                    <span style={{ fontFamily:T.font, fontWeight:900, fontSize:8, color: insR.delta > 0 ? '#7CF0BF' : '#FF9C86', letterSpacing:'0.04em' }}>
                      🛡 {insR.delta > 0 ? '+' : ''}{insR.delta}
                    </span>
                  )}
                </div>
              );
            }))}
          </div>
        </div>
        <button onClick={hostNewRound}""",
    'eredmeny-asztal zaras')

# ── E: biztosítás-nézet + fázis-útvonal ──
sub("""      {bjState.phase === 'betting' && <BettingView />}
      {(bjState.phase === 'playing' || bjState.phase === 'dealer') && <PlayingView />}""",
"""      {bjState.phase === 'betting' && <BettingView />}
      {bjState.phase === 'insurance' && <InsuranceView />}
      {(bjState.phase === 'playing' || bjState.phase === 'dealer') && <PlayingView />}""",
    'fazis utvonal')

sub("""  // ── Játék fázis (zöld filc asztal) ──
  const PlayingView = () => {""",
"""  // ── Biztosítás (csak ha az osztó Ászt mutat) ──
  // Mindenki EGYSZERRE dönt: a telefonján maga, a hoston a host is leütheti
  // helyette. Amikor mindenki döntött, a "Tovább" viszi a kört.
  const InsuranceView = () => {
    const parts = bjState.participants || [];
    const allDone = parts.length > 0 && parts.every(pid => (bjState.insDone || {})[pid]);
    const decide = (pid, take) => {
      const amt = take ? bjInsuranceAmount(bjState, pid) : 0;
      update({ ...bjState,
        insurance: { ...(bjState.insurance || {}), [pid]: amt },
        insDone: { ...(bjState.insDone || {}), [pid]: true } });
    };
    return (
      <div style={{ padding:'0 6px 12px' }}>
        <div style={{ background:'radial-gradient(ellipse at 50% 0%, rgba(255,255,255,0.10), rgba(255,255,255,0) 60%), #1E6E44', border:'4px solid #175636', borderRadius:'150px 150px 22px 22px', padding:'12px 8px 10px', boxShadow:'inset 0 2px 12px rgba(0,0,0,0.25)', marginBottom:12 }}>
          <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:6 }}>
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', letterSpacing:'0.12em', textTransform:'uppercase', display:'inline-flex', alignItems:'center', gap:5 }}><BohIcon name="tophat" size={13} />OSZTÓ — ÁSZ</span>
            <div style={{ display:'flex', gap:6 }}>
              {(bjState.dealerHand || []).map((c, i) => <BJCardEl key={i} card={c} faceDown={i === 1} />)}
            </div>
            <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.85)', textAlign:'center', lineHeight:1.5, maxWidth:320, marginTop:4 }}>
              Kértek biztosítást? Ha az osztónak Blackjackje van, a biztosítás 2:1-et fizet — ha nincs, elúszik.
            </div>
          </div>
        </div>
        {parts.map(pid => {
          const p = getPlayer(pid);
          const amt = bjInsuranceAmount(bjState, pid);
          const done = !!(bjState.insDone || {})[pid];
          const took = ((bjState.insurance || {})[pid] || 0) > 0;
          return (
            <div key={pid} style={{ display:'flex', alignItems:'center', gap:10, background:T.surface, borderRadius:14, padding:'9px 12px', marginBottom:8, boxShadow:T.shadowPill || T.shadow }}>
              <BJAvatar p={p} size={28} />
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p?.name || pid}</div>
                <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:1 }}>
                  {amt > 0 ? `Biztosítás: ${amt} zseton` : 'Nincs rá elég zsetonja'}
                </div>
              </div>
              {done ? (
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color: took ? T.mintDeep : T.inkMute, flexShrink:0 }}>{took ? `🛡 ${bjState.insurance[pid]}` : 'Nem kér'}</span>
              ) : (
                <div style={{ display:'flex', gap:6, flexShrink:0 }}>
                  <button disabled={amt <= 0} onClick={() => decide(pid, true)} style={{ padding:'8px 12px', borderRadius:11, border:'none', background: amt > 0 ? '#3b6fb5' : T.inkMute+'33', color: amt > 0 ? '#fff' : T.inkMute, fontFamily:T.font, fontWeight:900, fontSize:12, cursor: amt > 0 ? 'pointer' : 'default' }}>🛡 Kérek</button>
                  <button onClick={() => decide(pid, false)} style={{ padding:'8px 12px', borderRadius:11, border:'none', background:'#555', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:12, cursor:'pointer' }}>Nem</button>
                </div>
              )}
            </div>
          );
        })}
        <button onClick={() => update(bjAfterInsurance(bjState))} style={{ width:'100%', padding:'14px', borderRadius:16, background: allDone ? '#1a6b3c' : T.inkMute+'33', border:'none', fontFamily:T.font, fontWeight:900, fontSize:15, color: allDone ? '#fff' : T.inkSoft, cursor:'pointer', marginTop:4 }}>
          {allDone ? 'Mehet tovább 🂡' : 'Tovább (aki nem döntött, nem kér)'}
        </button>
        {isOnline && <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:8, textAlign:'center' }}>📱 A telefonján is dönthet mindenki</div>}
      </div>
    );
  };

  // ── Játék fázis (zöld filc asztal) ──
  const PlayingView = () => {""",
    'InsuranceView')

open(P, 'w', encoding='utf-8').write(src)
print('OK — 2. resz: host felulet')
