#!/usr/bin/env python3
"""v9.360 — Remove 8 unwanted themes, add 5 new ones with visual separator in picker"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Remove 8 unwanted themes from THEMES object
# Remove: wine, teal, plum, indigo, ember, midnight, crimson, coraltheme

to_remove = [
    # wine
    """  wine: {
    bg: '#6E1A3A', bgSoft: '#821E46', bgDeep: '#4E0E28',
    surface: '#FFF2F6', surfaceMuted: '#FFD8E4',
    ink: '#1A0008', inkSoft: '#6A1030', inkMute: '#B06080',
    mint: '#F060A0', mintSoft: '#FFD8EC', mintDeep: '#C03070',
    coral: '#FF6040', coralSoft: '#FFD8D0',
    purple: '#A040C0', yellow: '#F0B020', blue: '#4080D0', pink: '#FF80C0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(60,0,24,0.15), 0 6px 20px rgba(60,0,24,0.25)',
    shadowLift: '0 4px 0 rgba(60,0,24,0.20), 0 12px 32px rgba(60,0,24,0.35)',
    playBg: 'linear-gradient(160deg, #6E1A3A 0%, #4E0E28 100%)',
    bgOverlay: 'rgba(28, 4, 12, 0.98)',
  },
""",
    # teal
    """  teal: {
    bg: '#0A4A50', bgSoft: '#0E5860', bgDeep: '#063038',
    surface: '#F0FEFF', surfaceMuted: '#C0EEF2',
    ink: '#001416', inkSoft: '#105860', inkMute: '#40909A',
    mint: '#20D8C0', mintSoft: '#B0F0E8', mintDeep: '#10B0A0',
    coral: '#FF5040', coralSoft: '#FFD0C8',
    purple: '#7040D0', yellow: '#E0C010', blue: '#2080D0', pink: '#E040A0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(0,30,34,0.18), 0 6px 20px rgba(0,30,34,0.28)',
    shadowLift: '0 4px 0 rgba(0,30,34,0.24), 0 12px 32px rgba(0,30,34,0.38)',
    playBg: 'linear-gradient(160deg, #0A4A50 0%, #063038 100%)',
    bgOverlay: 'rgba(2, 12, 14, 0.98)',
  },
""",
    # plum
    """  plum: {
    bg: '#3A0E5E', bgSoft: '#481272', bgDeep: '#260840',
    surface: '#FDF2FF', surfaceMuted: '#EAD0FF',
    ink: '#0E001A', inkSoft: '#5A2080', inkMute: '#A060C0',
    mint: '#D060F0', mintSoft: '#F0D0FF', mintDeep: '#A030C0',
    coral: '#FF5050', coralSoft: '#FFD0D0',
    purple: '#E080FF', yellow: '#F0C030', blue: '#5080F0', pink: '#FF70C0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(40,0,70,0.18), 0 6px 20px rgba(40,0,70,0.28)',
    shadowLift: '0 4px 0 rgba(40,0,70,0.24), 0 12px 32px rgba(40,0,70,0.38)',
    playBg: 'linear-gradient(160deg, #3A0E5E 0%, #260840 100%)',
    bgOverlay: 'rgba(10, 2, 18, 0.98)',
  },
""",
    # indigo
    """  indigo: {
    bg: '#2A1A6E', bgSoft: '#341E88', bgDeep: '#180E4C',
    surface: '#F4F0FF', surfaceMuted: '#DDD8FF',
    ink: '#0A0420', inkSoft: '#4030A0', inkMute: '#8070C8',
    mint: '#60D0F0', mintSoft: '#C8F0FF', mintDeep: '#30A8D0',
    coral: '#FF5060', coralSoft: '#FFD0D4',
    purple: '#C080FF', yellow: '#FFD040', blue: '#60A0FF', pink: '#FF60C0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(20,0,80,0.18), 0 6px 20px rgba(20,0,80,0.28)',
    shadowLift: '0 4px 0 rgba(20,0,80,0.24), 0 12px 32px rgba(20,0,80,0.38)',
    playBg: 'linear-gradient(160deg, #2A1A6E 0%, #180E4C 100%)',
    bgOverlay: 'rgba(8, 4, 28, 0.98)',
  },
""",
    # ember
    """  ember: {
    bg: '#C4580A', bgSoft: '#D46510', bgDeep: '#943E06',
    surface: '#FFF8F2', surfaceMuted: '#FFE8D0',
    ink: '#1A0800', inkSoft: '#6A2808', inkMute: '#B06030',
    mint: '#4FC2A0', mintSoft: '#D0F0E4', mintDeep: '#3DA888',
    coral: '#FF4020', coralSoft: '#FFD0C0',
    purple: '#8040D0', yellow: '#F0C000', blue: '#2060C0', pink: '#E04080',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(80,20,0,0.12), 0 6px 20px rgba(80,20,0,0.20)',
    shadowLift: '0 4px 0 rgba(80,20,0,0.16), 0 12px 32px rgba(80,20,0,0.28)',
    playBg: 'linear-gradient(160deg, #C4580A 0%, #943E06 100%)',
    bgOverlay: 'rgba(50, 15, 0, 0.97)',
  },
""",
    # midnight
    """  midnight: {
    bg: '#0E1428', bgSoft: '#162040', bgDeep: '#080C18',
    surface: '#1E2A50', surfaceMuted: '#162040',
    ink: '#E8EEFF', inkSoft: '#8A9AC8', inkMute: '#4A5A88',
    mint: '#4FC2A0', mintSoft: '#0E2820', mintDeep: '#3DA888',
    coral: '#FF5050', coralSoft: '#2A0E0E',
    purple: '#A070FF', yellow: '#FFD030', blue: '#50A0FF', pink: '#FF60B0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(0,0,0,0.4), 0 6px 20px rgba(0,0,0,0.5)',
    shadowLift: '0 4px 0 rgba(0,0,0,0.5), 0 12px 32px rgba(0,0,0,0.6)',
    playBg: 'linear-gradient(160deg, #0E1428 0%, #080C18 100%)',
    bgOverlay: 'rgba(2, 4, 10, 0.99)',
  },
""",
    # crimson
    """  crimson: {
    bg: '#9C0820', bgSoft: '#B00A26', bgDeep: '#700418',
    surface: '#FFF2F4', surfaceMuted: '#FFD8DE',
    ink: '#1A0006', inkSoft: '#700018', inkMute: '#C05060',
    mint: '#FF8040', mintSoft: '#FFE4D0', mintDeep: '#D05010',
    coral: '#FF4040', coralSoft: '#FFD0D0',
    purple: '#9030C0', yellow: '#FFD020', blue: '#3060C0', pink: '#FF50A0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(80,0,16,0.15), 0 6px 20px rgba(80,0,16,0.25)',
    shadowLift: '0 4px 0 rgba(80,0,16,0.2), 0 12px 32px rgba(80,0,16,0.35)',
    playBg: 'linear-gradient(160deg, #9C0820 0%, #700418 100%)',
    bgOverlay: 'rgba(40, 0, 8, 0.98)',
  },
""",
    # coraltheme
    """  coraltheme: {
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
""",
]

for block in to_remove:
    assert block in html, f"FAIL removing theme block starting: {block[:40]}"
    html = html.replace(block, '', 1)

# ── 2. Add 5 new dark themes before closing };
new_dark_themes = """  dusk: {
    bg: '#4A2860', bgSoft: '#583070', bgDeep: '#321848',
    surface: '#FFF8FF', surfaceMuted: '#F0D8FF',
    ink: '#0E001A', inkSoft: '#5A3080', inkMute: '#A070C0',
    mint: '#E060D0', mintSoft: '#F8D0F0', mintDeep: '#B030A0',
    coral: '#FF6050', coralSoft: '#FFD0C8',
    purple: '#C060F0', yellow: '#F0C030', blue: '#5090F0', pink: '#FF70B0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(40,0,60,0.18), 0 6px 20px rgba(40,0,60,0.28)',
    shadowLift: '0 4px 0 rgba(40,0,60,0.24), 0 12px 32px rgba(40,0,60,0.38)',
    playBg: 'linear-gradient(160deg, #4A2860 0%, #321848 100%)',
    bgOverlay: 'rgba(14, 4, 22, 0.98)',
  },
  copper: {
    bg: '#7A3A10', bgSoft: '#8E4418', bgDeep: '#5A2808',
    surface: '#FFF8F2', surfaceMuted: '#FFE4C8',
    ink: '#1A0800', inkSoft: '#682A08', inkMute: '#B07040',
    mint: '#40C8A0', mintSoft: '#C8F0E4', mintDeep: '#28A880',
    coral: '#FF5030', coralSoft: '#FFD0C0',
    purple: '#8040C0', yellow: '#E0A800', blue: '#2060C0', pink: '#D04080',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(70,24,0,0.15), 0 6px 20px rgba(70,24,0,0.25)',
    shadowLift: '0 4px 0 rgba(70,24,0,0.20), 0 12px 32px rgba(70,24,0,0.35)',
    playBg: 'linear-gradient(160deg, #7A3A10 0%, #5A2808 100%)',
    bgOverlay: 'rgba(28, 8, 0, 0.98)',
  },
  moss: {
    bg: '#2A4020', bgSoft: '#344E28', bgDeep: '#182810',
    surface: '#F4FFF0', surfaceMuted: '#D0ECC8',
    ink: '#060E02', inkSoft: '#285020', inkMute: '#609050',
    mint: '#80D040', mintSoft: '#D8F8B8', mintDeep: '#50A820',
    coral: '#FF5030', coralSoft: '#FFD0C8',
    purple: '#9060D0', yellow: '#D8C010', blue: '#2070D0', pink: '#E04090',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(10,24,4,0.18), 0 6px 20px rgba(10,24,4,0.28)',
    shadowLift: '0 4px 0 rgba(10,24,4,0.24), 0 12px 32px rgba(10,24,4,0.38)',
    playBg: 'linear-gradient(160deg, #2A4020 0%, #182810 100%)',
    bgOverlay: 'rgba(4, 10, 2, 0.98)',
  },
  navy: {
    bg: '#0A1E40', bgSoft: '#102648', bgDeep: '#060E26',
    surface: '#F0F4FF', surfaceMuted: '#C8D4F0',
    ink: '#000814', inkSoft: '#203860', inkMute: '#506080',
    mint: '#40A0F0', mintSoft: '#C0DCF8', mintDeep: '#2070C0',
    coral: '#FF5050', coralSoft: '#FFD0D0',
    purple: '#9060E0', yellow: '#F0C030', blue: '#3080F0', pink: '#F060A0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(0,10,40,0.20), 0 6px 20px rgba(0,10,40,0.32)',
    shadowLift: '0 4px 0 rgba(0,10,40,0.28), 0 12px 32px rgba(0,10,40,0.44)',
    playBg: 'linear-gradient(160deg, #0A1E40 0%, #060E26 100%)',
    bgOverlay: 'rgba(2, 4, 14, 0.99)',
  },
  espresso: {
    bg: '#2C1808', bgSoft: '#381E0C', bgDeep: '#1C0E04',
    surface: '#FFF8F4', surfaceMuted: '#F0DDD0',
    ink: '#0A0200', inkSoft: '#5A3018', inkMute: '#A07050',
    mint: '#D08040', mintSoft: '#F8E4C0', mintDeep: '#A05010',
    coral: '#FF5030', coralSoft: '#FFD0C0',
    purple: '#9050C0', yellow: '#E0B000', blue: '#3070C0', pink: '#D04070',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(20,4,0,0.20), 0 6px 20px rgba(20,4,0,0.32)',
    shadowLift: '0 4px 0 rgba(20,4,0,0.28), 0 12px 32px rgba(20,4,0,0.44)',
    playBg: 'linear-gradient(160deg, #2C1808 0%, #1C0E04 100%)',
    bgOverlay: 'rgba(6, 2, 0, 0.99)',
  },
"""

old_themes_close = "};\n\nlet T = THEMES["
assert old_themes_close in html, "FAIL: themes close"
html = html.replace(old_themes_close, new_dark_themes + "};\n\nlet T = THEMES[", 1)

# ── 3. Update theme picker: existing + separator + 5 new
old_picker = """              <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:8, marginBottom:24 }}>
                {[
                  ['warm','☀️','Meleg'],['dark','🌙','Sötét'],['candy','🍬','Candy'],['lavender','💜','Lavender'],['ocean','🌊','Ocean'],
                  ['peach','🍑','Peach'],['lemon','🍋','Citrom'],['coraltheme','🌺','Coral'],['berry','🫐','Berry'],['ice','🩵','Ice'],
                  ['ember','🔥','Ember'],['midnight','🖤','Midnight'],['crimson','🩸','Crimson'],['forest','🌲','Forest'],['indigo','🔮','Indigo'],
                  ['wine','🍷','Bor'],['slate','🪨','Kő'],['teal','🌊','Teal'],['plum','💜','Szilva'],
                ].map(([key, icon, label]) => (
                  <button key={key} onClick={() => { setTheme && setTheme(key); }} style={{ padding:'10px 4px', borderRadius:14, border: currentTheme===key ? `2px solid ${T.mint}` : `2px solid transparent`, background: currentTheme===key ? T.mintSoft : T.surfaceMuted, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>
                    <span style={{ fontSize:20 }}>{icon}</span>
                    <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color: currentTheme===key ? T.mintDeep : T.inkSoft }}>{label}</span>
                  </button>
                ))}
              </div>"""
assert old_picker in html, "FAIL: theme picker"

new_picker = """              <div style={{ display:'flex', flexDirection:'column', gap:12, marginBottom:24 }}>
                <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:8 }}>
                  {[
                    ['warm','☀️','Meleg'],['dark','🌙','Sötét'],['candy','🍬','Candy'],['lavender','💜','Lavender'],['ocean','🌊','Ocean'],
                    ['peach','🍑','Peach'],['lemon','🍋','Citrom'],['berry','🫐','Berry'],['ice','🩵','Ice'],['slate','🪨','Kő'],
                  ].map(([key, icon, label]) => (
                    <button key={key} onClick={() => { setTheme && setTheme(key); }} style={{ padding:'10px 4px', borderRadius:14, border: currentTheme===key ? `2px solid ${T.mint}` : `2px solid transparent`, background: currentTheme===key ? T.mintSoft : T.surfaceMuted, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>
                      <span style={{ fontSize:20 }}>{icon}</span>
                      <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color: currentTheme===key ? T.mintDeep : T.inkSoft }}>{label}</span>
                    </button>
                  ))}
                </div>
                <div style={{ display:'flex', alignItems:'center', gap:10 }}>
                  <div style={{ flex:1, height:1, background:T.inkMute, opacity:0.3 }} />
                  <span style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkMute, letterSpacing:'0.06em', textTransform:'uppercase' }}>Sötét</span>
                  <div style={{ flex:1, height:1, background:T.inkMute, opacity:0.3 }} />
                </div>
                <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:8 }}>
                  {[
                    ['forest','🌲','Forest'],['dusk','🌆','Dusk'],['copper','🟤','Copper'],['moss','🌿','Moss'],['navy','⚓','Navy'],
                    ['espresso','☕','Espresso'],
                  ].map(([key, icon, label]) => (
                    <button key={key} onClick={() => { setTheme && setTheme(key); }} style={{ padding:'10px 4px', borderRadius:14, border: currentTheme===key ? `2px solid ${T.mint}` : `2px solid transparent`, background: currentTheme===key ? T.mintSoft : T.surfaceMuted, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>
                      <span style={{ fontSize:20 }}>{icon}</span>
                      <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color: currentTheme===key ? T.mintDeep : T.inkSoft }}>{label}</span>
                    </button>
                  ))}
                </div>
              </div>"""

html = html.replace(old_picker, new_picker, 1)

html = html.replace("const APP_VERSION = 'v9.359';", "const APP_VERSION = 'v9.360';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.360 — removed 8 themes, added 5 new dark themes (dusk/copper/moss/navy/espresso), picker has separator")
