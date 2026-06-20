#!/usr/bin/env python3
"""v9.362 — Re-add slate (Kő) theme"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add slate theme before closing };
slate_theme = """  slate: {
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
"""

old_close = "};\n\nlet T = THEMES["
assert old_close in html, "FAIL: themes close"
html = html.replace(old_close, slate_theme + "};\n\nlet T = THEMES[", 1)

# Add slate to the top grid in picker (after ice)
old_top_row = "['warm','☀️','Meleg'],['dark','🌙','Sötét'],['candy','🍬','Candy'],['lavender','💜','Lavender'],['ocean','🌊','Ocean'],\n                    ['peach','🍑','Peach'],['lemon','🍋','Citrom'],['berry','🫐','Berry'],['ice','🩵','Ice'],"
new_top_row = "['warm','☀️','Meleg'],['dark','🌙','Sötét'],['candy','🍬','Candy'],['lavender','💜','Lavender'],['ocean','🌊','Ocean'],\n                    ['peach','🍑','Peach'],['lemon','🍋','Citrom'],['berry','🫐','Berry'],['ice','🩵','Ice'],['slate','🪨','Kő'],"
assert old_top_row in html, "FAIL: picker top row"
html = html.replace(old_top_row, new_top_row, 1)

html = html.replace("const APP_VERSION = 'v9.361';", "const APP_VERSION = 'v9.362';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.362 — slate (Kő) theme restored")
