#!/usr/bin/env python3
"""v9.357 — Fix onboarding swipe (handlers inside style obj bug) + 4 bold themes"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Fix swipe: move onTouchStart/onTouchEnd OUT of style={{}} to JSX props
old_overlay = "<div style={{ position:'fixed', top:'calc(-1 * env(safe-area-inset-top))', left:0, right:0, bottom:0, zIndex:9999, background:`linear-gradient(to bottom, ${T.bg} 0%, ${T.bgOverlay} 45%)`, display:'flex', alignItems:'flex-end', justifyContent:'center', padding:`0 16px max(40px, calc(env(safe-area-inset-bottom) + 24px))`, onTouchStart:handleTouchStart, onTouchEnd:handleTouchEnd }}>"
new_overlay = "<div onTouchStart={handleTouchStart} onTouchEnd={handleTouchEnd} style={{ position:'fixed', top:'calc(-1 * env(safe-area-inset-top))', left:0, right:0, bottom:0, zIndex:9999, background:`linear-gradient(to bottom, ${T.bg} 0%, ${T.bgOverlay} 45%)`, display:'flex', alignItems:'flex-end', justifyContent:'center', padding:`0 16px max(40px, calc(env(safe-area-inset-bottom) + 24px))` }}>"
assert old_overlay in html, "FAIL: overlay div"
html = html.replace(old_overlay, new_overlay, 1)

# ── 2. Replace 10 soft themes with 4 bold themes
# New themes: ember (deep orange), night (dark navy), crimson (bold red), forest (deep green)
old_themes = """const THEMES = {
  warm: {
    bg: '#F4C57E',
    bgSoft: '#F8D69A',
    bgDeep: '#E8B260',
    surface: '#FFFFFF',
    surfaceMuted: '#FBEFD8',
    ink: '#1A2A4A',"""

new_themes = """const THEMES = {
  ember: {
    bg: '#E07820',
    bgSoft: '#E88A38',
    bgDeep: '#C05E10',
    surface: '#FFFFFF',
    surfaceMuted: '#FBE8D0',
    ink: '#1A0E00',"""

assert old_themes in html, "FAIL: themes start"
html = html.replace(old_themes, new_themes, 1)

# Fix warm references in rest of warm theme definition
old_warm_rest = """    mintDeep: '#3DA888',
    coral: '#F2A0A0',
    coralSoft: '#FBDADA',
    purple: '#A88AE8',
    yellow: '#F4C95A',
    blue: '#5BA0DB',
    pink: '#E985B8',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900,
    weightTitle: 800,
    weightBody: 600,
    letter: '-0.01em',
    letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(20,30,50,0.04), 0 6px 20px rgba(20,30,50,0.06)',
    shadowLift: '0 4px 0 rgba(20,30,50,0.06), 0 12px 32px rgba(20,30,50,0.10)',
    playBg: 'linear-gradient(160deg, #F4C57E 0%, #EDAF58 100%)',
    bgOverlay: 'rgba(75, 42, 5, 0.96)',
  },
  dark: {
    bg: '#2C3554',
    bgSoft: '#36405F',
    bgDeep: '#1E2640',
    surface: '#3D4870',
    surfaceMuted: '#333D60',
    ink: '#EDF1FB',
    inkSoft: '#C4CCDF',
    inkMute: '#8C98C0',
    mint: '#4FC2A0',
    mintSoft: '#1A3D35',
    mintDeep: '#3DA888',
    coral: '#F28080',
    coralSoft: '#3D1A1A',
    purple: '#A88AE8',
    yellow: '#F4C95A',
    blue: '#5BA0DB',
    pink: '#E985B8',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900,
    weightTitle: 800,
    weightBody: 600,
    letter: '-0.01em',
    letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(0,0,0,0.2), 0 6px 20px rgba(0,0,0,0.3)',
    shadowLift: '0 4px 0 rgba(0,0,0,0.25), 0 12px 32px rgba(0,0,0,0.4)',
    playBg: 'linear-gradient(160deg, #2C3554 0%, #1A2040 100%)',
    bgOverlay: 'rgba(10, 14, 28, 0.97)',
  },
  candy: {
    bg: '#FFE8F4',
    bgSoft: '#FFF0F8',
    bgDeep: '#FFD0EC',
    surface: '#FFFFFF',
    surfaceMuted: '#FFF0F8',
    ink: '#3A0A28',
    inkSoft: '#8C4070',
    inkMute: '#C080A8',
    mint: '#E040A0',
    mintSoft: '#FFD0EC',
    mintDeep: '#B02070',
    coral: '#FF6080',
    coralSoft: '#FFD0D8',
    purple: '#C060E0',
    yellow: '#FFB020',
    blue: '#6080FF',
    pink: '#FF60A0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900,
    weightTitle: 800,
    weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(180,0,100,0.06), 0 6px 20px rgba(180,0,100,0.10)',
    shadowLift: '0 4px 0 rgba(180,0,100,0.08), 0 12px 32px rgba(180,0,100,0.15)',
    playBg: 'linear-gradient(160deg, #FFE8F4 0%, #FFD0EC 100%)',
    bgOverlay: 'rgba(95, 12, 60, 0.96)',
  },
  lavender: {
    bg: '#EEE8FF', bgSoft: '#F4F0FF', bgDeep: '#DDD0FF',
    surface: '#FFFFFF', surfaceMuted: '#F4F0FF',
    ink: '#1A0A40', inkSoft: '#5040A0', inkMute: '#9080C8',
    mint: '#6040D0', mintSoft: '#E0D8FF', mintDeep: '#4020A0',
    coral: '#E04060', coralSoft: '#FFD0D8', purple: '#8040E0',
    yellow: '#C0A020', blue: '#2060E0', pink: '#E040A0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(60,0,180,0.05), 0 6px 20px rgba(60,0,180,0.09)',
    shadowLift: '0 4px 0 rgba(60,0,180,0.07), 0 12px 32px rgba(60,0,180,0.13)',
    playBg: 'linear-gradient(160deg, #EEE8FF 0%, #DDD0FF 100%)',
    bgOverlay: 'rgba(32, 12, 88, 0.96)',
  },
  ocean: {
    bg: '#E0F4F8', bgSoft: '#ECF8FC', bgDeep: '#C8EAF2',
    surface: '#FFFFFF', surfaceMuted: '#ECF8FC',
    ink: '#001830', inkSoft: '#205878', inkMute: '#6098B8',
    mint: '#0098B8', mintSoft: '#C8EAF2', mintDeep: '#006888',
    coral: '#E04040', coralSoft: '#FFD8D8', purple: '#4060E0',
    yellow: '#E0A020', blue: '#0060D0', pink: '#E040A0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(0,60,100,0.06), 0 6px 20px rgba(0,60,100,0.10)',
    shadowLift: '0 4px 0 rgba(0,60,100,0.08), 0 12px 32px rgba(0,60,100,0.14)',
    playBg: 'linear-gradient(160deg, #E0F4F8 0%, #C0E8F4 100%)',
    bgOverlay: 'rgba(6, 42, 62, 0.96)',
  },
  peach: {
    bg: '#FFE8D8', bgSoft: '#FFF0E8', bgDeep: '#FFD8C0',
    surface: '#FFFFFF', surfaceMuted: '#FFF0E8',
    ink: '#280800', inkSoft: '#784020', inkMute: '#C08060',
    mint: '#E06020', mintSoft: '#FFD8C0', mintDeep: '#A03000',
    coral: '#E02020', coralSoft: '#FFD0D0', purple: '#8040C0',
    yellow: '#E0A020', blue: '#2060C0', pink: '#E04080',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(160,60,0,0.06), 0 6px 20px rgba(160,60,0,0.10)',
    shadowLift: '0 4px 0 rgba(160,60,0,0.08), 0 12px 32px rgba(160,60,0,0.14)',
    playBg: 'linear-gradient(160deg, #FFE8D8 0%, #FFD0BC 100%)',
    bgOverlay: 'rgba(88, 32, 6, 0.96)',
  },
  lemon: {
    bg: '#F8F8D8', bgSoft: '#FFFCE8', bgDeep: '#F0F0B8',
    surface: '#FFFFFF', surfaceMuted: '#FFFCE8',
    ink: '#181800', inkSoft: '#585800', inkMute: '#989840',
    mint: '#888000', mintSoft: '#F0F0B8', mintDeep: '#585800',
    coral: '#C02020', coralSoft: '#FFD0D0', purple: '#6040B0',
    yellow: '#B08000', blue: '#2060B0', pink: '#C04080',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(80,80,0,0.06), 0 6px 20px rgba(80,80,0,0.10)',
    shadowLift: '0 4px 0 rgba(80,80,0,0.08), 0 12px 32px rgba(80,80,0,0.14)',
    playBg: 'linear-gradient(160deg, #F8F8D8 0%, #ECECA8 100%)',
    bgOverlay: 'rgba(52, 52, 6, 0.96)',
  },
  coraltheme: {
    bg: '#FFE8E0', bgSoft: '#FFF0EC', bgDeep: '#FFD8CC',
    surface: '#FFFFFF', surfaceMuted: '#FFF0EC',
    ink: '#280000', inkSoft: '#802020', inkMute: '#C07060',
    mint: '#E02040', mintSoft: '#FFD0D8', mintDeep: '#A00020',
    coral: '#E04020', coralSoft: '#FFD0C8', purple: '#8020C0',
    yellow: '#C08000', blue: '#2040C0', pink: '#E04080',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(180,40,0,0.06), 0 6px 20px rgba(180,40,0,0.10)',
    shadowLift: '0 4px 0 rgba(180,40,0,0.08), 0 12px 32px rgba(180,40,0,0.14)',
    playBg: 'linear-gradient(160deg, #FFE8E0 0%, #FFCCC0 100%)',
    bgOverlay: 'rgba(105, 22, 12, 0.96)',
  },
  berry: {
    bg: '#F0E8F8', bgSoft: '#F6F0FC', bgDeep: '#E0D0F0',
    surface: '#FFFFFF', surfaceMuted: '#F6F0FC',
    ink: '#180028', inkSoft: '#602080', inkMute: '#A070C0',
    mint: '#8020C0', mintSoft: '#E0D0F0', mintDeep: '#500080',
    coral: '#E02060', coralSoft: '#FFD0DC', purple: '#6020A0',
    yellow: '#C09000', blue: '#2040C0', pink: '#E040C0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(100,0,160,0.06), 0 6px 20px rgba(100,0,160,0.10)',
    shadowLift: '0 4px 0 rgba(100,0,160,0.08), 0 12px 32px rgba(100,0,160,0.14)',
    playBg: 'linear-gradient(160deg, #F0E8F8 0%, #DDD0F0 100%)',
    bgOverlay: 'rgba(50, 6, 85, 0.96)',
  },
  ice: {
    bg: '#E8F4FF', bgSoft: '#F0F8FF', bgDeep: '#D0E8FF',
    surface: '#FFFFFF', surfaceMuted: '#F0F8FF',
    ink: '#001028', inkSoft: '#204870', inkMute: '#6090B8',
    mint: '#0060C0', mintSoft: '#D0E8FF', mintDeep: '#003890',
    coral: '#E02040', coralSoft: '#FFD0D8', purple: '#6030C0',
    yellow: '#C09000', blue: '#0040B0', pink: '#E040A0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(0,40,100,0.06), 0 6px 20px rgba(0,40,100,0.10)',
    shadowLift: '0 4px 0 rgba(0,40,100,0.08), 0 12px 32px rgba(0,40,100,0.14)',
    playBg: 'linear-gradient(160deg, #E8F4FF 0%, #D0E8FF 100%)',
    bgOverlay: 'rgba(6, 22, 72, 0.96)',
  },
};"""

new_warm_rest = """    mintDeep: '#C06010',
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
    mint: '#FF4060',
    mintSoft: '#FFD0D8',
    mintDeep: '#C00020',
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

assert old_warm_rest in html, "FAIL: old themes body"
html = html.replace(old_warm_rest, new_warm_rest, 1)

# ── 3. Update default theme reference and localStorage fallback
html = html.replace("let T = THEMES[localStorage.getItem('boh_theme')] || THEMES['warm'];",
                    "let T = THEMES[localStorage.getItem('boh_theme')] || THEMES['ember'];")
html = html.replace("if (!T) T = THEMES['warm'];",
                    "if (!T) T = THEMES['ember'];")

# ── 4. Update theme picker: 4 themes, 2x2 grid, bigger buttons with color swatches
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

new_picker = """              <div style={{ display:'grid', gridTemplateColumns:'repeat(2,1fr)', gap:10, marginBottom:24 }}>
                {[
                  ['ember','#E07820','#C05E10','🔥','Ember'],
                  ['night','#1A2040','#0E1428','🌙','Night'],
                  ['crimson','#C01030','#900820','❤️','Crimson'],
                  ['forest','#0D5C3A','#084028','🌿','Forest'],
                ].map(([key, c1, c2, icon, label]) => (
                  <button key={key} onClick={() => { setTheme && setTheme(key); }} style={{ padding:'14px 16px', borderRadius:16, border: currentTheme===key ? `2.5px solid ${T.mint}` : `2px solid transparent`, background:`linear-gradient(135deg, ${c1} 0%, ${c2} 100%)`, cursor:'pointer', display:'flex', alignItems:'center', gap:12, boxShadow: currentTheme===key ? `0 0 0 3px ${T.mint}44, 0 4px 16px ${c2}55` : `0 2px 8px ${c2}44` }}>
                    <span style={{ fontSize:24 }}>{icon}</span>
                    <span style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:'#fff', textShadow:'0 1px 4px rgba(0,0,0,0.3)' }}>{label}</span>
                    {currentTheme===key && <span style={{ marginLeft:'auto', fontSize:16 }}>✓</span>}
                  </button>
                ))}
              </div>"""

assert old_picker in html, "FAIL: theme picker"
html = html.replace(old_picker, new_picker, 1)

html = html.replace("const APP_VERSION = 'v9.356';", "const APP_VERSION = 'v9.357';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.357 — swipe fixed, 4 bold themes (ember/night/crimson/forest)")
