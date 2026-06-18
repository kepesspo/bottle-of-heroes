#!/usr/bin/env python3
"""patch_9_154.py — Állás tab: ne nyomja össze a sorokat"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.153';" in content
content = content.replace("const APP_VERSION = 'v9.153';", "const APP_VERSION = 'v9.154';")

# Az állás div flex+bottom:0 kombináció összenyomja a sorokat.
# Megoldás: a scrollozó div ne legyen flex, a tartalom egy belső div-ben legyen.

OLD_ALLAS = """              {/* ÁLLÁS — absolute, scrollable, same height as vezérlés */}
              <div style={{ visibility: menuTab==='állás' ? 'visible' : 'hidden', position:'absolute', top:0, left:14, right:14, bottom:0, overflowY:'auto', display:'flex', flexDirection:'column', gap:10 }}>
                {mSorted.map((p,i) => <LeaderRow key={p.id||i} p={p} rank={i+1} maxScore={mMaxScore} showScores={true} />)}
                <div style={{ height:8 }} />
              </div>"""

NEW_ALLAS = """              {/* ÁLLÁS — absolute, scrollable, same height as vezérlés */}
              <div style={{ visibility: menuTab==='állás' ? 'visible' : 'hidden', position:'absolute', top:0, left:14, right:14, bottom:0, overflowY:'auto' }}>
                <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
                  {mSorted.map((p,i) => <LeaderRow key={p.id||i} p={p} rank={i+1} maxScore={mMaxScore} showScores={true} />)}
                  <div style={{ height:8 }} />
                </div>
              </div>"""

assert OLD_ALLAS in content, "állás div not found"
content = content.replace(OLD_ALLAS, NEW_ALLAS, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.154 ready")
