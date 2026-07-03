import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove avatar circle from AdminProfiles cards — keep name + hide + delete
OLD1 = '''        <div key={p.id} style={{ display:'flex', alignItems:'center', gap:12, background:T.surface, borderRadius:14, padding:'12px 14px', marginBottom:8, boxShadow:T.shadow }}>
          <div style={{ width:40, height:40, borderRadius:'50%', background:p.color||'#888', flexShrink:0, display:'grid', placeItems:'center', overflow:'hidden' }}>
            {p.img ? <img src={p.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff' }}>{(p.name||'?')[0].toUpperCase()}</span>}
          </div>
          <div style={{ flex:1, minWidth:0 }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{p.name}</div>
            {p.nickname && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub }}>{p.nickname}</div>}
          </div>'''
NEW1 = '''        <div key={p.id} style={{ display:'flex', alignItems:'center', gap:10, background:T.surface, borderRadius:14, padding:'12px 14px', marginBottom:8, boxShadow:T.shadow }}>
          <div style={{ width:12, height:12, borderRadius:'50%', background:p.color||'#888', flexShrink:0 }} />
          <div style={{ flex:1, minWidth:0 }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{p.name}</div>
            {p.nickname && <div style={{ fontFamily:T.font, fontSize:12, color:T.sub }}>{p.nickname}</div>}
          </div>'''
assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# Version bump
content = re.sub(r'v9\.704', 'v9.705', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.705")
