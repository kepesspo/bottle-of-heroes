#!/usr/bin/env python3
"""
v9.607:
1. ResultBanner: avatar + jobb dizájn
2. Éjfél téma törlése
3. Kreatív témanevek
4. Témák azonos mérete (egy grid)
5. OVFJ Kész gomb sticky
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.606') >= 1
html = html.replace('v9.606', 'v9.607', 1)

# ── 1. THEME_DEFS: töröl Éjfél, kreatív nevek ────────────────────────────────
OLD_THEMES = """                const THEME_DEFS = [
                  { key:'warm',     label:'Meleg',    bg:'#F4C57E', accent:'#4FC2A0', surface:'#FFFFFF' },
                  { key:'peach',    label:'Barack',   bg:'#FFE8D8', accent:'#E06030', surface:'#FFFFFF' },
                  { key:'lemon',    label:'Citrom',   bg:'#F8F8D8', accent:'#808010', surface:'#FFFFFF' },
                  { key:'ice',      label:'Ice',      bg:'#E8F4FF', accent:'#2070C0', surface:'#FFFFFF' },
                  { key:'jade',     label:'Jade',     bg:'#B8E8C8', accent:'#20A060', surface:'#FFFFFF' },
                  { key:'dark',     label:'Sötét',    bg:'#2C3554', accent:'#4FC2A0', surface:'#3D4870' },
                  { key:'slate',    label:'Kő',       bg:'#1E2A38', accent:'#40C8A0', surface:'#2E3E50' },
                  { key:'midnight', label:'Éjfél',    bg:'#28204A', accent:'#9070F8', surface:'#3C2E60' },
                ];"""
NEW_THEMES = """                const THEME_DEFS = [
                  { key:'warm',     label:'Homokpart',   bg:'#F4C57E', accent:'#4FC2A0', surface:'#FFFFFF' },
                  { key:'peach',    label:'Naplemente',  bg:'#FFE8D8', accent:'#E06030', surface:'#FFFFFF' },
                  { key:'lemon',    label:'Limonádé',    bg:'#F8F8D8', accent:'#808010', surface:'#FFFFFF' },
                  { key:'ice',      label:'Jéghegy',     bg:'#E8F4FF', accent:'#2070C0', surface:'#FFFFFF' },
                  { key:'jade',     label:'Dzsungel',    bg:'#B8E8C8', accent:'#20A060', surface:'#FFFFFF' },
                  { key:'dark',     label:'Kozmosz',     bg:'#2C3554', accent:'#4FC2A0', surface:'#3D4870' },
                  { key:'slate',    label:'Mélytenger',  bg:'#1E2A38', accent:'#40C8A0', surface:'#2E3E50' },
                ];"""
assert html.count(OLD_THEMES) == 1, f"themes: {html.count(OLD_THEMES)}"
html = html.replace(OLD_THEMES, NEW_THEMES, 1)
print("OK: témák átnevezve, Éjfél törölve")

# ── 2. Light/dark filter + grid: egy unified grid, azonos méret ───────────────
OLD_GRID = """                const lightThemes = THEME_DEFS.filter(d => !['dark','slate','midnight'].includes(d.key));
                const darkThemes  = THEME_DEFS.filter(d =>  ['dark','slate','midnight'].includes(d.key));
                return (
                  <>
                    <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:8 }}>☀️ Világos témák</div>
                    <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:8, marginBottom:16 }}>
                      {lightThemes.map(def => <ThemeBtn key={def.key} def={def} />)}
                    </div>
                    <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:8 }}>🌙 Sötét témák</div>
                    <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:8, marginBottom:24 }}>
                      {darkThemes.map(def => <ThemeBtn key={def.key} def={def} />)}
                    </div>
                  </>
                );"""
NEW_GRID = """                return (
                  <>
                    <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:8 }}>🎨 Témák</div>
                    <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:8, marginBottom:24 }}>
                      {THEME_DEFS.map(def => <ThemeBtn key={def.key} def={def} />)}
                    </div>
                  </>
                );"""
assert html.count(OLD_GRID) == 1, f"grid: {html.count(OLD_GRID)}"
html = html.replace(OLD_GRID, NEW_GRID, 1)
print("OK: unified 4-column téma grid")

# ── 3. ResultBanner: avatar + jobb dizájn ─────────────────────────────────────
OLD_BANNER = """      {/* ResultBanner */}
      {gameResult && (
        <div style={{ flexShrink:0, padding:'0 18px 8px', maxWidth:960, margin:'0 auto', width:'100%', boxSizing:'border-box' }}>
          <div style={{ borderRadius:16, padding:'12px 16px', display:'flex', alignItems:'center', gap:12, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)', background: gameResult.correct ? `${T.mint}1e` : `${T.coral}2e`, border:`2px solid ${gameResult.correct ? T.mint : T.coral}` }}>
            <div key={gameResult.ts} style={{ fontSize:26, display:'inline-block', animation: gameResult.correct ? undefined : 'shakeDrink 0.75s ease-in-out' }}>{gameResult.correct ? '🎉' : '🍺'}</div>
            <div>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color: gameResult.correct ? '#50A882' : '#C05050' }}>
                {gameResult.correct ? 'Helyes! +1 pont 🌟' : 'Inni kell!'}
              </div>
              {gameResult.subtitle && (
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:1 }}>
                  {gameResult.subtitle}{gameResult.drinks > 0 ? ` — ${gameResult.drinks} kortyt iszik!` : ''}
                </div>
              )}
              {!gameResult.subtitle && !gameResult.correct && gameResult.playerName && (
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:1 }}>
                  {gameResult.playerName} iszik {gameResult.drinks > 1 ? `${gameResult.drinks} kortyt` : 'egyet'}
                </div>
              )}
              {!gameResult.subtitle && gameResult.correct && gameResult.playerName && (
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:1 }}>{gameResult.playerName} kap 1 pontot</div>
              )}
            </div>
          </div>
        </div>
      )}"""
NEW_BANNER = """      {/* ResultBanner */}
      {gameResult && (() => {
        const rp = gameResult.playerName ? players.find(p => p.name === gameResult.playerName) : null;
        const accent = gameResult.correct ? T.mint : T.coral;
        const accentText = gameResult.correct ? '#1a7a50' : '#b83030';
        return (
          <div style={{ flexShrink:0, padding:'0 18px 8px', maxWidth:960, margin:'0 auto', width:'100%', boxSizing:'border-box' }}>
            <div key={gameResult.ts} style={{ borderRadius:18, padding:'12px 16px', display:'flex', alignItems:'center', gap:12, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)', background: gameResult.correct ? `${T.mint}18` : `${T.coral}22`, border:`2px solid ${accent}44` }}>
              {/* Avatar */}
              {rp ? (
                <div style={{ width:48, height:48, borderRadius:'50%', background:rp.color, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0, boxShadow:`0 0 0 3px ${accent}55` }}>
                  {rp.img ? <img src={rp.img} style={{ width:48, height:48, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:'#fff' }}>{(rp.name||'?').charAt(0).toUpperCase()}</span>}
                </div>
              ) : (
                <div style={{ fontSize:28, flexShrink:0, animation: gameResult.correct ? undefined : 'shakeDrink 0.75s ease-in-out' }}>{gameResult.correct ? '🎉' : '🍺'}</div>
              )}
              {/* Text */}
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:accentText }}>
                  {gameResult.correct ? (rp ? `${rp.name} pontot kap! 🌟` : 'Helyes! +1 pont 🌟') : (rp ? `${rp.name} iszik!` : 'Inni kell!')}
                </div>
                {gameResult.subtitle && (
                  <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>
                    {gameResult.subtitle}{gameResult.drinks > 0 ? ` — ${gameResult.drinks} korty` : ''}
                  </div>
                )}
                {!gameResult.subtitle && !gameResult.correct && gameResult.drinks > 1 && (
                  <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>{gameResult.drinks} korty</div>
                )}
              </div>
              {/* Emoji right */}
              <div style={{ fontSize:24, flexShrink:0, animation: gameResult.correct ? undefined : 'shakeDrink 0.75s ease-in-out' }}>{gameResult.correct ? '🌟' : '🍺'}</div>
            </div>
          </div>
        );
      })()}"""
assert html.count(OLD_BANNER) == 1, f"banner: {html.count(OLD_BANNER)}"
html = html.replace(OLD_BANNER, NEW_BANNER, 1)
print("OK: ResultBanner avatar redesign")

# ── 4. OVFJ Kész gomb: sticky bottom ─────────────────────────────────────────
OLD_KÉSZ = "        <div ref={submitAreaRef}>"
NEW_KÉSZ = "        <div ref={submitAreaRef} style={{position:'sticky',bottom:0,background:T.bg,paddingTop:8,paddingBottom:4,zIndex:10}}>"
assert html.count(OLD_KÉSZ) == 1, f"kész: {html.count(OLD_KÉSZ)}"
html = html.replace(OLD_KÉSZ, NEW_KÉSZ, 1)
print("OK: Kész gomb sticky")

print(f"Final size: {len(html):,} chars")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
