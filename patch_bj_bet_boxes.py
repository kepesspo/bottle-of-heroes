# v9.806: BJ bet selection as tappable boxes
import io

P = '/home/user/bottle-of-heroes/index.html'
c = io.open(P, encoding='utf-8').read()

OLD = """            <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:18, marginBottom:18 }}>
              <button onClick={() => !bj.betsDone[playerId] && setMyBet(myBet - 1)} disabled={!!bj.betsDone[playerId]} style={{ width:52, height:52, borderRadius:14, border:'none', background:T.surfaceMuted, fontFamily:T.font, fontWeight:900, fontSize:26, cursor:'pointer', color:T.ink, opacity: bj.betsDone[playerId] ? 0.4 : 1 }}>−</button>
              <div>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:44, color:T.ink, lineHeight:1 }}>{myBet}</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>korty</div>
              </div>
              <button onClick={() => !bj.betsDone[playerId] && setMyBet(myBet + 1)} disabled={!!bj.betsDone[playerId]} style={{ width:52, height:52, borderRadius:14, border:'none', background:T.surfaceMuted, fontFamily:T.font, fontWeight:900, fontSize:26, cursor:'pointer', color:T.ink, opacity: bj.betsDone[playerId] ? 0.4 : 1 }}>+</button>
            </div>"""

NEW = """            <div style={{ display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:8, marginBottom:18 }}>
              {(() => {
                const presets = [1, 2, 3, 5, 8, 10, 15, 20].filter(v => v <= myChips);
                if (!presets.includes(myChips)) presets.push(myChips);
                const betsLocked = !!bj.betsDone[playerId];
                return presets.map(v => {
                  const sel = myBet === v;
                  const allIn = v === myChips && ![1, 2, 3, 5, 8, 10, 15, 20].includes(v);
                  return (
                    <div key={v} onClick={betsLocked ? undefined : () => setMyBet(v)} style={{ padding:'12px 4px', borderRadius:12, border: sel ? `2px solid ${T.mint}` : `2px solid ${T.surfaceMuted}`, background: sel ? T.mintSoft : 'transparent', fontFamily:T.font, fontWeight:900, fontSize:15, color: sel ? T.mint : T.inkSoft, cursor: betsLocked ? 'default' : 'pointer', opacity: betsLocked ? 0.4 : 1 }}>{allIn ? `All-in (${v})` : v} 🍺</div>
                  );
                });
              })()}
            </div>"""

assert OLD in c, 'OLD stepper block not found'
assert c.count(OLD) == 1
c = c.replace(OLD, NEW)

VOLD = "const APP_VERSION = 'v9.805';"
assert c.count(VOLD) == 1
c = c.replace(VOLD, "const APP_VERSION = 'v9.806';")
assert c.count('v9.805') == 0
assert c.count('v9.806') == 1

io.open(P, 'w', encoding='utf-8').write(c)
print('patched OK')
