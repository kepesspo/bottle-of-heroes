#!/usr/bin/env python3
"""Patch: Result banner → shrinks to mini pill (v9.641 → v9.642)"""
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()
orig = src

def replace_once(old, new, label):
    global src
    if old not in src:
        print(f'MISSING: {label}'); sys.exit(1)
    if src.count(old) != 1:
        print(f'AMBIGUOUS ({src.count(old)}x): {label}'); sys.exit(1)
    src = src.replace(old, new, 1)
    print(f'OK: {label}')

# ── 1. CSS: mini pill animation ───────────────────────────────────────────────
replace_once(
    '@keyframes resultFadeOut { from{opacity:1;transform:scale(1)} to{opacity:0;transform:scale(0.88)} }',
    """@keyframes resultFadeOut { from{opacity:1;transform:scale(1)} to{opacity:0;transform:scale(0.88)} }
    @keyframes miniPillIn { from{transform:translateY(60px) scale(0.7);opacity:0} to{transform:translateY(0) scale(1);opacity:1} }""",
    "CSS: miniPillIn animation"
)

# ── 2. Add resultMinimized state ──────────────────────────────────────────────
replace_once(
    "const [gameResult, setGameResult] = useState(null); // { correct, playerName }",
    "const [gameResult, setGameResult] = useState(null); // { correct, playerName }\n  const [resultMinimized, setResultMinimized] = useState(false);",
    "resultMinimized state"
)

# ── 3. Clear resultMinimized on gameIdx change ────────────────────────────────
replace_once(
    "useEffect(() => { setCsapatLosers(new Set()); setPendingCommit(null); setGameResult(null); }, [gameIdx]);",
    "useEffect(() => { setCsapatLosers(new Set()); setPendingCommit(null); setGameResult(null); setResultMinimized(false); }, [gameIdx]);",
    "clear resultMinimized on gameIdx"
)

# ── 4. Auto-dismiss: minimize instead of clearing ────────────────────────────
replace_once(
    """  useEffect(() => {
    if (!gameResult) return;
    const t = setTimeout(() => setGameResult(null), 2600);
    return () => clearTimeout(t);
  }, [gameResult && gameResult.ts]);""",
    """  useEffect(() => {
    if (!gameResult) return;
    setResultMinimized(false);
    const t = setTimeout(() => setResultMinimized(true), 2600);
    return () => clearTimeout(t);
  }, [gameResult && gameResult.ts]);""",
    "auto-minimize useEffect"
)

# ── 5. Replace ResultBanner render with two-state version ─────────────────────
replace_once(
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
    """      {/* ResultBanner — full overlay or mini pill */}
      {gameResult && (() => {
        const rp = gameResult.playerName ? players.find(p => p.name === gameResult.playerName) : null;
        const isCorrect = gameResult.correct;
        const bgGrad = isCorrect
          ? 'linear-gradient(160deg, #1a8a55f0 0%, #25b572f0 100%)'
          : 'linear-gradient(160deg, #c02828f0 0%, #e84040f0 100%)';
        const glow = isCorrect ? '#25b572' : '#e84040';

        if (resultMinimized) {
          // ── Mini pill ──────────────────────────────────────────────────────
          return (
            <div key={'mini-' + gameResult.ts} onClick={() => setResultMinimized(false)} style={{
              position:'fixed', bottom:90, left:'50%', transform:'translateX(-50%)',
              zIndex:200, animation:'miniPillIn .35s cubic-bezier(.2,.9,.3,1.2)',
              pointerEvents:'auto',
            }}>
              <div style={{
                background: bgGrad,
                borderRadius:50, padding:'8px 16px 8px 10px',
                display:'flex', alignItems:'center', gap:10,
                boxShadow:`0 4px 20px ${glow}66`,
              }}>
                {/* Small avatar */}
                {rp ? (
                  <div style={{ width:32, height:32, borderRadius:'50%', background:rp.color, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0, boxShadow:'0 0 0 2px rgba(255,255,255,0.5)' }}>
                    {rp.img ? <img src={rp.img} style={{ width:32, height:32, objectFit:'cover' }} />
                      : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff' }}>{(rp.name||'?').charAt(0).toUpperCase()}</span>}
                  </div>
                ) : (
                  <span style={{ fontSize:22 }}>{isCorrect ? '🌟' : '🍺'}</span>
                )}
                {/* Text */}
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:'#fff', whiteSpace:'nowrap' }}>
                  {isCorrect ? 'Helyes! +1 🌟' : `Inni kell!${gameResult.drinks > 0 ? ` ${gameResult.drinks} 🍺` : ''}`}
                </div>
                {/* Player name */}
                {gameResult.playerName && (
                  <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.75)', whiteSpace:'nowrap' }}>
                    — {gameResult.playerName}
                  </div>
                )}
              </div>
            </div>
          );
        }

        // ── Full overlay ───────────────────────────────────────────────────
        const anim = isCorrect
          ? 'resultBounceIn .45s cubic-bezier(.2,.9,.3,1.3) forwards'
          : 'resultShakeIn .5s ease-out forwards';
        return (
          <div key={gameResult.ts} onClick={() => setResultMinimized(true)} style={{
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
              {rp ? (
                <div style={{ width:80, height:80, borderRadius:'50%', background:rp.color, display:'grid', placeItems:'center', overflow:'hidden', boxShadow:'0 0 0 5px rgba(255,255,255,0.45)', animation: isCorrect ? undefined : 'shakeDrink .7s ease-in-out' }}>
                  {rp.img ? <img src={rp.img} style={{ width:80, height:80, objectFit:'cover' }} />
                    : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:34, color:'#fff' }}>{(rp.name||'?').charAt(0).toUpperCase()}</span>}
                </div>
              ) : (
                <div style={{ fontSize:64, lineHeight:1, animation: isCorrect ? 'starPop .45s' : 'shakeDrink .7s ease-in-out' }}>
                  {isCorrect ? '🌟' : '🍺'}
                </div>
              )}
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:28, color:'#fff', textAlign:'center', lineHeight:1.1, textShadow:'0 2px 10px rgba(0,0,0,0.2)' }}>
                {isCorrect ? 'Helyes! 🌟' : 'Inni kell!'}
              </div>
              {!isCorrect && gameResult.drinks > 0 && (
                <div style={{ display:'flex', alignItems:'baseline', gap:6, animation:'drinkNumPop .5s cubic-bezier(.2,.9,.3,1.4)' }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:64, color:'#fff', lineHeight:1, textShadow:'0 4px 20px rgba(0,0,0,0.25)' }}>{gameResult.drinks}</span>
                  <span style={{ fontFamily:T.font, fontWeight:700, fontSize:22, color:'rgba(255,255,255,0.85)' }}>korty</span>
                </div>
              )}
              {gameResult.playerName && (
                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:'rgba(255,255,255,0.9)', textAlign:'center' }}>
                  {isCorrect ? `${gameResult.playerName} — +1 pont` : gameResult.playerName}
                </div>
              )}
              {gameResult.subtitle && (
                <div style={{ fontFamily:T.font, fontSize:13, color:'rgba(255,255,255,0.78)', textAlign:'center', lineHeight:1.4 }}>
                  {gameResult.subtitle}
                </div>
              )}
              <div style={{ fontFamily:T.font, fontSize:11, color:'rgba(255,255,255,0.45)', marginTop:4 }}>koppints a kicsinyítéshez</div>
            </div>
          </div>
        );
      })()}""",
    "ResultBanner two-state: overlay + mini pill"
)

# ── Version bump ──────────────────────────────────────────────────────────────
replace_once(
    "const APP_VERSION = 'v9.641';",
    "const APP_VERSION = 'v9.642';",
    "version bump 9.641 → 9.642"
)

assert src != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)
print("\nAll patches applied.")
