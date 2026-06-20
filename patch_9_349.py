#!/usr/bin/env python3
"""v9.349 — Three fixes:
   1. New player gets default name 'Játékos N'
   2. Install button more prominent on home screen
   3. Onboarding: swipe left/right to navigate steps
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. New player default name
old_add = "const np = { id:'p'+Date.now(), name:'', color, drinks:0, points:0, img:null };"
new_add = "const np = { id:'p'+Date.now(), name:`Játékos ${players.length + 1}`, color, drinks:0, points:0, img:null };"
assert old_add in html, "FAIL: addPlayer"
html = html.replace(old_add, new_add, 1)

# ── 2. Install button more prominent — replace subtle list item with a bold CTA card
old_install = """          {!isStandalone && (
            <button onClick={() => setShowInstall(true)} style={{ display:'flex', alignItems:'center', gap:14, width:'100%', padding:'14px 16px', background:T.surface, border:'none', borderRadius:16, cursor:'pointer', textAlign:'left', boxShadow:T.shadow }}>
              <div style={{ width:44, height:44, borderRadius:12, background:T.mint, display:'grid', placeItems:'center', flexShrink:0 }}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12" y2="18.01"/></svg>
              </div>
              <div style={{ flex:1 }}>
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }}>{t('addToHome')}</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>{t('installHomeBtn')}</div>
              </div>
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M7 4l5 5-5 5" stroke={T.inkSoft} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/></svg>
            </button>
          )}"""
new_install = """          {!isStandalone && (
            <button onClick={() => setShowInstall(true)} style={{ display:'flex', alignItems:'center', gap:14, width:'100%', padding:'16px 20px', background:T.mint, border:'none', borderRadius:20, cursor:'pointer', textAlign:'left', boxShadow:`0 4px 0 ${T.mintDeep}, 0 6px 24px ${T.mint}55` }}>
              <div style={{ width:48, height:48, borderRadius:14, background:'rgba(255,255,255,0.22)', display:'grid', placeItems:'center', flexShrink:0 }}>
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v13M8 12l4 4 4-4"/><rect x="3" y="18" width="18" height="3" rx="1.5" fill="#fff" stroke="none"/></svg>
              </div>
              <div style={{ flex:1 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff', letterSpacing:'-0.01em' }}>{t('addToHome')}</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.82)', marginTop:2 }}>{t('installHomeBtn')}</div>
              </div>
              <svg width="20" height="20" viewBox="0 0 18 18" fill="none"><path d="M7 4l5 5-5 5" stroke="rgba(255,255,255,0.7)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/></svg>
            </button>
          )}"""
assert old_install in html, "FAIL: install button"
html = html.replace(old_install, new_install, 1)

# ── 3. Onboarding swipe support
old_onboard_func = """function OnboardingOverlay({ onDone }) {
  const [step, setStep] = React.useState(0);"""
new_onboard_func = """function OnboardingOverlay({ onDone }) {
  const [step, setStep] = React.useState(0);
  const touchStartX = React.useRef(null);
  const handleTouchStart = e => { touchStartX.current = e.touches[0].clientX; };
  const handleTouchEnd = e => {
    if (touchStartX.current === null) return;
    const dx = e.changedTouches[0].clientX - touchStartX.current;
    touchStartX.current = null;
    if (Math.abs(dx) < 40) return;
    if (dx < 0 && step < steps.length - 1) setStep(s => s + 1);
    if (dx > 0 && step > 0) setStep(s => s - 1);
  };"""
assert old_onboard_func in html, "FAIL: onboarding func"
html = html.replace(old_onboard_func, new_onboard_func, 1)

# Add touch handlers to the overlay div
old_overlay_div = "position:'fixed', top:'calc(-1 * env(safe-area-inset-top))', left:0, right:0, bottom:0, zIndex:9999, background:`linear-gradient(to bottom, ${T.bg} 0%, ${T.bgOverlay} 45%)`, display:'flex', alignItems:'flex-end', justifyContent:'center', padding:`0 16px max(40px, calc(env(safe-area-inset-bottom) + 24px))`"
new_overlay_div = "position:'fixed', top:'calc(-1 * env(safe-area-inset-top))', left:0, right:0, bottom:0, zIndex:9999, background:`linear-gradient(to bottom, ${T.bg} 0%, ${T.bgOverlay} 45%)`, display:'flex', alignItems:'flex-end', justifyContent:'center', padding:`0 16px max(40px, calc(env(safe-area-inset-bottom) + 24px))`, onTouchStart:handleTouchStart, onTouchEnd:handleTouchEnd"
assert old_overlay_div in html, "FAIL: overlay div"
html = html.replace(old_overlay_div, new_overlay_div, 1)

html = html.replace("const APP_VERSION = 'v9.348';", "const APP_VERSION = 'v9.349';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.349 — default player name, prominent install CTA, onboarding swipe")
