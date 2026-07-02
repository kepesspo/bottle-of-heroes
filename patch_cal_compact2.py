import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = '''  return (
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

NEW = '''  return (
    <div style={{ flex:1, overflowY:'auto', padding:'6px 6px 24px' }}>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:4 }}>
        <button onClick={() => setCalMonth(new Date(year, month-1, 1))} style={{ width:26, height:26, borderRadius:7, border:'none', background:T.surface, cursor:'pointer', display:'grid', placeItems:'center', boxShadow:T.shadow }}>
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:T.ink }}>{HU_MONTHS[month]} {year}</div>
        <button onClick={() => setCalMonth(new Date(year, month+1, 1))} style={{ width:26, height:26, borderRadius:7, border:'none', background:T.surface, cursor:'pointer', display:'grid', placeItems:'center', boxShadow:T.shadow }}>
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(7,1fr)', marginBottom:1 }}>
        {HU_DAYS.map((d,i) => <div key={i} style={{ textAlign:'center', fontFamily:T.font, fontWeight:700, fontSize:9, color:T.sub, padding:'1px 0' }}>{d}</div>)}
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(7,1fr)', gap:2 }}>'''

assert OLD in content, "OLD not found"
content = content.replace(OLD, NEW, 1)

# Also make the cell font slightly smaller
OLD2 = "                <span style={{ fontFamily:T.font, fontWeight:(isTod||hasEv)?900:400, fontSize:12, color: textColor, lineHeight:1 }}>{d}</span>"
NEW2 = "                <span style={{ fontFamily:T.font, fontWeight:(isTod||hasEv)?900:400, fontSize:11, color: textColor, lineHeight:1 }}>{d}</span>"
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# Tighter list section
OLD3 = "      {monthEvs.length > 0 && (\n        <div style={{ marginTop:12 }}>"
NEW3 = "      {monthEvs.length > 0 && (\n        <div style={{ marginTop:8 }}>"
assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

content = re.sub(r'v9\.697', 'v9.698', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.698")
