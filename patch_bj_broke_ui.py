#!/usr/bin/env python3
# v9.814 — BJ broke/rebuy panel: single calm card (white surface, coral border, bare picker)
import io

P = '/home/user/bottle-of-heroes/index.html'
c = io.open(P, encoding='utf-8').read()

# --- 1) BJStackPicker: optional `bare` prop -------------------------------
OLD = "function BJStackPicker({ onConfirm, onCancel }) {\n  const [sel, setSel] = React.useState(10);\n  return (\n    <div style={{ marginTop:10, padding:'10px', borderRadius:12, background:T.surfaceMuted }}>"
NEW = "function BJStackPicker({ onConfirm, onCancel, bare }) {\n  const [sel, setSel] = React.useState(10);\n  return (\n    <div style={ bare ? { marginTop:10 } : { marginTop:10, padding:'10px', borderRadius:12, background:T.surfaceMuted } }>"
assert OLD in c, 'picker header'
c = c.replace(OLD, NEW)

OLD = "border:`2px solid ${sel === v ? T.mint : 'transparent'}`, background: sel === v ? T.mintSoft : T.surface"
NEW = "border:`2px solid ${sel === v ? T.mint : (bare ? 'rgba(0,0,0,.08)' : 'transparent')}`, background: sel === v ? T.mintSoft : T.surface"
assert OLD in c, 'picker option border'
c = c.replace(OLD, NEW)

OLD = "<button onClick={onCancel} style={{ padding:'10px 14px', borderRadius:10, border:'none', background:T.surface, fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft, cursor:'pointer' }}>✕</button>"
NEW = "<button onClick={onCancel} style={{ padding:'10px 14px', borderRadius:10, border: bare ? '1.5px solid rgba(0,0,0,.12)' : 'none', background: bare ? 'transparent' : T.surface, fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft, cursor:'pointer' }}>✕</button>"
assert OLD in c, 'picker cancel'
c = c.replace(OLD, NEW)

# --- 2) Observer results phase: merge broke content into one calm card ----
OLD = """                return (
                  <div style={{ marginTop:12 }}>
                    <div style={{ padding:'12px', borderRadius:14, background: res.delta < 0 ? T.coralSoft : res.delta > 0 ? `${T.mint}20` : T.surfaceMuted, textAlign:'center' }}>
                      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color: res.delta < 0 ? T.coral : res.delta > 0 ? T.mint : T.ink }}>{res.label}</div>
                      <div style={{ fontFamily:T.font, fontSize:14, fontWeight:T.weightTitle, color: res.delta < 0 ? T.coral : res.delta > 0 ? T.mint : T.inkSoft, marginTop:6, display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
                        <span>{res.delta > 0 ? '+' : ''}{res.delta} 🍺 → készleted:</span>
                        <BJChipStack count={myChips} size={34} />
                      </div>
                    </div>
                    {broke ? (
                      <div style={{ marginTop:10, padding:'12px', borderRadius:14, background:T.coralSoft, textAlign:'center' }}>
                        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.coral }}>💀 Elfogyott a készleted!</div>
                        <div style={{ fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color:T.coral, marginTop:4 }}>Igyál {startStack} kortyot!</div>
                        {!rebuyPick && (
                        <div style={{ display:'flex', gap:8, marginTop:10 }}>
                          <button onClick={() => setRebuyPick({ drinkN: startStack })} style={{ flex:1, padding:'11px', borderRadius:12, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer' }}>🔄 Megittam — újra beszállok</button>
                          <button onClick={() => { if (!(bj.brokeDrank || {})[playerId]) bjBookDrinksRemote(code, playerId, startStack); bjWrite(code, { ...bj, cashedOut: { ...(bj.cashedOut || {}), [playerId]: true }, brokeDrank: { ...(bj.brokeDrank || {}), [playerId]: true } }); }} style={{ flex:1, padding:'11px', borderRadius:12, border:'none', background:'#555', fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer' }}>🚪 Kiszállok</button>
                        </div>
                        )}
                        {rebuyPick && (
                          <BJStackPicker onConfirm={v => guestRebuy(rebuyPick.drinkN, v)} onCancel={() => setRebuyPick(null)} />
                        )}
                      </div>
                    ) : !amOut ? ("""
NEW = """                return (
                  <div style={{ marginTop:12 }}>
                    {broke ? (
                      <div style={{ padding:'12px', borderRadius:14, background:T.surface, border:`1.5px solid ${T.coral}`, textAlign:'center' }}>
                        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.coral }}>{res.label} · {res.delta > 0 ? '+' : ''}{res.delta} 🍺</div>
                        <div style={{ height:1, background:'rgba(0,0,0,.08)', margin:'10px 0' }} />
                        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.coral }}>💀 Elfogyott a készleted — igyál {startStack} kortyot!</div>
                        {!rebuyPick && (
                        <div style={{ display:'flex', gap:8, marginTop:10 }}>
                          <button onClick={() => setRebuyPick({ drinkN: startStack })} style={{ flex:1, padding:'11px', borderRadius:12, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer' }}>🔄 Megittam — újra beszállok</button>
                          <button onClick={() => { if (!(bj.brokeDrank || {})[playerId]) bjBookDrinksRemote(code, playerId, startStack); bjWrite(code, { ...bj, cashedOut: { ...(bj.cashedOut || {}), [playerId]: true }, brokeDrank: { ...(bj.brokeDrank || {}), [playerId]: true } }); }} style={{ flex:1, padding:'11px', borderRadius:12, border:'none', background:'#555', fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer' }}>🚪 Kiszállok</button>
                        </div>
                        )}
                        {rebuyPick && (
                          <BJStackPicker bare onConfirm={v => guestRebuy(rebuyPick.drinkN, v)} onCancel={() => setRebuyPick(null)} />
                        )}
                      </div>
                    ) : (
                    <div style={{ padding:'12px', borderRadius:14, background: res.delta < 0 ? T.coralSoft : res.delta > 0 ? `${T.mint}20` : T.surfaceMuted, textAlign:'center' }}>
                      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color: res.delta < 0 ? T.coral : res.delta > 0 ? T.mint : T.ink }}>{res.label}</div>
                      <div style={{ fontFamily:T.font, fontSize:14, fontWeight:T.weightTitle, color: res.delta < 0 ? T.coral : res.delta > 0 ? T.mint : T.inkSoft, marginTop:6, display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
                        <span>{res.delta > 0 ? '+' : ''}{res.delta} 🍺 → készleted:</span>
                        <BJChipStack count={myChips} size={34} />
                      </div>
                    </div>
                    )}
                    {!broke && !amOut ? ("""
assert OLD in c, 'observer results block'
c = c.replace(OLD, NEW)

# --- 3) Host offline ResultsView broke row: white card + coral border -----
OLD = "<div key={pid} style={{ marginBottom:6, padding:'8px 10px', borderRadius:12, background:T.coralSoft }}>"
NEW = "<div key={pid} style={{ marginBottom:6, padding:'8px 10px', borderRadius:12, background:T.surface, border:`1.5px solid ${T.coral}` }}>"
assert OLD in c, 'host broke row'
c = c.replace(OLD, NEW)

OLD = "<BJStackPicker onConfirm={v => { hostRebuy(pid, true, v); setHostRebuyPick(null); }} onCancel={() => setHostRebuyPick(null)} />"
NEW = "<BJStackPicker bare onConfirm={v => { hostRebuy(pid, true, v); setHostRebuyPick(null); }} onCancel={() => setHostRebuyPick(null)} />"
assert OLD in c, 'host picker'
c = c.replace(OLD, NEW)

# --- 4) Version bump ------------------------------------------------------
assert c.count('v9.813') == 1, 'version count'
c = c.replace('v9.813', 'v9.814')

io.open(P, 'w', encoding='utf-8').write(c)
print('patch OK')
