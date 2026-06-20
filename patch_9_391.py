#!/usr/bin/env python3
"""v9.391 — Splash: 3 eltűnési animáció (scale+fade, logo repül, flash reveal) + beállítás"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. CSS: exit animációk ─────────────────────────────────────────────────────
old_hidden_css = """    #splash.hidden { opacity:0; pointer-events:none; }"""

new_hidden_css = """    #splash.hidden { opacity:0; pointer-events:none; }
    /* Exit: scale+fade */
    #splash.exit-scale { transition: opacity 0.5s ease, transform 0.5s ease !important; opacity:0; transform:scale(1.18); pointer-events:none; }
    /* Exit: logo repül */
    #splash.exit-fly { pointer-events:none; }
    #splash.exit-fly #splash-logo-wrap { animation: splashFlyOut 0.55s cubic-bezier(0.4,0,1,1) forwards !important; }
    #splash.exit-fly #splash-title-wrap, #splash.exit-fly #splash-tagline { animation: splashFadeDown 0.35s ease forwards !important; }
    @keyframes splashFlyOut { to { transform: translateY(-55vh) scale(0.4); opacity:0; } }
    @keyframes splashFadeDown { to { transform: translateY(18px); opacity:0; } }
    /* Exit: flash reveal */
    #splash.exit-flash #splash-flash { animation: splashExitFlash 0.45s ease forwards !important; }
    @keyframes splashExitFlash { 0%{opacity:0} 25%{opacity:1} 100%{opacity:1} }"""

assert old_hidden_css in html, "FAIL: hidden css"
html = html.replace(old_hidden_css, new_hidden_css, 1)

# ── 2. JS: _hideSplash exit stílus szerint ────────────────────────────────────
old_hide_js = """window._hideSplash = function() {
  if (!window._splashReactReady || !window._splashTimerDone) return;
  const splash = document.getElementById('splash');
  if (splash) {
    splash.classList.add('hidden');
    setTimeout(() => { if (splash.parentNode) splash.parentNode.removeChild(splash); }, 300);
  }
};"""

new_hide_js = """window._hideSplash = function() {
  if (!window._splashReactReady || !window._splashTimerDone) return;
  const splash = document.getElementById('splash');
  if (!splash) return;
  const exitStyle = localStorage.getItem('boh_splash_exit') || 'fade';
  if (exitStyle === 'scale') {
    splash.classList.add('exit-scale');
    setTimeout(() => { if (splash.parentNode) splash.parentNode.removeChild(splash); }, 550);
  } else if (exitStyle === 'fly') {
    splash.classList.add('exit-fly');
    setTimeout(() => {
      splash.style.transition = 'opacity 0.2s ease';
      splash.style.opacity = '0';
    }, 450);
    setTimeout(() => { if (splash.parentNode) splash.parentNode.removeChild(splash); }, 700);
  } else if (exitStyle === 'flash') {
    const flash = document.getElementById('splash-flash');
    if (flash) flash.style.animation = 'splashExitFlash 0.45s ease forwards';
    setTimeout(() => { if (splash.parentNode) splash.parentNode.removeChild(splash); }, 450);
  } else {
    splash.classList.add('hidden');
    setTimeout(() => { if (splash.parentNode) splash.parentNode.removeChild(splash); }, 300);
  }
};"""

assert old_hide_js in html, "FAIL: hide js"
html = html.replace(old_hide_js, new_hide_js, 1)

# ── 3. HomeScreen: splashExit state ───────────────────────────────────────────
old_state = """  const [splashOn, setSplashOn] = React.useState(() => localStorage.getItem('boh_splash') !== '0');
  const toggleSplash = () => {
    const next = !splashOn;
    setSplashOn(next);
    try { localStorage.setItem('boh_splash', next ? '1' : '0'); } catch(e) {}
  };"""

new_state = """  const [splashOn, setSplashOn] = React.useState(() => localStorage.getItem('boh_splash') !== '0');
  const toggleSplash = () => {
    const next = !splashOn;
    setSplashOn(next);
    try { localStorage.setItem('boh_splash', next ? '1' : '0'); } catch(e) {}
  };
  const [splashExit, setSplashExit] = React.useState(() => localStorage.getItem('boh_splash_exit') || 'fade');
  const setSplashExitStyle = (key) => {
    setSplashExit(key);
    try { localStorage.setItem('boh_splash_exit', key); } catch(e) {}
  };"""

assert old_state in html, "FAIL: state"
html = html.replace(old_state, new_state, 1)

# ── 4. Settings UI: eltűnési stílus választó ──────────────────────────────────
old_settings_end = """                <Toggle on={splashOn} onChange={toggleSplash} />
              </div>

            </div>
          </SheetOverlay>"""

new_settings_end = """                <Toggle on={splashOn} onChange={toggleSplash} />
              </div>
              {splashOn && (<>
                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginTop:16, marginBottom:8 }}>Eltűnési animáció</div>
                <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
                  {[
                    ['fade','Fade','Egyszerű átfakulás'],
                    ['scale','Scale + Fade','Kinő és elfakul'],
                    ['fly','Logó felrepül','Logo felfelé repül, szöveg eltűnik'],
                    ['flash','Flash → Reveal','Fehér villanás, azonnali megjelenés'],
                  ].map(([key, label, sub]) => (
                    <button key={key} onClick={() => setSplashExitStyle(key)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 14px', borderRadius:14, border: splashExit===key ? '2px solid '+T.mint : '2px solid transparent', background: splashExit===key ? T.mintSoft : T.surfaceMuted, cursor:'pointer', textAlign:'left' }}>
                      <div style={{ flex:1 }}>
                        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color: splashExit===key ? T.mintDeep : T.ink }}>{label}</div>
                        <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:1 }}>{sub}</div>
                      </div>
                      {splashExit===key && <span style={{ color:T.mint, fontSize:16 }}>✓</span>}
                    </button>
                  ))}
                </div>
              </>)}

            </div>
          </SheetOverlay>"""

assert old_settings_end in html, "FAIL: settings ui"
html = html.replace(old_settings_end, new_settings_end, 1)

html = html.replace("const APP_VERSION = 'v9.390';", "const APP_VERSION = 'v9.391';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.391 — 3 eltűnési animáció implementálva + beállítás")
