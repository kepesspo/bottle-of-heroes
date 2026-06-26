#!/usr/bin/env python3
"""Patch: Result mini bar full-width + fade anim + zIndex fix (v9.643 → v9.644)"""
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

# ── 1. CSS: fix shrinkOut transform order (translateY FIRST, then scale) ───────
replace_once(
    "@keyframes resultShrinkOut { 0%{transform:scale(1) translateY(0);opacity:1;border-radius:32px} 100%{transform:scale(0.18) translateY(38vh);opacity:0;border-radius:50px} }",
    "@keyframes resultShrinkOut { 0%{transform:translateY(0) scale(1);opacity:1} 100%{transform:translateY(42vh) scale(0.15);opacity:0} }",
    "CSS: resultShrinkOut transform order fix"
)

# miniPillIn → fadeIn (egyszerű megjelenés, nem oldalas slide)
replace_once(
    "@keyframes miniPillIn { from{transform:translateY(60px) scale(0.7);opacity:0} to{transform:translateY(0) scale(1);opacity:1} }",
    "@keyframes miniBarIn { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }",
    "CSS: miniBarIn animáció (fade+slide up)"
)

# ── 2. A mini pill renderelése → full-width bar, zIndex:45, fadeIn ─────────────
replace_once(
    """              {/* Mini pill */}
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
              )}""",
    """              {/* Mini bar — full width, above footer, below sheet */}
              {showPill && (
                <div key={'mini-' + gameResult.ts} onClick={() => setResultMinimized(false)} style={{
                  position:'fixed',
                  bottom:'calc(68px + env(safe-area-inset-bottom, 0px))',
                  left:16, right:16,
                  zIndex:45,
                  animation:'miniBarIn .25s ease-out',
                  borderRadius:20,
                  background: bgGrad,
                  padding:'10px 14px',
                  display:'flex', alignItems:'center', gap:12,
                  boxShadow:`0 -2px 16px ${glow}33, 0 4px 16px ${glow}44`,
                  cursor:'pointer',
                }}>
                  {rp ? (
                    <div style={{ width:34, height:34, borderRadius:'50%', background:rp.color, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0, boxShadow:'0 0 0 2.5px rgba(255,255,255,0.5)' }}>
                      {rp.img ? <img src={rp.img} style={{ width:34, height:34, objectFit:'cover' }} />
                        : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff' }}>{(rp.name||'?').charAt(0).toUpperCase()}</span>}
                    </div>
                  ) : <span style={{ fontSize:26, flexShrink:0 }}>{isCorrect ? '🌟' : '🍺'}</span>}
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff' }}>
                      {isCorrect ? 'Helyes! +1 pont 🌟' : 'Inni kell!'}
                    </div>
                    {!isCorrect && gameResult.drinks > 0 && (
                      <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:'rgba(255,255,255,0.85)' }}>
                        {gameResult.drinks} korty 🍺
                      </div>
                    )}
                    {gameResult.subtitle && (
                      <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.8)' }}>{gameResult.subtitle}</div>
                    )}
                  </div>
                  <span style={{ fontSize:18, flexShrink:0, opacity:0.7 }}>▲</span>
                </div>
              )}""",
    "Mini bar: full-width, zIndex:45, fadeIn, above footer"
)

# ── Version bump ──────────────────────────────────────────────────────────────
replace_once(
    "const APP_VERSION = 'v9.643';",
    "const APP_VERSION = 'v9.644';",
    "version bump 9.643 → 9.644"
)

assert src != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)
print("\nAll patches applied.")
