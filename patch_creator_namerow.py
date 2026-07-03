import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = """          <div style={{ display:'flex', gap:8, overflowX:'auto' }}>
            {profiles.map(p => {
              const sel = creator && creator.id === p.id;
              return (
                <div key={p.id} onClick={() => setCreator(sel ? null : { id: p.id, name: p.name, color: p.color, img: p.img || null })}
                  title={p.name}
                  style={{ width:36, height:36, borderRadius:'50%', flexShrink:0, display:'grid', placeItems:'center', overflow:'hidden', cursor:'pointer', WebkitTapHighlightColor:'transparent', background: p.img ? T.bg : (p.color||'#888'), boxShadow: sel ? `0 0 0 2.5px ${T.bg}, 0 0 0 4.5px ${p.color||T.mint}` : 'none', transition:'box-shadow .15s, opacity .15s', opacity: creator && !sel ? 0.35 : 1 }}>
                  {p.img
                    ? <img src={p.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} />
                    : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff' }}>{(p.name||'?')[0].toUpperCase()}</span>
                  }
                </div>
              );
            })}
          </div>"""

NEW = """          <div style={{ display:'flex', gap:10, overflowX:'auto', paddingBottom:2 }}>
            {profiles.map(p => {
              const sel = creator && creator.id === p.id;
              return (
                <div key={p.id} onClick={() => setCreator(sel ? null : { id: p.id, name: p.name, color: p.color, img: p.img || null })}
                  style={{ width:38, height:38, borderRadius:'50%', flexShrink:0, display:'grid', placeItems:'center', overflow:'hidden', cursor:'pointer', WebkitTapHighlightColor:'transparent', background: p.img ? T.bg : (p.color||'#888'), outline: sel ? `2px solid ${p.color||T.mint}` : '2px solid transparent', outlineOffset:2, transform: sel ? 'scale(1.12)' : 'scale(1)', transition:'transform .15s, outline-color .15s, opacity .15s', opacity: creator && !sel ? 0.35 : 1 }}>
                  {p.img
                    ? <img src={p.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} />
                    : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff' }}>{(p.name||'?')[0].toUpperCase()}</span>
                  }
                </div>
              );
            })}
          </div>
          {creator && (
            <div style={{ marginTop:8, fontFamily:T.font, fontWeight:700, fontSize:13, color: creator.color || T.mint, textAlign:'center' }}>
              {creator.name}
            </div>
          )}"""

assert OLD in content, "OLD not found"
content = content.replace(OLD, NEW, 1)

content = re.sub(r'v9\.716', 'v9.717', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.717")
