#!/usr/bin/env python3
"""v9.357 — Fix onboarding swipe + 4 bold themes (ember/night/crimson/forest)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Fix swipe: move touch handlers out of style object
old_overlay = "<div style={{ position:'fixed', top:'calc(-1 * env(safe-area-inset-top))', left:0, right:0, bottom:0, zIndex:9999, background:`linear-gradient(to bottom, ${T.bg} 0%, ${T.bgOverlay} 45%)`, display:'flex', alignItems:'flex-end', justifyContent:'center', padding:`0 16px max(40px, calc(env(safe-area-inset-bottom) + 24px))`, onTouchStart:handleTouchStart, onTouchEnd:handleTouchEnd }}>"
new_overlay = "<div onTouchStart={handleTouchStart} onTouchEnd={handleTouchEnd} style={{ position:'fixed', top:'calc(-1 * env(safe-area-inset-top))', left:0, right:0, bottom:0, zIndex:9999, background:`linear-gradient(to bottom, ${T.bg} 0%, ${T.bgOverlay} 45%)`, display:'flex', alignItems:'flex-end', justifyContent:'center', padding:`0 16px max(40px, calc(env(safe-area-inset-bottom) + 24px))` }}>"
assert old_overlay in html, "FAIL: overlay swipe fix"
html = html.replace(old_overlay, new_overlay, 1)

# ── 2. Replace entire THEMES object with 4 bold themes
old_themes_start = "const THEMES = {\n  warm: {"
assert old_themes_start in html, "FAIL: THEMES start"

# Find the full THEMES block end
themes_end_marker = "};\n\nlet T = THEMES["
assert themes_end_marker in html, "FAIL: THEMES end"

themes_start_idx = html.index("const THEMES = {")
themes_end_idx = html.index(themes_end_marker) + 2  # include "};"

old_themes_block = html[themes_start_idx:themes_end_idx]

new_themes_block = """const THEMES = {
  ember: {
    bg: '#E07820',
    bgSoft: '#E88830',
    bgDeep: '#C05E10',
    surface: '#FFFFFF',
    surfaceMuted: '#FFF0E0',
    ink: '#1A0800',
    inkSoft: '#7A3010',
    inkMute: '#C08050',
    mint: '#4FC2A0',
    mintSoft: '#D8F4EC',
    mintDeep: '#3DA888',
    coral: '#E03020',
    coralSoft: '#FFD0C8',
    purple: '#7040D0',
    yellow: '#D09000',
    blue: '#2050C0',
    pink: '#D04080',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900,
    weightTitle: 800,
    weightBody: 600,
    letter: '-0.01em',
    letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(60,20,0,0.08), 0 6px 20px rgba(60,20,0,0.14)',
    shadowLift: '0 4px 0 rgba(60,20,0,0.12), 0 12px 32px rgba(60,20,0,0.18)',
    playBg: 'linear-gradient(160deg, #E07820 0%, #C05E10 100%)',
    bgOverlay: 'rgba(80, 30, 0, 0.96)',
  },
  night: {
    bg: '#1A2040',
    bgSoft: '#222A50',
    bgDeep: '#0E1428',
    surface: '#2A3460',
    surfaceMuted: '#222A50',
    ink: '#EDF1FF',
    inkSoft: '#9AAACE',
    inkMute: '#5A6A9A',
    mint: '#4FC2A0',
    mintSoft: '#1A3D35',
    mintDeep: '#3DA888',
    coral: '#FF5252',
    coralSoft: '#3D1A1A',
    purple: '#B080FF',
    yellow: '#FFD040',
    blue: '#60A0FF',
    pink: '#FF60B0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900,
    weightTitle: 800,
    weightBody: 600,
    letter: '-0.01em',
    letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(0,0,0,0.3), 0 6px 20px rgba(0,0,0,0.4)',
    shadowLift: '0 4px 0 rgba(0,0,0,0.4), 0 12px 32px rgba(0,0,0,0.5)',
    playBg: 'linear-gradient(160deg, #1A2040 0%, #0E1428 100%)',
    bgOverlay: 'rgba(6, 8, 18, 0.98)',
  },
  crimson: {
    bg: '#C01030',
    bgSoft: '#D01840',
    bgDeep: '#900820',
    surface: '#FFFFFF',
    surfaceMuted: '#FFE8EC',
    ink: '#1A0008',
    inkSoft: '#801020',
    inkMute: '#C06070',
    mint: '#FF8040',
    mintSoft: '#FFE0D0',
    mintDeep: '#D05010',
    coral: '#FF6020',
    coralSoft: '#FFD8C8',
    purple: '#8020C0',
    yellow: '#FFD020',
    blue: '#2040C0',
    pink: '#FF40A0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900,
    weightTitle: 800,
    weightBody: 600,
    letter: '-0.01em',
    letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(100,0,20,0.15), 0 6px 20px rgba(100,0,20,0.25)',
    shadowLift: '0 4px 0 rgba(100,0,20,0.2), 0 12px 32px rgba(100,0,20,0.35)',
    playBg: 'linear-gradient(160deg, #C01030 0%, #900820 100%)',
    bgOverlay: 'rgba(60, 0, 12, 0.97)',
  },
  forest: {
    bg: '#0D5C3A',
    bgSoft: '#126846',
    bgDeep: '#084028',
    surface: '#FFFFFF',
    surfaceMuted: '#D0F0E0',
    ink: '#001A0E',
    inkSoft: '#206040',
    inkMute: '#60A080',
    mint: '#20C060',
    mintSoft: '#C0F0D8',
    mintDeep: '#108040',
    coral: '#FF5030',
    coralSoft: '#FFD8D0',
    purple: '#8040D0',
    yellow: '#E0C020',
    blue: '#2060D0',
    pink: '#E04080',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900,
    weightTitle: 800,
    weightBody: 600,
    letter: '-0.01em',
    letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(0,40,20,0.15), 0 6px 20px rgba(0,40,20,0.25)',
    shadowLift: '0 4px 0 rgba(0,40,20,0.2), 0 12px 32px rgba(0,40,20,0.35)',
    playBg: 'linear-gradient(160deg, #0D5C3A 0%, #084028 100%)',
    bgOverlay: 'rgba(2, 20, 10, 0.97)',
  },
};"""

html = html[:themes_start_idx] + new_themes_block + html[themes_end_idx:]

# ── 3. Update default theme reference
html = html.replace("let T = THEMES[localStorage.getItem('boh_theme')] || THEMES['warm'];",
                    "let T = THEMES[localStorage.getItem('boh_theme')] || THEMES['ember'];")
html = html.replace("if (!T) T = THEMES['warm'];",
                    "if (!T) T = THEMES['ember'];")

# ── 4. Update theme picker: 4 themes, 2x2 grid
old_picker = """              <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:8, marginBottom:24 }}>
                {[
                  ['warm','☀️','Meleg'],['dark','🌙','Sötét'],['candy','🍬','Candy'],['lavender','💜','Lavender'],['ocean','🌊','Ocean'],
                  ['peach','🍑','Peach'],['lemon','🍋','Citrom'],['coraltheme','🌺','Coral'],['berry','🫐','Berry'],['ice','🩵','Ice'],
                ].map(([key, icon, label]) => (
                  <button key={key} onClick={() => { setTheme && setTheme(key); }} style={{ padding:'10px 4px', borderRadius:14, border: currentTheme===key ? `2px solid ${T.mint}` : `2px solid transparent`, background: currentTheme===key ? T.mintSoft : T.surfaceMuted, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>
                    <span style={{ fontSize:20 }}>{icon}</span>
                    <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color: currentTheme===key ? T.mintDeep : T.inkSoft }}>{label}</span>
                  </button>
                ))}
              </div>"""
assert old_picker in html, "FAIL: theme picker"

new_picker = """              <div style={{ display:'grid', gridTemplateColumns:'repeat(2,1fr)', gap:10, marginBottom:24 }}>
                {[
                  ['ember','🔥','Parázs','#E07820','#C05E10'],
                  ['night','🌙','Éjszaka','#1A2040','#0E1428'],
                  ['crimson','🩸','Karmazsin','#C01030','#900820'],
                  ['forest','🌿','Erdő','#0D5C3A','#084028'],
                ].map(([key, icon, label, c1, c2]) => (
                  <button key={key} onClick={() => { setTheme && setTheme(key); }} style={{ padding:'16px 12px', borderRadius:18, border: currentTheme===key ? '3px solid #fff' : '3px solid transparent', background:`linear-gradient(135deg, ${c1} 0%, ${c2} 100%)`, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', gap:6, boxShadow: currentTheme===key ? `0 0 0 2px ${c1}, 0 6px 20px ${c1}66` : '0 2px 8px rgba(0,0,0,0.2)' }}>
                    <span style={{ fontSize:26 }}>{icon}</span>
                    <span style={{ fontFamily:'Nunito, system-ui, sans-serif', fontWeight:800, fontSize:13, color:'#fff', textShadow:'0 1px 4px rgba(0,0,0,0.4)' }}>{label}</span>
                    {currentTheme===key && <div style={{ width:20, height:20, borderRadius:'50%', background:'rgba(255,255,255,0.9)', display:'grid', placeItems:'center' }}><svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 6l3 3 5-5" stroke={c1} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg></div>}
                  </button>
                ))}
              </div>"""

html = html.replace(old_picker, new_picker, 1)

html = html.replace("const APP_VERSION = 'v9.356';", "const APP_VERSION = 'v9.357';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.357 — swipe fixed, 4 bold themes (ember/night/crimson/forest)")
