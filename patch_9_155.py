#!/usr/bin/env python3
"""patch_9_155.py — Beállítások: splash screen toggle + splash ellenőrzi localStorage"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.154';" in content
content = content.replace("const APP_VERSION = 'v9.154';", "const APP_VERSION = 'v9.155';")

# ── 1. Splash screen: ellenőrizze a localStorage-t, ha ki van kapcsolva ne jelenjen meg ──
OLD_SPLASH_DIV = """<div id="splash">
  <div id="splash-bg"></div>"""

NEW_SPLASH_DIV = """<div id="splash" style="display:none">
  <div id="splash-bg"></div>"""

assert OLD_SPLASH_DIV in content, "splash div not found"
content = content.replace(OLD_SPLASH_DIV, NEW_SPLASH_DIV, 1)

# A splash theme script után adjuk hozzá a toggle ellenőrzést
OLD_SPLASH_SCRIPT_END = """})();
</script>
<!-- iOS 18+ haptic trigger -->"""

NEW_SPLASH_SCRIPT_END = """  // Ha splash ki van kapcsolva, ne jelenjen meg
  var splashEnabled = localStorage.getItem('boh_splash') !== '0';
  if (splashEnabled) {
    splash.style.display = '';
  }
})();
</script>
<!-- iOS 18+ haptic trigger -->"""

assert OLD_SPLASH_SCRIPT_END in content, "splash script end not found"
content = content.replace(OLD_SPLASH_SCRIPT_END, NEW_SPLASH_SCRIPT_END, 1)

# ── 2. Beállítások oldalon: splash toggle state + UI ──
OLD_SETTINGS_STATE = "function HomeScreen({ go, onStartGame, setTheme, currentTheme, setLang, currentLang, resumeRoomData, onResume }) {"

NEW_SETTINGS_STATE = """function HomeScreen({ go, onStartGame, setTheme, currentTheme, setLang, currentLang, resumeRoomData, onResume }) {
  const [splashOn, setSplashOn] = React.useState(() => localStorage.getItem('boh_splash') !== '0');
  const toggleSplash = () => {
    const next = !splashOn;
    setSplashOn(next);
    localStorage.setItem('boh_splash', next ? '1' : '0');
  };"""

assert OLD_SETTINGS_STATE in content, "HomeScreen not found"
content = content.replace(OLD_SETTINGS_STATE, NEW_SETTINGS_STATE, 1)

# ── 3. Splash toggle UI a beállítások panelben, a Language után ──
OLD_LANG_END = """              <div style={{ display:'flex', gap:8 }}>
                {[['hu',t('langHu')],['en',t('langEn')]].map(([key, label]) => (
                  <button key={key} onClick={() => { setLang && setLang(key); }} style={{ flex:1, padding:'12px 8px', borderRadius:14, border: currentLang===key ? `2px solid ${T.mint}` : `2px solid transparent`, background: currentLang===key ? T.mintSoft : T.surfaceMuted, cursor:'pointer', fontFamily:T.font, fontWeight:700, fontSize:13, color: currentLang===key ? T.mintDeep : T.inkSoft }}>
                    {label}
                  </button>
                ))}
              </div>
            </div>
          </SheetOverlay>"""

NEW_LANG_END = """              <div style={{ display:'flex', gap:8 }}>
                {[['hu',t('langHu')],['en',t('langEn')]].map(([key, label]) => (
                  <button key={key} onClick={() => { setLang && setLang(key); }} style={{ flex:1, padding:'12px 8px', borderRadius:14, border: currentLang===key ? `2px solid ${T.mint}` : `2px solid transparent`, background: currentLang===key ? T.mintSoft : T.surfaceMuted, cursor:'pointer', fontFamily:T.font, fontWeight:700, fontSize:13, color: currentLang===key ? T.mintDeep : T.inkSoft }}>
                    {label}
                  </button>
                ))}
              </div>
              {/* Splash screen toggle */}
              <div style={{ width:1, background:T.inkMute+'25', margin:'20px 0' }} />
              <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
                <div>
                  <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>Splash screen</div>
                  <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>Betöltési animáció indításkor</div>
                </div>
                <div onClick={toggleSplash} style={{ width:48, height:28, borderRadius:14, background: splashOn ? T.mint : T.surfaceMuted, position:'relative', cursor:'pointer', flexShrink:0, transition:'background .2s' }}>
                  <div style={{ position:'absolute', top:3, left: splashOn ? 23 : 3, width:22, height:22, borderRadius:'50%', background:'#fff', boxShadow:'0 1px 3px rgba(0,0,0,0.2)', transition:'left .2s' }}/>
                </div>
              </div>
            </div>
          </SheetOverlay>"""

assert OLD_LANG_END in content, "lang end not found"
content = content.replace(OLD_LANG_END, NEW_LANG_END, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.155 ready")
