#!/usr/bin/env python3
"""v9.359 — Add 10 darker bold themes alongside existing 10"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_themes_end = """  ice: {
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

new_themes_end = """  ice: {
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
  ember: {
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
  midnight: {
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
  crimson: {
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
  forest: {
    bg: '#0A4828', bgSoft: '#0E5830', bgDeep: '#063018',
    surface: '#F0FFF6', surfaceMuted: '#C8F0D8',
    ink: '#001A0A', inkSoft: '#185830', inkMute: '#50A070',
    mint: '#30D878', mintSoft: '#B8F0D0', mintDeep: '#18A050',
    coral: '#FF5030', coralSoft: '#FFD0C8',
    purple: '#8050D0', yellow: '#D0C000', blue: '#2060D0', pink: '#E04080',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(0,30,12,0.18), 0 6px 20px rgba(0,30,12,0.28)',
    shadowLift: '0 4px 0 rgba(0,30,12,0.24), 0 12px 32px rgba(0,30,12,0.38)',
    playBg: 'linear-gradient(160deg, #0A4828 0%, #063018 100%)',
    bgOverlay: 'rgba(2, 14, 6, 0.98)',
  },
  indigo: {
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
  wine: {
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
  slate: {
    bg: '#1E2A38', bgSoft: '#263444', bgDeep: '#121C28',
    surface: '#2E3E50', surfaceMuted: '#263444',
    ink: '#E0EAF4', inkSoft: '#8AA0B8', inkMute: '#4A6078',
    mint: '#40C8A0', mintSoft: '#103028', mintDeep: '#30A880',
    coral: '#FF6050', coralSoft: '#301412',
    purple: '#A080E0', yellow: '#F0C040', blue: '#60A8F0', pink: '#F060A0',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(0,0,0,0.25), 0 6px 20px rgba(0,0,0,0.35)',
    shadowLift: '0 4px 0 rgba(0,0,0,0.32), 0 12px 32px rgba(0,0,0,0.45)',
    playBg: 'linear-gradient(160deg, #1E2A38 0%, #121C28 100%)',
    bgOverlay: 'rgba(4, 8, 14, 0.99)',
  },
  teal: {
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
  plum: {
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
};"""

assert old_themes_end in html, "FAIL: themes end"
html = html.replace(old_themes_end, new_themes_end, 1)

# Update theme picker to show all 20 themes, 5-column grid, 4 rows
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

new_picker = """              <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:8, marginBottom:24 }}>
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

html = html.replace(old_picker, new_picker, 1)

html = html.replace("const APP_VERSION = 'v9.358';", "const APP_VERSION = 'v9.359';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.359 — 10 new dark bold themes added (ember/midnight/crimson/forest/indigo/wine/slate/teal/plum + existing 10)")
