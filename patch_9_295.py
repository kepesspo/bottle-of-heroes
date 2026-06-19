#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. PlayScreen menü — fade a tab contents wrapper aljára (mind a 3 tabet fedi)
old1 = """            </div>{/* end tab contents wrapper */}"""
new1 = """              <div style={{ position:'absolute', bottom:0, left:0, right:0, height:56, background:`linear-gradient(to bottom, transparent, ${T.surface})`, pointerEvents:'none', zIndex:3 }} />
            </div>{/* end tab contents wrapper */}"""
assert old1 in html, "FAIL: tab contents wrapper"
html = html.replace(old1, new1, 1)

# ── 2. EndScreen — fade a scroll wrapper szülőjébe
import re
end_pos = html.find("function EndScreen(")
search = html[end_pos:end_pos+500]
old2 = """      <div style={{ flex:1, minHeight:0, position:'relative' }}>
        <div style={{ height:'100%', overflowY:'auto', WebkitOverflowScrolling:'touch' }}>"""
new2 = """      <div style={{ flex:1, minHeight:0, position:'relative' }}>
        <div style={{ position:'absolute', bottom:0, left:0, right:0, height:80, background:`linear-gradient(to bottom, transparent, ${T.bg})`, pointerEvents:'none', zIndex:2 }} />
        <div style={{ height:'100%', overflowY:'auto', WebkitOverflowScrolling:'touch' }}>"""
idx2 = html.find(old2, end_pos)
assert idx2 != -1, "FAIL: EndScreen scroll wrapper"
html = html[:idx2] + new2 + html[idx2+len(old2):]

# ── 3. StatsScreen — fade a scroll wrapper szülőjébe
stats_pos = html.find("function StatsScreen(")
old3 = """      <div style={{ flex:1, overflowY:'auto', padding:'12px 16px 40px' }}>"""
new3 = """      <div style={{ flex:1, position:'relative' }}>
        <div style={{ position:'absolute', bottom:0, left:0, right:0, height:80, background:`linear-gradient(to bottom, transparent, ${T.bg})`, pointerEvents:'none', zIndex:2 }} />
        <div style={{ height:'100%', overflowY:'auto', padding:'12px 16px 40px' }}>"""
idx3 = html.find(old3, stats_pos)
assert idx3 != -1, "FAIL: StatsScreen scroll"
html = html[:idx3] + new3 + html[idx3+len(old3):]
# Close the extra wrapper div — find the matching closing after this content block
# The StatsScreen ends with </div> </div> pattern, we need one more closing div
old3_close = """      </div>
    </div>
  );
}

function HomeScreen"""
new3_close = """      </div>
      </div>{/* StatsScreen scroll wrapper */}
    </div>
  );
}

function HomeScreen"""
assert old3_close in html, "FAIL: StatsScreen close"
html = html.replace(old3_close, new3_close, 1)

html = html.replace("const APP_VERSION = 'v9.294';", "const APP_VERSION = 'v9.295';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.295 — scroll fade: PlayScreen menü, EndScreen, StatsScreen")
