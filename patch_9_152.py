#!/usr/bin/env python3
"""patch_9_152.py — Menü: vezérlés magassága mérvadó, állás lista scrollozható"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.151';" in content
content = content.replace("const APP_VERSION = 'v9.151';", "const APP_VERSION = 'v9.152';")

OLD_TAB_WRAPPER = """            {/* Tab contents — fixed height = max(állás,vezérlés) so no jump on switch */}
            {(() => {
              const allasMagassag = mSorted.length * 62 + 28;
              const vezMagassag = 370;
              const tabH = Math.max(allasMagassag, vezMagassag);
              return (
            <div style={{ position:'relative', padding:'0 14px 8px', minHeight: tabH }}>
              {/* ÁLLÁS — always absolute, visible only when active */}
              <div style={{ visibility: menuTab==='állás' ? 'visible' : 'hidden', position:'absolute', top:0, left:14, right:14, display:'flex', flexDirection:'column', gap:10 }}>
                {mSorted.map((p,i) => <LeaderRow key={p.id||i} p={p} rank={i+1} maxScore={mMaxScore} showScores={true} />)}
                <div style={{ height:8 }} />
              </div>

              {/* VEZÉRLÉS — always absolute, visible only when active */}
              <div style={{ visibility: menuTab==='vezérlés' ? 'visible' : 'hidden', position:'absolute', top:0, left:14, right:14, display:'flex', flexDirection:'column', gap:10 }}>"""

NEW_TAB_WRAPPER = """            {/* Tab contents — height = vezérlés content, állás scrolls inside */}
            <div style={{ position:'relative', padding:'0 14px 8px' }}>
              {/* ÁLLÁS — absolute, scrollable, same height as vezérlés */}
              <div style={{ visibility: menuTab==='állás' ? 'visible' : 'hidden', position:'absolute', top:0, left:14, right:14, bottom:0, overflowY:'auto', display:'flex', flexDirection:'column', gap:10 }}>
                {mSorted.map((p,i) => <LeaderRow key={p.id||i} p={p} rank={i+1} maxScore={mMaxScore} showScores={true} />)}
                <div style={{ height:8 }} />
              </div>

              {/* VEZÉRLÉS — relative, determines container height */}
              <div style={{ visibility: menuTab==='vezérlés' ? 'visible' : 'hidden', display:'flex', flexDirection:'column', gap:10 }}>"""

assert OLD_TAB_WRAPPER in content, "tab wrapper not found"
content = content.replace(OLD_TAB_WRAPPER, NEW_TAB_WRAPPER, 1)

OLD_TAB_END = """              </div>{/* end vezérlés */}
            </div>
              ); })()}{/* end tab contents wrapper */}"""

NEW_TAB_END = """              </div>{/* end vezérlés */}
            </div>{/* end tab contents wrapper */}"""

assert OLD_TAB_END in content, "tab end not found"
content = content.replace(OLD_TAB_END, NEW_TAB_END, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.152 ready")
