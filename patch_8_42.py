#!/usr/bin/env python3
"""
v8.42: Busz — ász wild kártya (mindig helyes tipp), aceMode kapcsoló eltávolítva
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. evalBusGuess: ha a húzott kártya ász → mindig helyes ──────────────────
OLD_EVAL = """  const evalBusGuess = (guess, routeCard, drawnCard, aceHigh=true) => {
    const getIdx = v => v === 'A' ? (aceHigh ? 13 : -1) : CARD_VALUES.indexOf(v);
    const rr = getIdx(routeCard.value);
    const dr = getIdx(drawnCard.value);
    if (rr === dr) return false;
    return (guess === 'K' && dr < rr) || (guess === 'N' && dr > rr);
  };"""

NEW_EVAL = """  const evalBusGuess = (guess, routeCard, drawnCard) => {
    // Ace is wild — always correct when drawn
    if (drawnCard.value === 'A') return true;
    const getIdx = v => CARD_VALUES.indexOf(v);
    const rr = getIdx(routeCard.value);
    const dr = getIdx(drawnCard.value);
    if (rr === dr) return false;
    return (guess === 'K' && dr < rr) || (guess === 'N' && dr > rr);
  };"""

assert OLD_EVAL in content, "evalBusGuess not found"
content = content.replace(OLD_EVAL, NEW_EVAL, 1)
print("✓ evalBusGuess: ász wild")

# ── 2. Fix call site: remove aceHigh parameter ────────────────────────────────
OLD_CALL = "      const correct = evalBusGuess(actualGuess, routeCard, drawnCard, aceHigh);"
NEW_CALL = "      const correct = evalBusGuess(actualGuess, routeCard, drawnCard);"
assert OLD_CALL in content, "evalBusGuess call not found"
content = content.replace(OLD_CALL, NEW_CALL, 1)
print("✓ Call site updated")

# ── 3. Inline evalG in observer code: ász wild ────────────────────────────────
OLD_EVALG = "        const _aceHigh = settings?.aceMode !== 'low'; const evalG = (g, rc, dc) => { const getI=v=>v==='A'?(_aceHigh?13:-1):CARD_VALUES.indexOf(v); const rr=getI(rc.value),dr=getI(dc.value); if(rr===dr)return false; return (g==='K'&&dr<rr)||(g==='N'&&dr>rr); };"
NEW_EVALG = "        const evalG = (g, rc, dc) => { if(dc.value==='A')return true; const getI=v=>CARD_VALUES.indexOf(v); const rr=getI(rc.value),dr=getI(dc.value); if(rr===dr)return false; return (g==='K'&&dr<rr)||(g==='N'&&dr>rr); };"
assert OLD_EVALG in content, "inline evalG not found"
content = content.replace(OLD_EVALG, NEW_EVALG, 1)
print("✓ Observer inline evalG: ász wild")

# ── 4. Remove aceMode config section from BuszConfigSheet ────────────────────
OLD_ACE_CONFIG = """        {(() => { const aceHigh = config.aceMode !== 'low'; return (
          <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'13px 0', borderTop:'1px solid rgba(26,42,74,0.10)' }}>
            <div>
              <span style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>Ász értéke</span>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:1 }}>{aceHigh ? 'Magas — K felett (11-es)' : 'Alacsony — 2 alatt (1-es)'}</div>
            </div>
            <div style={{ display:'flex', background:T.surfaceMuted, padding:4, borderRadius:12, gap:3, flexShrink:0 }}>
              {[{k:'high',l:'11-es'},{k:'low',l:'1-es'}].map(o => (
                <button key={o.k} onClick={() => setConfig(c => ({...c, aceMode:o.k}))} style={{ padding:'7px 10px', borderRadius:9, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:12, background:(aceHigh?'high':'low')===o.k?T.mint:'transparent', color:(aceHigh?'high':'low')===o.k?'#fff':T.inkSoft, transition:'all .15s' }}>
                  {o.l}
                </button>
              ))}
            </div>
          </div>
        ); })()}"""
assert OLD_ACE_CONFIG in content, "aceMode config section not found"
content = content.replace(OLD_ACE_CONFIG, '', 1)
print("✓ aceMode kapcsoló eltávolítva")

# ── 5. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.41';"
NEW_VER = "const APP_VERSION = 'v8.42';"
assert OLD_VER in content
content = content.replace(OLD_VER, NEW_VER, 1)
print("✓ Version → v8.42")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Saved")
