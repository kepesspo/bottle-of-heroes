#!/usr/bin/env python3
"""v9.346 — Add bgOverlay per theme: dark but same hue, smooth status bar transition"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add bgOverlay to each theme — dark version of the theme's hue
replacements = [
    ("playBg: 'linear-gradient(160deg, #F4C57E 0%, #EDAF58 100%)',\n  },\n  dark: {",
     "playBg: 'linear-gradient(160deg, #F4C57E 0%, #EDAF58 100%)',\n    bgOverlay: 'rgba(75, 42, 5, 0.96)',\n  },\n  dark: {"),

    ("playBg: 'linear-gradient(160deg, #2C3554 0%, #1A2040 100%)',\n  },\n  candy: {",
     "playBg: 'linear-gradient(160deg, #2C3554 0%, #1A2040 100%)',\n    bgOverlay: 'rgba(10, 14, 28, 0.97)',\n  },\n  candy: {"),

    ("playBg: 'linear-gradient(160deg, #FFE8F4 0%, #FFD0EC 100%)',\n  },\n  lavender: {",
     "playBg: 'linear-gradient(160deg, #FFE8F4 0%, #FFD0EC 100%)',\n    bgOverlay: 'rgba(95, 12, 60, 0.96)',\n  },\n  lavender: {"),

    ("playBg: 'linear-gradient(160deg, #EEE8FF 0%, #DDD0FF 100%)',\n  },\n  ocean: {",
     "playBg: 'linear-gradient(160deg, #EEE8FF 0%, #DDD0FF 100%)',\n    bgOverlay: 'rgba(32, 12, 88, 0.96)',\n  },\n  ocean: {"),

    ("playBg: 'linear-gradient(160deg, #E0F4F8 0%, #C0E8F4 100%)',\n  },\n  peach: {",
     "playBg: 'linear-gradient(160deg, #E0F4F8 0%, #C0E8F4 100%)',\n    bgOverlay: 'rgba(6, 42, 62, 0.96)',\n  },\n  peach: {"),

    ("playBg: 'linear-gradient(160deg, #FFE8D8 0%, #FFD0BC 100%)',\n  },\n  lemon: {",
     "playBg: 'linear-gradient(160deg, #FFE8D8 0%, #FFD0BC 100%)',\n    bgOverlay: 'rgba(88, 32, 6, 0.96)',\n  },\n  lemon: {"),

    ("playBg: 'linear-gradient(160deg, #F8F8D8 0%, #ECECA8 100%)',\n  },\n  coraltheme: {",
     "playBg: 'linear-gradient(160deg, #F8F8D8 0%, #ECECA8 100%)',\n    bgOverlay: 'rgba(52, 52, 6, 0.96)',\n  },\n  coraltheme: {"),

    ("playBg: 'linear-gradient(160deg, #FFE8E0 0%, #FFCCC0 100%)',\n  },\n  berry: {",
     "playBg: 'linear-gradient(160deg, #FFE8E0 0%, #FFCCC0 100%)',\n    bgOverlay: 'rgba(105, 22, 12, 0.96)',\n  },\n  berry: {"),

    ("playBg: 'linear-gradient(160deg, #F0E8F8 0%, #DDD0F0 100%)',\n  },\n  ice: {",
     "playBg: 'linear-gradient(160deg, #F0E8F8 0%, #DDD0F0 100%)',\n    bgOverlay: 'rgba(50, 6, 85, 0.96)',\n  },\n  ice: {"),

    ("playBg: 'linear-gradient(160deg, #E8F4FF 0%, #D0E8FF 100%)',\n  },\n};",
     "playBg: 'linear-gradient(160deg, #E8F4FF 0%, #D0E8FF 100%)',\n    bgOverlay: 'rgba(6, 22, 72, 0.96)',\n  },\n};"),
]

for old, new in replacements:
    assert old in html, f"FAIL: {old[:40]}"
    html = html.replace(old, new, 1)

# Update overlays to use T.bgOverlay
old_onboard_bg = "background:`linear-gradient(to bottom, ${T.bg} 0%, rgba(14,14,24,0.92) 90px)`"
new_onboard_bg = "background:`linear-gradient(to bottom, ${T.bg} 0%, ${T.bgOverlay} 90px)`"
assert old_onboard_bg in html, "FAIL: onboarding bg"
html = html.replace(old_onboard_bg, new_onboard_bg, 1)

old_round_bg = "background:`linear-gradient(to bottom, ${T.bg} 0%, rgba(14,14,24,0.92) 90px)`"
new_round_bg = "background:`linear-gradient(to bottom, ${T.bg} 0%, ${T.bgOverlay} 90px)`"
assert old_round_bg in html, "FAIL: round bg"
html = html.replace(old_round_bg, new_round_bg, 1)

html = html.replace("const APP_VERSION = 'v9.345';", "const APP_VERSION = 'v9.346';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.346 — themed overlay bgOverlay per theme, smooth status bar transition")
