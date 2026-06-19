#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Új keyframe-ek hozzáadása
old_kf = "    @keyframes gameProgressGrow { from{width:0} to{width:100%} }"
new_kf = """    @keyframes gameProgressGrow { from{width:0} to{width:100%} }
    @keyframes nextBounce  { 0%,100%{transform:translateY(0) scale(1)} 40%{transform:translateY(-7px) scale(1.10)} 70%{transform:translateY(-3px) scale(1.03)} }
    @keyframes shakeDrink  { 0%{transform:rotate(0) scale(1)} 15%{transform:rotate(-20deg) scale(1.25)} 35%{transform:rotate(15deg) scale(1.18)} 55%{transform:rotate(-10deg) scale(1.1)} 75%{transform:rotate(8deg)} 90%{transform:rotate(-3deg)} 100%{transform:rotate(0) scale(1)} }
    @keyframes confettiUp  { 0%{transform:translateY(0) rotate(0deg) scale(1);opacity:1} 100%{transform:translateY(-130px) rotate(540deg) scale(0.4);opacity:0} }"""
assert old_kf in html, "FAIL: keyframes"
html = html.replace(old_kf, new_kf, 1)

# ── 2. Kövi gomb bounce animáció pendingCommit esetén
old_btn = """            <button onClick={commitPending} disabled={!active} style={{
              flex:1, borderRadius:999,
              border:'none',
              cursor: active ? 'pointer' : 'default',
              background: active ? T.mint : 'transparent',
              display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:3,
              padding:'8px 0', minWidth:0,
              transition:'background .25s',
            }}>"""
new_btn = """            <button onClick={commitPending} disabled={!active} style={{
              flex:1, borderRadius:999,
              border:'none',
              cursor: active ? 'pointer' : 'default',
              background: active ? T.mint : 'transparent',
              display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:3,
              padding:'8px 0', minWidth:0,
              transition:'background .25s',
              animation: active ? 'nextBounce 1.4s ease-in-out infinite' : undefined,
            }}>"""
assert old_btn in html, "FAIL: Kövi gomb"
html = html.replace(old_btn, new_btn, 1)

# ── 3. Shake animáció a 🍺 ikonra + timestamp a gameResult-ban (újraindításhoz)
old_onresult = "    setGameResult({ ...res, drinks: scaled, subtitle });"
new_onresult = "    setGameResult({ ...res, drinks: scaled, subtitle, ts: Date.now() });"
assert old_onresult in html, "FAIL: onResult setGameResult"
html = html.replace(old_onresult, new_onresult, 1)

old_drink_icon = """            <div style={{ fontSize:26 }}>{gameResult.correct ? '🎉' : '🍺'}</div>"""
new_drink_icon = """            <div key={gameResult.ts} style={{ fontSize:26, display:'inline-block', animation: gameResult.correct ? undefined : 'shakeDrink 0.75s ease-in-out' }}>{gameResult.correct ? '🎉' : '🍺'}</div>"""
assert old_drink_icon in html, "FAIL: drink icon"
html = html.replace(old_drink_icon, new_drink_icon, 1)

# ── 4. Konfetti burst pontszerzéskor — ConfettiPop komponens a ResultBanner elé
old_confetti_anchor = "      {/* ResultBanner */}\n      {gameResult && ("
new_confetti_anchor = """      {/* ConfettiPop */}
      {gameResult?.correct && (() => {
        const COLS = ['#F59E0B','#10B981','#6366F1','#EC4899','#F97316','#14B8A6','#EF4444','#8B5CF6','#FBBF24','#34D399','#A78BFA','#F472B6'];
        const pts = Array.from({length:14}, (_,i) => ({
          id: i,
          left: 5 + (i * 7.2) % 90,
          color: COLS[i % COLS.length],
          delay: (i * 0.07).toFixed(2),
          dur: (0.7 + (i % 5) * 0.12).toFixed(2),
          size: 5 + (i % 4) * 3,
          round: i % 3 !== 0,
        }));
        return (
          <div key={gameResult.ts} style={{ position:'fixed', bottom:85, left:0, right:0, height:0, pointerEvents:'none', zIndex:300 }}>
            {pts.map(p => (
              <div key={p.id} style={{
                position:'absolute', left:`${p.left}%`, bottom:0,
                width:p.size, height:p.size,
                borderRadius: p.round ? '50%' : 2,
                background: p.color,
                animation: `confettiUp ${p.dur}s ${p.delay}s ease-out forwards`,
              }} />
            ))}
          </div>
        );
      })()}
      {/* ResultBanner */}
      {gameResult && ("""
assert old_confetti_anchor in html, "FAIL: ConfettiPop anchor"
html = html.replace(old_confetti_anchor, new_confetti_anchor, 1)

# ── 5. Frosted glass a SheetOverlay belső divjén
old_sheet_inner = """        width:'100%', background:T.surface,
          borderTopLeftRadius:20, borderTopRightRadius:20,
          boxShadow:'0 -10px 40px rgba(0,0,0,0.2)',
          animation: closing ? 'none' : 'slideUp .3s cubic-bezier(.2,.9,.3,1)',
          maxHeight:'85%', overflowY:'auto',
          transform: `translateY(${translateY})`,
          transition: dragY === 0 && !closing ? 'transform .22s cubic-bezier(.2,.9,.3,1)' : closing ? 'transform .22s ease-in' : 'none',
          willChange:'transform',"""
new_sheet_inner = """        width:'100%', background: T.surface + 'EE',
          backdropFilter:'blur(20px) saturate(1.6)',
          WebkitBackdropFilter:'blur(20px) saturate(1.6)',
          borderTopLeftRadius:20, borderTopRightRadius:20,
          boxShadow:'0 -10px 40px rgba(0,0,0,0.2)',
          animation: closing ? 'none' : 'slideUp .3s cubic-bezier(.2,.9,.3,1)',
          maxHeight:'85%', overflowY:'auto',
          transform: `translateY(${translateY})`,
          transition: dragY === 0 && !closing ? 'transform .22s cubic-bezier(.2,.9,.3,1)' : closing ? 'transform .22s ease-in' : 'none',
          willChange:'transform',"""
assert old_sheet_inner in html, "FAIL: SheetOverlay frosted glass"
html = html.replace(old_sheet_inner, new_sheet_inner, 1)

html = html.replace("const APP_VERSION = 'v9.304';", "const APP_VERSION = 'v9.305';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.305 — Bounce (Kövi), Shake (🍺), Konfetti (pont), Frosted glass (sheet)")
