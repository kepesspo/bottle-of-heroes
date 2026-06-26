#!/usr/bin/env python3
"""Patch: Result banner shrink anim + bottomsheet fix (v9.642 → v9.643)"""
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

# ── 1. CSS: shrink animation + backdrop fade ──────────────────────────────────
replace_once(
    '@keyframes miniPillIn { from{transform:translateY(60px) scale(0.7);opacity:0} to{transform:translateY(0) scale(1);opacity:1} }',
    """@keyframes miniPillIn { from{transform:translateY(60px) scale(0.7);opacity:0} to{transform:translateY(0) scale(1);opacity:1} }
    @keyframes resultShrinkOut { 0%{transform:scale(1) translateY(0);opacity:1;border-radius:32px} 100%{transform:scale(0.18) translateY(38vh);opacity:0;border-radius:50px} }
    @keyframes backdropFadeOut { from{opacity:1} to{opacity:0} }""",
    "CSS: shrink + backdrop animations"
)

# ── 2. Bottomsheet: overflow:'hidden' vissza + footer padding fix ─────────────
replace_once(
    """          boxShadow:'0 -8px 60px rgba(0,0,0,0.28)',
          animation: closing ? 'none' : 'slideUp .3s cubic-bezier(.2,.9,.3,1)',
          maxHeight:'82vh',
          display:'flex', flexDirection:'column',""",
    """          boxShadow:'0 -8px 60px rgba(0,0,0,0.28)',
          animation: closing ? 'none' : 'slideUp .3s cubic-bezier(.2,.9,.3,1)',
          maxHeight:'82vh',
          display:'flex', flexDirection:'column',
          overflow:'hidden',""",
    "SheetOverlay: overflow:hidden vissza"
)

# Accent strip: visszaállítjuk az egyszerű formára (overflow wrapper nem kell ha a szülőnek van)
replace_once(
    """        {/* Accent gradient strip */}
        <div style={{ overflow:'hidden', borderTopLeftRadius:28, borderTopRightRadius:28, flexShrink:0 }}>
          <div style={{ height:3, background:`linear-gradient(90deg, ${T.mint}, ${T.coral})` }} />
        </div>""",
    """        {/* Accent gradient strip */}
        <div style={{ height:3, background:`linear-gradient(90deg, ${T.mint}, ${T.coral})`, flexShrink:0 }} />""",
    "SheetOverlay: accent strip egyszerűsítés"
)

# Footer padding: env(safe-area-inset-bottom) már a fix div kezeli
replace_once(
    "padding:'8px 16px', paddingBottom:'max(20px, env(safe-area-inset-bottom))'",
    "padding:'8px 16px 20px'",
    "SheetOverlay: footer padding fix"
)

# ── 3. resultMinimized state: három érték ('false' | 'shrinking' | 'true') ────
# Az auto-minimize effect: 'shrinking' stateből vált
replace_once(
    """  useEffect(() => {
    if (!gameResult) return;
    setResultMinimized(false);
    const t = setTimeout(() => setResultMinimized(true), 2600);
    return () => clearTimeout(t);
  }, [gameResult && gameResult.ts]);""",
    """  useEffect(() => {
    if (!gameResult) return;
    setResultMinimized(false);
    const t = setTimeout(() => setResultMinimized('shrinking'), 2600);
    return () => clearTimeout(t);
  }, [gameResult && gameResult.ts]);""",
    "Auto-minimize: shrinking state"
)

# ── 4. ResultBanner: shrinking state + animáció ───────────────────────────────
replace_once(
    """        if (resultMinimized) {
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
        }""",
    """        if (resultMinimized === 'shrinking' || resultMinimized === true) {
          // ── Mini pill (vagy shrinking state előtte) ────────────────────────
          const showPill = resultMinimized === true;
          return (
            <>
              {/* Shrinking overlay — csak animáció közben látszik */}
              {resultMinimized === 'shrinking' && (
                <div style={{
                  position:'fixed', inset:0, zIndex:250,
                  display:'flex', alignItems:'center', justifyContent:'center',
                  animation:'backdropFadeOut .35s ease forwards',
                  pointerEvents:'none',
                }}>
                  <div style={{
                    background: bgGrad,
                    borderRadius:32, padding:'32px 36px',
                    display:'flex', flexDirection:'column', alignItems:'center', gap:14,
                    minWidth:260, maxWidth:340, width:'80vw',
                    animation:'resultShrinkOut .35s cubic-bezier(.4,0,.6,1) forwards',
                    boxShadow:`0 20px 70px ${glow}99`,
                  }} onAnimationEnd={() => setResultMinimized(true)}>
                    {rp ? (
                      <div style={{ width:80, height:80, borderRadius:'50%', background:rp.color, display:'grid', placeItems:'center', overflow:'hidden', boxShadow:'0 0 0 5px rgba(255,255,255,0.45)' }}>
                        {rp.img ? <img src={rp.img} style={{ width:80, height:80, objectFit:'cover' }} />
                          : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:34, color:'#fff' }}>{(rp.name||'?').charAt(0).toUpperCase()}</span>}
                      </div>
                    ) : <div style={{ fontSize:64 }}>{isCorrect ? '🌟' : '🍺'}</div>}
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:28, color:'#fff' }}>{isCorrect ? 'Helyes! 🌟' : 'Inni kell!'}</div>
                    {!isCorrect && gameResult.drinks > 0 && (
                      <div style={{ display:'flex', alignItems:'baseline', gap:6 }}>
                        <span style={{ fontFamily:T.font, fontWeight:900, fontSize:64, color:'#fff', lineHeight:1 }}>{gameResult.drinks}</span>
                        <span style={{ fontFamily:T.font, fontWeight:700, fontSize:22, color:'rgba(255,255,255,0.85)' }}>korty</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
              {/* Mini pill */}
              {showPill && (
                <div key={'mini-' + gameResult.ts} onClick={() => setResultMinimized(false)} style={{
                  position:'fixed', bottom:96, left:'50%', transform:'translateX(-50%)',
                  zIndex:200, animation:'miniPillIn .3s cubic-bezier(.2,.9,.3,1.2)',
                  pointerEvents:'auto',
                }}>
                  <div style={{
                    background: bgGrad,
                    borderRadius:50, padding:'8px 14px 8px 10px',
                    display:'flex', alignItems:'center', gap:9,
                    boxShadow:`0 4px 20px ${glow}66`,
                  }}>
                    {rp ? (
                      <div style={{ width:30, height:30, borderRadius:'50%', background:rp.color, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0, boxShadow:'0 0 0 2px rgba(255,255,255,0.5)' }}>
                        {rp.img ? <img src={rp.img} style={{ width:30, height:30, objectFit:'cover' }} />
                          : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff' }}>{(rp.name||'?').charAt(0).toUpperCase()}</span>}
                      </div>
                    ) : <span style={{ fontSize:20 }}>{isCorrect ? '🌟' : '🍺'}</span>}
                    <div style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:'#fff', whiteSpace:'nowrap' }}>
                      {isCorrect ? 'Helyes! +1 🌟' : `Inni kell!${gameResult.drinks > 0 ? ` ${gameResult.drinks} 🍺` : ''}`}
                    </div>
                  </div>
                </div>
              )}
            </>
          );
        }""",
    "ResultBanner: shrinking state + pill (player name nélkül)"
)

# ── Version bump ──────────────────────────────────────────────────────────────
replace_once(
    "const APP_VERSION = 'v9.642';",
    "const APP_VERSION = 'v9.643';",
    "version bump 9.642 → 9.643"
)

assert src != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)
print("\nAll patches applied.")
