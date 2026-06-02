# -*- coding: utf-8 -*-
import base64

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Load banner image as base64
with open('imposztor.png', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('ascii')
banner_data = f"data:image/png;base64,{b64}"

# 2. Add banner to IMGS object (after imposztor_icon entry)
old_imgs = "  'imposztor_icon.png': 'data:image/png;base64,"
# Find the end of that line
idx = html.find(old_imgs)
line_end = html.find('\n', idx)
old_line = html[idx:line_end+1]
new_line = old_line + f"  'imposztor_banner.png': '{banner_data}',\n"
html = html.replace(old_line, new_line, 1)

# 3. Add banner field to imposztor game definition
old_game = "{ id:'imposztor', name:'Imposztor',               difficulty:'közepes', category:'Csapat', emoji:'🕵️', symbol:IMGS['imposztor_symbol.png'], img:IMGS['imposztor_icon.png'], dnr:true,"
new_game = "{ id:'imposztor', name:'Imposztor',               difficulty:'közepes', category:'Csapat', emoji:'🕵️', symbol:IMGS['imposztor_symbol.png'], img:IMGS['imposztor_icon.png'], banner:IMGS['imposztor_banner.png'], dnr:true,"
assert old_game in html, "Game def not found"
html = html.replace(old_game, new_game, 1)

# 4. Update header to use banner image (full width, no split)
old_header = """          {currentGameId === 'imposztor' ? (
            <div style={{ flex:1, height:60, borderRadius:18, overflow:'hidden', display:'flex', background:`${currentGame.color}18`, border:`1.5px solid ${currentGame.color}30` }}>
              <div style={{ width:'50%', height:'100%', overflow:'hidden', flexShrink:0 }}>
                <img src={currentGame.symbol} alt="" style={{ width:'100%', height:'100%', objectFit:'cover', objectPosition:'center top' }} draggable="false" />
              </div>
              <div style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', padding:'0 12px' }}>
                <span style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:currentGame.color, textTransform:'uppercase', letterSpacing:T.letterDisplay, textAlign:'center' }}>{currentGame.name}</span>
              </div>
            </div>"""
new_header = """          {currentGame.banner ? (
            <div style={{ flex:1, height:60, borderRadius:18, overflow:'hidden' }}>
              <img src={currentGame.banner} alt={currentGame.name} style={{ width:'100%', height:'100%', objectFit:'contain', objectPosition:'center' }} draggable="false" />
            </div>"""
assert old_header in html, "Header not found"
html = html.replace(old_header, new_header, 1)

# 5. Version bump
assert 'Verzió 5.53 · DNR · 2026.06.02 13:00' in html, "Version not found"
html = html.replace('Verzió 5.53 · DNR · 2026.06.02 13:00', 'Verzió 5.57 · DNR · 2026.06.02 14:00', 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done — v5.57")
