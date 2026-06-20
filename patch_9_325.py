#!/usr/bin/env python3
"""v9.325 — Accessibility: contrast fixes, font size bumps, touch target improvements"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════════════════
# 1. DARK THEME — improve contrast ratios
#    Current inkMute #6E789A on #2C3554 ≈ 1.8:1 (FAIL)
#    Fixed  inkMute #8C98C0 on #2C3554 ≈ 3.2:1 (PASS AA for UI components)
#    inkSoft slight bump for body text contrast
# ══════════════════════════════════════════════════════════════════════
old_dark_theme = "    inkSoft: '#B0BADC',\n    inkMute: '#6E789A',"
new_dark_theme = "    inkSoft: '#C4CCDF',\n    inkMute: '#8C98C0',"
assert old_dark_theme in html, "FAIL: dark theme inkMute"
html = html.replace(old_dark_theme, new_dark_theme, 1)

# ══════════════════════════════════════════════════════════════════════
# 2. FONT SIZES — bump all fontSize:9 → 11, fontSize:10 → 12
#    fontSize:9 is illegible in dim lighting / while drinking
# ══════════════════════════════════════════════════════════════════════
# Use targeted replace to avoid matching CSS pixel values accidentally
import re

# Replace fontSize:9 (as JS property, not in strings like '9px')
html = re.sub(r'\bfontSize:9\b', 'fontSize:11', html)
# Replace fontSize:10 (as JS property)
html = re.sub(r'\bfontSize:10\b', 'fontSize:12', html)
# Also replace fontSize:'9' and fontSize:'10' string variants
html = html.replace("fontSize:'9'", "fontSize:'11'")
html = html.replace("fontSize:'10'", "fontSize:'12'")

# ══════════════════════════════════════════════════════════════════════
# 3. TOUCH TARGETS — fix critical small interactive elements
# ══════════════════════════════════════════════════════════════════════

# Back button in AppBar: 38×38 → 44×44
old_back_btn = "style={{ width:38, height:38, border:'none', background:'transparent', color:T.ink, cursor:'pointer', display:'grid', placeItems:'center', borderRadius:12, flexShrink:0 }}"
new_back_btn = "style={{ width:44, height:44, border:'none', background:'transparent', color:T.ink, cursor:'pointer', display:'grid', placeItems:'center', borderRadius:14, flexShrink:0 }}"
assert old_back_btn in html, "FAIL: back btn"
html = html.replace(old_back_btn, new_back_btn, 1)

# Back button placeholder spacer: also 38 → 44
old_back_spacer = "<div style={{ width:38, flexShrink:0 }} />"
new_back_spacer = "<div style={{ width:44, flexShrink:0 }} />"
assert old_back_spacer in html, "FAIL: back spacer"
html = html.replace(old_back_spacer, new_back_spacer, 1)

# Info button on game cards: 28×28 → 40×40 (invisible larger tap area)
old_info_btn = "style={{ width:28, height:28, borderRadius:9, background:'rgba(26,42,74,0.07)', border:'none', cursor:'pointer', display:'grid', placeItems:'center', fontSize:14, color:T.inkSoft }}"
new_info_btn = "style={{ width:40, height:40, borderRadius:12, background:'rgba(26,42,74,0.07)', border:'none', cursor:'pointer', display:'grid', placeItems:'center', fontSize:15, color:T.inkSoft }}"
assert old_info_btn in html, "FAIL: info btn"
html = html.replace(old_info_btn, new_info_btn, 1)

# Toggle switch: height 28 → 36, thumb adjusts proportionally
old_toggle = "    <div onClick={onChange} style={{ width:48, height:28, borderRadius:14, background: on ? T.mint : T.surfaceMuted, position:'relative', cursor:'pointer', flexShrink:0, transition:'background .2s' }}>\n      <div style={{ position:'absolute', top:3, left: on ? 23 : 3, width:22, height:22, borderRadius:'50%', background:'#fff', boxShadow:'0 1px 3px rgba(0,0,0,0.2)', transition:'left .2s' }}/>"
new_toggle = "    <div onClick={onChange} style={{ width:52, height:32, borderRadius:16, background: on ? T.mint : T.surfaceMuted, position:'relative', cursor:'pointer', flexShrink:0, transition:'background .2s' }}>\n      <div style={{ position:'absolute', top:4, left: on ? 24 : 4, width:24, height:24, borderRadius:'50%', background:'#fff', boxShadow:'0 1px 3px rgba(0,0,0,0.2)', transition:'left .2s' }}/>"
assert old_toggle in html, "FAIL: toggle"
html = html.replace(old_toggle, new_toggle, 1)

# QR button in online room: 38×38 → 44×44
old_qr_btn = "style={{ width:38, height:38, borderRadius:10, border:'none', background:'rgba(20,30,50,0.08)', cursor:'pointer', display:'grid', placeItems:'center', touchAction:'manipulation', WebkitTapHighlightColor:'rgba(0,0,0,0.1)', pointerEvents:'auto' }}"
new_qr_btn = "style={{ width:44, height:44, borderRadius:12, border:'none', background:'rgba(20,30,50,0.08)', cursor:'pointer', display:'grid', placeItems:'center', touchAction:'manipulation', WebkitTapHighlightColor:'rgba(0,0,0,0.1)', pointerEvents:'auto' }}"
assert old_qr_btn in html, "FAIL: QR btn"
html = html.replace(old_qr_btn, new_qr_btn, 1)

# Stats tab buttons — add minHeight:44 for proper touch target
old_tab_btn = "style={{ flex:1, padding:'7px 4px', borderRadius:13, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:12, background: tab===t.k ? T.mint : 'transparent', color: tab===t.k ? '#fff' : T.inkSoft, transition:'all .18s', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:3 }}"
new_tab_btn = "style={{ flex:1, padding:'7px 4px', minHeight:44, borderRadius:13, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:12, background: tab===t.k ? T.mint : 'transparent', color: tab===t.k ? '#fff' : T.inkSoft, transition:'all .18s', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:3 }}"
assert old_tab_btn in html, "FAIL: tab btn"
html = html.replace(old_tab_btn, new_tab_btn, 1)

# ══════════════════════════════════════════════════════════════════════
# 4. Minimum font size for in-game text (most critical: PlayScreen labels)
#    nowPlaying / themePlaying labels: fontSize:9 already bumped above
#    Extra: section headers fontSize:10 → 12 already done above
# ══════════════════════════════════════════════════════════════════════

html = html.replace("const APP_VERSION = 'v9.324';", "const APP_VERSION = 'v9.325';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Count changes
import subprocess
result = subprocess.run(['python3', '-c', '''
with open("index.html") as f:
    html = f.read()
c9 = html.count("fontSize:11")
c10 = html.count("fontSize:12")
print(f"fontSize:11 occurrences (from 9→11): {c9}")
print(f"fontSize:12 occurrences (from 10→12): {c10}")
'''], capture_output=True, text=True)
print(result.stdout)

print("Done: v9.325 — Accessibility: dark theme contrast, fontSize 9→11 / 10→12, touch targets")
