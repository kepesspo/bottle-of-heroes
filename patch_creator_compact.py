import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = """          <div style={{ display:'flex', gap:12, overflowX:'auto', paddingBottom:2 }}>
            {profiles.map(p => {
              const sel = creator && creator.id === p.id;
              return (
                <div key={p.id} onClick={() => setCreator(sel ? null : { id: p.id, name: p.name, color: p.color, img: p.img || null })}
                  style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:5, cursor:'pointer', flexShrink:0, WebkitTapHighlightColor:'transparent' }}>
                  <div style={{ width:52, height:52, borderRadius:'50%', background: p.img ? T.bg : (p.color||'#888'), display:'grid', placeItems:'center', overflow:'hidden', border:`3px solid ${sel ? (p.color||T.mint) : 'transparent'}`, boxSizing:'border-box', transition:'border-color .15s', boxShadow: sel ? `0 0 0 2px ${T.bg}, 0 0 0 4px ${p.color||T.mint}` : 'none' }}>
                    {p.img
                      ? <img src={p.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} />
                      : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:'#fff' }}>{(p.name||'?')[0].toUpperCase()}</span>
                    }
                  </div>
                  <span style={{ fontFamily:T.font, fontWeight: sel ? 900 : 600, fontSize:11, color: sel ? (p.color||T.mint) : T.sub, maxWidth:52, textAlign:'center', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</span>
                </div>
              );
            })}
          </div>"""

NEW = """          <div style={{ display:'flex', gap:8, overflowX:'auto' }}>
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

assert OLD in content, "OLD not found"
content = content.replace(OLD, NEW, 1)

content = re.sub(r'v9\.715', 'v9.716', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.716")
