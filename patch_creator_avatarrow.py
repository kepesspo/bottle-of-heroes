import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = """      {/* Létrehozó */}
      {profiles.length > 0 && (
        <div style={card}>
          {label('Létrehozó')}
          <div style={{ display:'flex', flexWrap:'wrap', gap:8 }}>
            {profiles.map(p => {
              const sel = creator && creator.id === p.id;
              return (
                <div key={p.id} onClick={() => setCreator(sel ? null : { id: p.id, name: p.name, color: p.color, img: p.img || null })}
                  style={{ display:'flex', alignItems:'center', gap:8, padding:'8px 12px', borderRadius:12, background: sel ? (p.color || T.mint) + '22' : T.bg, border:`2px solid ${sel ? (p.color || T.mint) : 'transparent'}`, cursor:'pointer', transition:'all .15s', WebkitTapHighlightColor:'transparent' }}>
                  <div style={{ width:28, height:28, borderRadius:'50%', background: p.color || '#888', flexShrink:0, display:'grid', placeItems:'center', overflow:'hidden' }}>
                    {p.img ? <img src={p.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff' }}>{(p.name||'?')[0].toUpperCase()}</span>}
                  </div>
                  <span style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color: sel ? (p.color || T.mint) : T.ink }}>{p.name}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}"""

NEW = """      {/* Létrehozó */}
      {profiles.length > 0 && (
        <div style={card}>
          {label('Létrehozó')}
          <div style={{ display:'flex', gap:12, overflowX:'auto', paddingBottom:2 }}>
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
          </div>
        </div>
      )}"""

assert OLD in content, "OLD not found"
content = content.replace(OLD, NEW, 1)

content = re.sub(r'v9\.714', 'v9.715', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.715")
