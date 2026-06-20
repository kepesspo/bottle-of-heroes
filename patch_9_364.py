#!/usr/bin/env python3
"""v9.364 — Remove mint2, merge all themes into single grid"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove mint2 theme
key = 'mint2'
start_marker = f'  {key}: {{\n'
assert start_marker in html, f"FAIL: cant find theme {key}"
start = html.index(start_marker)
end = html.index('\n  },\n', start) + len('\n  },\n')
html = html[:start] + html[end:]

# Replace the split picker (two grids + separator) with a single grid
old_picker = """              <div style={{ display:'flex', flexDirection:'column', gap:12, marginBottom:24 }}>
                <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:8 }}>
                  {[
                    ['warm','☀️','Meleg'],['dark','🌙','Sötét'],['peach','🍑','Peach'],['lemon','🍋','Citrom'],['berry','🫐','Berry'],
                    ['ice','🩵','Ice'],['slate','🪨','Kő'],
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
                    ['jade','🪴','Jade'],['mint2','🌿','Menta'],
                  ].map(([key, icon, label]) => (
                    <button key={key} onClick={() => { setTheme && setTheme(key); }} style={{ padding:'10px 4px', borderRadius:14, border: currentTheme===key ? `2px solid ${T.mint}` : `2px solid transparent`, background: currentTheme===key ? T.mintSoft : T.surfaceMuted, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>
                      <span style={{ fontSize:20 }}>{icon}</span>
                      <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color: currentTheme===key ? T.mintDeep : T.inkSoft }}>{label}</span>
                    </button>
                  ))}
                </div>
              </div>"""
assert old_picker in html, "FAIL: picker"

new_picker = """              <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:8, marginBottom:24 }}>
                {[
                  ['warm','☀️','Meleg'],['dark','🌙','Sötét'],['peach','🍑','Peach'],['lemon','🍋','Citrom'],['berry','🫐','Berry'],
                  ['ice','🩵','Ice'],['slate','🪨','Kő'],['jade','🪴','Jade'],
                ].map(([key, icon, label]) => (
                  <button key={key} onClick={() => { setTheme && setTheme(key); }} style={{ padding:'10px 4px', borderRadius:14, border: currentTheme===key ? `2px solid ${T.mint}` : `2px solid transparent`, background: currentTheme===key ? T.mintSoft : T.surfaceMuted, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>
                    <span style={{ fontSize:20 }}>{icon}</span>
                    <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color: currentTheme===key ? T.mintDeep : T.inkSoft }}>{label}</span>
                  </button>
                ))}
              </div>"""

html = html.replace(old_picker, new_picker, 1)

html = html.replace("const APP_VERSION = 'v9.363';", "const APP_VERSION = 'v9.364';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.364 — removed mint2, merged into single 8-theme grid")
