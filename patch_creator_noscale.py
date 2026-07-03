import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = "style={{ width:38, height:38, borderRadius:'50%', flexShrink:0, display:'grid', placeItems:'center', overflow:'hidden', cursor:'pointer', WebkitTapHighlightColor:'transparent', background: p.img ? T.bg : (p.color||'#888'), outline: sel ? `2px solid ${p.color||T.mint}` : '2px solid transparent', outlineOffset:2, transform: sel ? 'scale(1.12)' : 'scale(1)', transition:'transform .15s, outline-color .15s, opacity .15s', opacity: creator && !sel ? 0.35 : 1 }}>"
NEW = "style={{ width:38, height:38, borderRadius:'50%', flexShrink:0, display:'grid', placeItems:'center', overflow:'hidden', cursor:'pointer', WebkitTapHighlightColor:'transparent', background: p.img ? T.bg : (p.color||'#888'), outline: sel ? `2.5px solid ${p.color||T.mint}` : '2.5px solid transparent', outlineOffset:3, transition:'outline-color .15s, opacity .15s', opacity: creator && !sel ? 0.35 : 1 }}>"
assert OLD in content, "OLD not found"
content = content.replace(OLD, NEW, 1)

# Also add paddingBottom+paddingTop to the row so outline doesn't clip
OLD2 = "          <div style={{ display:'flex', gap:10, overflowX:'auto', paddingBottom:2 }}>"
NEW2 = "          <div style={{ display:'flex', gap:10, overflowX:'auto', paddingBottom:8, paddingTop:4 }}>"
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

content = re.sub(r'v9\.718', 'v9.719', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.719")
