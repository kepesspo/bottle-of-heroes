with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = """      {/* Tab switcher */}
      <div style={{ padding:'10px 16px 0' }}>
        <div style={{ display:'flex', background:T.surface, borderRadius:18, padding:4, boxShadow:T.shadow, overflowX:'auto' }}>
          {TABS.map(([k,label]) => (
            <button key={k} onClick={() => setTab(k)} style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', padding:'10px 0', borderRadius:14, border:'none', fontFamily:T.font, fontWeight:900, fontSize:12, cursor:'pointer', background: tab===k ? T.mint : 'transparent', color: tab===k ? '#fff' : T.inkSoft, transition:'all .2s', WebkitTapHighlightColor:'transparent' }}>
              {label}
            </button>
          ))}
        </div>
      </div>"""

NEW = """      {/* Tab switcher — scrollable */}
      <div style={{ padding:'10px 16px 0' }}>
        <div style={{ display:'flex', background:T.surface, borderRadius:18, padding:4, boxShadow:T.shadow, overflowX:'auto', WebkitOverflowScrolling:'touch', scrollbarWidth:'none' }}>
          {TABS.map(([k,label]) => (
            <button key={k} onClick={() => setTab(k)} style={{ flexShrink:0, display:'flex', alignItems:'center', justifyContent:'center', padding:'10px 16px', borderRadius:14, border:'none', fontFamily:T.font, fontWeight:900, fontSize:13, cursor:'pointer', background: tab===k ? T.mint : 'transparent', color: tab===k ? '#fff' : T.inkSoft, transition:'all .2s', WebkitTapHighlightColor:'transparent', whiteSpace:'nowrap' }}>
              {label}
            </button>
          ))}
        </div>
      </div>"""

assert OLD in content, "OLD not found"
content = content.replace(OLD, NEW, 1)

import re
content = re.sub(r'v9\.720', 'v9.721', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.721")
