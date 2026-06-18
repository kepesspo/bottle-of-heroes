#!/usr/bin/env python3
"""patch_9_151.py — Menü: egyforma magasság az Állás és Vezérlés tabok között"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.150';" in content
content = content.replace("const APP_VERSION = 'v9.150';", "const APP_VERSION = 'v9.151';")

# A megközelítés:
# - Mindkét tab mindig position:absolute (egyik sem befolyásolja a konténer magasságát)
# - A konténernek explicit magassága van: max(állás_height, vezérlés_height)
# - vezérlés magassága ~370px fix (leader+szobakód+input+gombok+kilépés)
# - állás magassága: players.length * 62 + 20
# - Így váltáskor nem ugrik semmi

OLD_TAB_WRAPPER = """            {/* Tab contents — same wrapper so height stays stable */}
            <div style={{ position:'relative', padding:'0 14px 8px' }}>
              {/* ÁLLÁS — always rendered for stable height; hidden when not active */}
              <div style={{ visibility: menuTab==='állás' ? 'visible' : 'hidden', position: menuTab==='állás' ? 'relative' : 'absolute', top:0, left:0, right:0, display:'flex', flexDirection:'column', gap:10 }}>
                {mSorted.map((p,i) => <LeaderRow key={p.id||i} p={p} rank={i+1} maxScore={mMaxScore} showScores={true} />)}
                <div style={{ height:8 }} />
              </div>

              {/* VEZÉRLÉS — always rendered; hidden when not active */}
              <div style={{ visibility: menuTab==='vezérlés' ? 'visible' : 'hidden', position: menuTab==='vezérlés' ? 'relative' : 'absolute', top:0, left:0, right:0, display:'flex', flexDirection:'column', gap:10 }}>"""

NEW_TAB_WRAPPER = """            {/* Tab contents — fixed height = max(állás,vezérlés) so no jump on switch */}
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

assert OLD_TAB_WRAPPER in content, "tab wrapper not found"
content = content.replace(OLD_TAB_WRAPPER, NEW_TAB_WRAPPER, 1)

# Close the IIFE after the end of the tab contents wrapper
OLD_TAB_END = """              </div>{/* end vezérlés */}
            </div>{/* end tab contents wrapper */}"""

NEW_TAB_END = """              </div>{/* end vezérlés */}
            </div>
              ); })()}{/* end tab contents wrapper */}"""

assert OLD_TAB_END in content, "tab end not found"
content = content.replace(OLD_TAB_END, NEW_TAB_END, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.151 ready")
