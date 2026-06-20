#!/usr/bin/env python3
"""v9.361 — Remove all new dark themes, add green options"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove: forest, slate, dusk, copper, moss, navy, espresso
to_remove_keys = ['forest', 'slate', 'dusk', 'copper', 'moss', 'navy', 'espresso']

for key in to_remove_keys:
    # Find the theme block by key
    start_marker = f'  {key}: {{\n'
    assert start_marker in html, f"FAIL: cant find theme {key}"
    start = html.index(start_marker)
    # Find end: next theme or closing };
    end = html.index('\n  },\n', start) + len('\n  },\n')
    html = html[:start] + html[end:]

# Add green themes before closing };
new_greens = """  jade: {
    bg: '#B8E8C8', bgSoft: '#CCF0DA', bgDeep: '#98D8AC',
    surface: '#FFFFFF', surfaceMuted: '#E4F8EC',
    ink: '#082818', inkSoft: '#286840', inkMute: '#70A880',
    mint: '#20A060', mintSoft: '#C0EDD4', mintDeep: '#108040',
    coral: '#E06050', coralSoft: '#FFE0DC',
    purple: '#8050C0', yellow: '#C0A010', blue: '#3080C0', pink: '#D05090',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(0,60,24,0.06), 0 6px 20px rgba(0,60,24,0.10)',
    shadowLift: '0 4px 0 rgba(0,60,24,0.08), 0 12px 32px rgba(0,60,24,0.14)',
    playBg: 'linear-gradient(160deg, #B8E8C8 0%, #98D8AC 100%)',
    bgOverlay: 'rgba(6, 38, 18, 0.96)',
  },
  mint2: {
    bg: '#C8F0E0', bgSoft: '#D8F8EC', bgDeep: '#A8E0CC',
    surface: '#FFFFFF', surfaceMuted: '#E8FBF2',
    ink: '#062018', inkSoft: '#205840', inkMute: '#60A080',
    mint: '#10B880', mintSoft: '#B8F0D8', mintDeep: '#089060',
    coral: '#E05050', coralSoft: '#FFE0E0',
    purple: '#7050C0', yellow: '#B8A010', blue: '#3090C0', pink: '#D04080',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(0,70,40,0.06), 0 6px 20px rgba(0,70,40,0.10)',
    shadowLift: '0 4px 0 rgba(0,70,40,0.08), 0 12px 32px rgba(0,70,40,0.14)',
    playBg: 'linear-gradient(160deg, #C8F0E0 0%, #A8E0CC 100%)',
    bgOverlay: 'rgba(4, 32, 20, 0.96)',
  },
  lime: {
    bg: '#D8F0A0', bgSoft: '#E4F8B8', bgDeep: '#C0E080',
    surface: '#FFFFFF', surfaceMuted: '#F0FBD8',
    ink: '#182800', inkSoft: '#486010', inkMute: '#88A840',
    mint: '#60A000', mintSoft: '#DCF0A0', mintDeep: '#408000',
    coral: '#E05030', coralSoft: '#FFE0D8',
    purple: '#7850C0', yellow: '#A89000', blue: '#3080B0', pink: '#D04080',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(40,60,0,0.06), 0 6px 20px rgba(40,60,0,0.10)',
    shadowLift: '0 4px 0 rgba(40,60,0,0.08), 0 12px 32px rgba(40,60,0,0.14)',
    playBg: 'linear-gradient(160deg, #D8F0A0 0%, #C0E080 100%)',
    bgOverlay: 'rgba(22, 38, 0, 0.96)',
  },
"""

old_close = "};\n\nlet T = THEMES["
assert old_close in html, "FAIL: themes close"
html = html.replace(old_close, new_greens + "};\n\nlet T = THEMES[", 1)

# Update picker
old_picker = """              <div style={{ display:'flex', flexDirection:'column', gap:12, marginBottom:24 }}>
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
assert old_picker in html, "FAIL: theme picker"

new_picker = """              <div style={{ display:'flex', flexDirection:'column', gap:12, marginBottom:24 }}>
                <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:8 }}>
                  {[
                    ['warm','☀️','Meleg'],['dark','🌙','Sötét'],['candy','🍬','Candy'],['lavender','💜','Lavender'],['ocean','🌊','Ocean'],
                    ['peach','🍑','Peach'],['lemon','🍋','Citrom'],['berry','🫐','Berry'],['ice','🩵','Ice'],
                  ].map(([key, icon, label]) => (
                    <button key={key} onClick={() => { setTheme && setTheme(key); }} style={{ padding:'10px 4px', borderRadius:14, border: currentTheme===key ? `2px solid ${T.mint}` : `2px solid transparent`, background: currentTheme===key ? T.mintSoft : T.surfaceMuted, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>
                      <span style={{ fontSize:20 }}>{icon}</span>
                      <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color: currentTheme===key ? T.mintDeep : T.inkSoft }}>{label}</span>
                    </button>
                  ))}
                </div>
                <div style={{ display:'flex', alignItems:'center', gap:10 }}>
                  <div style={{ flex:1, height:1, background:T.inkMute, opacity:0.3 }} />
                  <span style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkMute, letterSpacing:'0.06em', textTransform:'uppercase' }}>Zöld</span>
                  <div style={{ flex:1, height:1, background:T.inkMute, opacity:0.3 }} />
                </div>
                <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:8 }}>
                  {[
                    ['jade','🪴','Jade'],['mint2','🌿','Menta'],['lime','🍃','Lime'],
                  ].map(([key, icon, label]) => (
                    <button key={key} onClick={() => { setTheme && setTheme(key); }} style={{ padding:'10px 4px', borderRadius:14, border: currentTheme===key ? `2px solid ${T.mint}` : `2px solid transparent`, background: currentTheme===key ? T.mintSoft : T.surfaceMuted, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>
                      <span style={{ fontSize:20 }}>{icon}</span>
                      <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color: currentTheme===key ? T.mintDeep : T.inkSoft }}>{label}</span>
                    </button>
                  ))}
                </div>
              </div>"""

html = html.replace(old_picker, new_picker, 1)

html = html.replace("const APP_VERSION = 'v9.360';", "const APP_VERSION = 'v9.361';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.361 — removed dark themes, added 3 green options (jade/mint/lime)")
