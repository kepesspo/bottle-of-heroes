#!/usr/bin/env python3
"""Patch: Result banner full redesign (v9.639 → v9.640)"""
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()
orig = src

def replace_once(old, new, label):
    global src
    if old not in src:
        print(f'MISSING: {label}')
        sys.exit(1)
    if src.count(old) != 1:
        print(f'AMBIGUOUS ({src.count(old)}x): {label}')
        sys.exit(1)
    src = src.replace(old, new, 1)
    print(f'OK: {label}')

# ── 1. CSS animations ─────────────────────────────────────────────────────────
replace_once(
    '@keyframes podiumRise   { from{transform:scaleY(0);opacity:0} to{transform:scaleY(1);opacity:1} }',
    """@keyframes podiumRise   { from{transform:scaleY(0);opacity:0} to{transform:scaleY(1);opacity:1} }
    @keyframes resultBounceIn { 0%{transform:scale(0.4) translateY(-30px);opacity:0} 55%{transform:scale(1.08);opacity:1} 75%{transform:scale(0.96)} 100%{transform:scale(1)} }
    @keyframes resultShakeIn { 0%{transform:scale(0.5);opacity:0} 35%{transform:scale(1.06);opacity:1} 50%{transform:scale(1) translateX(-10px)} 65%{transform:translateX(10px)} 78%{transform:translateX(-5px)} 90%{transform:translateX(5px)} 100%{transform:translateX(0)} }
    @keyframes drinkNumPop { 0%{transform:scale(0.2);opacity:0} 65%{transform:scale(1.18)} 100%{transform:scale(1);opacity:1} }
    @keyframes starPop { 0%{transform:scale(0) rotate(-20deg);opacity:0} 55%{transform:scale(1.25) rotate(12deg);opacity:1} 100%{transform:scale(1) rotate(0deg)} }
    @keyframes resultFadeOut { from{opacity:1;transform:scale(1)} to{opacity:0;transform:scale(0.88)} }""",
    "CSS: result animations"
)

# ── 2. Auto-dismiss useEffect ─────────────────────────────────────────────────
replace_once(
    "useEffect(() => { setCsapatLosers(new Set()); setPendingCommit(null); setGameResult(null); }, [gameIdx]);",
    """useEffect(() => { setCsapatLosers(new Set()); setPendingCommit(null); setGameResult(null); }, [gameIdx]);
  useEffect(() => {
    if (!gameResult) return;
    const t = setTimeout(() => setGameResult(null), 2600);
    return () => clearTimeout(t);
  }, [gameResult && gameResult.ts]);""",
    "Auto-dismiss useEffect"
)

# ── 3. Replace full ResultBanner ──────────────────────────────────────────────
replace_once(
    """      {/* ResultBanner */}
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
                  {gameResult.correct ? 'Helyes! +1 pont 🌟' : 'Inni kell!'}
                </div>
                {gameResult.subtitle && (
                  <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>
                    {gameResult.subtitle}{gameResult.drinks > 0 ? ` — ${gameResult.drinks} korty` : ''}
                  </div>
                )}
                {!gameResult.subtitle && !gameResult.correct && gameResult.playerName && (
                  <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>
                    {gameResult.playerName} iszik {gameResult.drinks > 1 ? `${gameResult.drinks} kortyt` : 'egyet'}
                  </div>
                )}
                {!gameResult.subtitle && gameResult.correct && gameResult.playerName && (
                  <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>{gameResult.playerName} kap 1 pontot</div>
                )}
              </div>
              {/* Emoji right */}
              <div style={{ fontSize:24, flexShrink:0, animation: gameResult.correct ? undefined : 'shakeDrink 0.75s ease-in-out' }}>{gameResult.correct ? '🌟' : '🍺'}</div>
            </div>
          </div>
        );
      })()}""",
    """      {/* ResultBanner — full overlay */}
      {gameResult && (() => {
        const rp = gameResult.playerName ? players.find(p => p.name === gameResult.playerName) : null;
        const isCorrect = gameResult.correct;
        const anim = isCorrect
          ? 'resultBounceIn .45s cubic-bezier(.2,.9,.3,1.3) forwards'
          : 'resultShakeIn .5s ease-out forwards';
        const bgGrad = isCorrect
          ? 'linear-gradient(160deg, #1a8a55f0 0%, #25b572f0 100%)'
          : 'linear-gradient(160deg, #c02828f0 0%, #e84040f0 100%)';
        const glow = isCorrect ? '#25b572' : '#e84040';
        return (
          <div key={gameResult.ts} onClick={() => setGameResult(null)} style={{
            position:'fixed', inset:0, zIndex:250,
            display:'flex', alignItems:'center', justifyContent:'center',
            background:'rgba(0,0,0,0.35)', backdropFilter:'blur(3px)', WebkitBackdropFilter:'blur(3px)',
          }}>
            <div style={{
              background: bgGrad,
              borderRadius:32, padding:'32px 36px',
              display:'flex', flexDirection:'column', alignItems:'center', gap:14,
              animation: anim,
              boxShadow: `0 20px 70px ${glow}99, 0 0 0 1.5px rgba(255,255,255,0.18)`,
              minWidth:260, maxWidth:340, width:'80vw',
            }}>
              {/* Avatar or big emoji */}
              {rp ? (
                <div style={{
                  width:80, height:80, borderRadius:'50%', background:rp.color,
                  display:'grid', placeItems:'center', overflow:'hidden',
                  boxShadow:`0 0 0 5px rgba(255,255,255,0.45)`,
                  animation: isCorrect ? undefined : 'shakeDrink .7s ease-in-out',
                }}>
                  {rp.img ? <img src={rp.img} style={{ width:80, height:80, objectFit:'cover' }} />
                    : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:34, color:'#fff' }}>{(rp.name||'?').charAt(0).toUpperCase()}</span>}
                </div>
              ) : (
                <div style={{ fontSize:64, lineHeight:1, animation: isCorrect ? 'starPop .45s' : 'shakeDrink .7s ease-in-out' }}>
                  {isCorrect ? '🌟' : '🍺'}
                </div>
              )}
              {/* Headline */}
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:28, color:'#fff', textAlign:'center', lineHeight:1.1, textShadow:'0 2px 10px rgba(0,0,0,0.2)' }}>
                {isCorrect ? 'Helyes! 🌟' : 'Inni kell!'}
              </div>
              {/* Drink count — big */}
              {!isCorrect && gameResult.drinks > 0 && (
                <div style={{ display:'flex', alignItems:'baseline', gap:6, animation:'drinkNumPop .5s cubic-bezier(.2,.9,.3,1.4)' }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:64, color:'#fff', lineHeight:1, textShadow:'0 4px 20px rgba(0,0,0,0.25)' }}>{gameResult.drinks}</span>
                  <span style={{ fontFamily:T.font, fontWeight:700, fontSize:22, color:'rgba(255,255,255,0.85)' }}>korty</span>
                </div>
              )}
              {/* Player name */}
              {gameResult.playerName && (
                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:'rgba(255,255,255,0.9)', textAlign:'center' }}>
                  {isCorrect ? `${gameResult.playerName} — +1 pont` : gameResult.playerName}
                </div>
              )}
              {/* Subtitle */}
              {gameResult.subtitle && (
                <div style={{ fontFamily:T.font, fontSize:13, color:'rgba(255,255,255,0.78)', textAlign:'center', lineHeight:1.4 }}>
                  {gameResult.subtitle}
                </div>
              )}
              {/* Tap to dismiss hint */}
              <div style={{ fontFamily:T.font, fontSize:11, color:'rgba(255,255,255,0.45)', marginTop:4 }}>koppints a bezáráshoz</div>
            </div>
          </div>
        );
      })()}""",
    "ResultBanner full overlay redesign"
)

# ── Version bump ──────────────────────────────────────────────────────────────
replace_once(
    "const APP_VERSION = 'v9.639';",
    "const APP_VERSION = 'v9.640';",
    "version bump 9.639 → 9.640"
)

assert src != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)
print("\nAll patches applied.")
