#!/usr/bin/env python3
"""v9.358 — Restore original 10 themes (ember/night/crimson/forest were too bold)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find and replace the current THEMES block (4 bold themes) with the original 10
themes_start_idx = html.index("const THEMES = {")
themes_end_marker = "};\n\nlet T = THEMES["
themes_end_idx = html.index(themes_end_marker) + 2  # include "};"

new_themes_block = """const THEMES = {
  warm: {
    bg: '#F4C57E',
    bgSoft: '#F8D69A',
    bgDeep: '#E8B260',
    surface: '#FFFFFF',
    surfaceMuted: '#FBEFD8',
    ink: '#1A2A4A',
    inkSoft: '#4A5878',
    inkMute: '#8A93A8',
    mint: '#4FC2A0',
    mintSoft: '#D9F1E8',
    mintDeep: '#3DA888',
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
    surfaceMuted: '#FFF4FA',
    ink: '#3A1030',
    inkSoft: '#7A4060',
    inkMute: '#B890A8',
    mint: '#E040A0',
    mintSoft: '#FFD8EE',
    mintDeep: '#C02080',
    coral: '#FF6090',
    coralSoft: '#FFD8E4',
    purple: '#C060E0',
    yellow: '#FFB830',
    blue: '#60B0F0',
    pink: '#FF80C0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(180,0,100,0.06), 0 6px 20px rgba(180,0,100,0.10)',
    shadowLift: '0 4px 0 rgba(180,0,100,0.08), 0 12px 32px rgba(180,0,100,0.15)',
    playBg: 'linear-gradient(160deg, #FFE8F4 0%, #FFD0EC 100%)',
    bgOverlay: 'rgba(95, 12, 60, 0.96)',
  },
  lavender: {
    bg: '#EEE8FF', bgSoft: '#F4F0FF', bgDeep: '#DDD0FF',
    surface: '#FFFFFF', surfaceMuted: '#F7F4FF',
    ink: '#20103A', inkSoft: '#55407A', inkMute: '#9A90B8',
    mint: '#7040E8', mintSoft: '#E4D8FF', mintDeep: '#5020C8',
    coral: '#E06080', coralSoft: '#FFD8E4',
    purple: '#A060F0', yellow: '#D0A030', blue: '#6080E0', pink: '#E080C0',
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
    surface: '#FFFFFF', surfaceMuted: '#F0FAFB',
    ink: '#0A2030', inkSoft: '#305870', inkMute: '#7098A8',
    mint: '#0090B8', mintSoft: '#C8EAF5', mintDeep: '#0070A0',
    coral: '#E07050', coralSoft: '#FFE4D8',
    purple: '#6070C8', yellow: '#E0A820', blue: '#2080C0', pink: '#C070A0',
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
    surface: '#FFFFFF', surfaceMuted: '#FFF5EE',
    ink: '#3A1808', inkSoft: '#7A4830', inkMute: '#B89080',
    mint: '#E06030', mintSoft: '#FFE0D0', mintDeep: '#C04010',
    coral: '#F08060', coralSoft: '#FFE4D8',
    purple: '#A060C0', yellow: '#E0A020', blue: '#5090D0', pink: '#E080A0',
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
    surface: '#FFFFFF', surfaceMuted: '#FFFFF0',
    ink: '#28280A', inkSoft: '#606030', inkMute: '#A0A060',
    mint: '#808010', mintSoft: '#F0F0C0', mintDeep: '#606008',
    coral: '#E06050', coralSoft: '#FFE0D8',
    purple: '#8060C0', yellow: '#D0B000', blue: '#4090C8', pink: '#D080A0',
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
    surface: '#FFFFFF', surfaceMuted: '#FFF5F2',
    ink: '#3A1008', inkSoft: '#7A4030', inkMute: '#B89088',
    mint: '#E04830', mintSoft: '#FFD8D0', mintDeep: '#C02810',
    coral: '#FF7060', coralSoft: '#FFE0DC',
    purple: '#A050C0', yellow: '#F0A020', blue: '#4090D0', pink: '#E870A0',
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
    surface: '#FFFFFF', surfaceMuted: '#F8F4FD',
    ink: '#280830', inkSoft: '#603070', inkMute: '#A080B0',
    mint: '#9030C0', mintSoft: '#ECD8F8', mintDeep: '#7010A0',
    coral: '#D05080', coralSoft: '#FFD8E8',
    purple: '#B040E0', yellow: '#C09030', blue: '#5080D0', pink: '#E060A0',
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
    surface: '#FFFFFF', surfaceMuted: '#F4FAFF',
    ink: '#0A1828', inkSoft: '#304860', inkMute: '#7090A8',
    mint: '#2070C0', mintSoft: '#D0E8FF', mintDeep: '#1050A0',
    coral: '#D06060', coralSoft: '#FFE0E0',
    purple: '#6060C8', yellow: '#C0A030', blue: '#3080D0', pink: '#C070B0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(0,40,100,0.06), 0 6px 20px rgba(0,40,100,0.10)',
    shadowLift: '0 4px 0 rgba(0,40,100,0.08), 0 12px 32px rgba(0,40,100,0.14)',
    playBg: 'linear-gradient(160deg, #E8F4FF 0%, #D0E8FF 100%)',
    bgOverlay: 'rgba(6, 22, 72, 0.96)',
  },
};"""

html = html[:themes_start_idx] + new_themes_block + html[themes_end_idx:]

# Restore default theme to 'warm'
html = html.replace("let T = THEMES[localStorage.getItem('boh_theme')] || THEMES['ember'];",
                    "let T = THEMES[localStorage.getItem('boh_theme')] || THEMES['warm'];")
html = html.replace("if (!T) T = THEMES['ember'];",
                    "if (!T) T = THEMES['warm'];")

# Restore theme picker to 5-column grid with 10 themes
old_picker = """              <div style={{ display:'grid', gridTemplateColumns:'repeat(2,1fr)', gap:10, marginBottom:24 }}>
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
assert old_picker in html, "FAIL: theme picker"

new_picker = """              <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:8, marginBottom:24 }}>
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

html = html.replace(old_picker, new_picker, 1)

html = html.replace("const APP_VERSION = 'v9.357';", "const APP_VERSION = 'v9.358';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.358 — restored original 10 themes")
