import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Make calendar more compact: tighter padding, smaller gap, smaller day headers
OLD = '''  return (
    <div style={{ flex:1, overflowY:'auto', padding:'8px 12px 32px' }}>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:8 }}>
        <button onClick={() => setCalMonth(new Date(year, month-1, 1))} style={{ width:32, height:32, borderRadius:10, border:'none', background:T.surface, cursor:'pointer', display:'grid', placeItems:'center', boxShadow:T.shadow }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{HU_MONTHS[month]} {year}</div>
        <button onClick={() => setCalMonth(new Date(year, month+1, 1))} style={{ width:32, height:32, borderRadius:10, border:'none', background:T.surface, cursor:'pointer', display:'grid', placeItems:'center', boxShadow:T.shadow }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(7,1fr)', marginBottom:2 }}>
        {HU_DAYS.map((d,i) => <div key={i} style={{ textAlign:'center', fontFamily:T.font, fontWeight:700, fontSize:10, color:T.sub, padding:'2px 0' }}>{d}</div>)}
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(7,1fr)', gap:2 }}>'''

NEW = '''  return (
    <div style={{ flex:1, overflowY:'auto', padding:'6px 10px 24px' }}>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:6 }}>
        <button onClick={() => setCalMonth(new Date(year, month-1, 1))} style={{ width:28, height:28, borderRadius:8, border:'none', background:T.surface, cursor:'pointer', display:'grid', placeItems:'center', boxShadow:T.shadow }}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>{HU_MONTHS[month]} {year}</div>
        <button onClick={() => setCalMonth(new Date(year, month+1, 1))} style={{ width:28, height:28, borderRadius:8, border:'none', background:T.surface, cursor:'pointer', display:'grid', placeItems:'center', boxShadow:T.shadow }}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(7,1fr)', marginBottom:1 }}>
        {HU_DAYS.map((d,i) => <div key={i} style={{ textAlign:'center', fontFamily:T.font, fontWeight:700, fontSize:9, color:T.sub, padding:'1px 0' }}>{d}</div>)}
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(7,1fr)', gap:2 }}>'''

assert OLD in content, "OLD not found"
content = content.replace(OLD, NEW, 1)

content = re.sub(r'v9\.695', 'v9.696', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.696")
